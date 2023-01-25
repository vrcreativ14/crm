from json.encoder import JSONEncoder
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields.array import ArrayField
from django.forms.models import model_to_dict
from django.views.generic.base import View
from core import email, models
from core.mixins import AuditTrailMixin
from re import T
from django.core.exceptions import ValidationError
from accounts.models import Company
import io

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from django.utils.html import escape
from django.views.generic import DetailView

from core.pdf import PDF
from core.utils import clean_and_validate_email_addresses
from core.email import EmailSendingException

from healthinsurance.models.deal import Deal, ProcessEmail
from healthinsurance.constants import *
from healthinsurance.utils import deal_stages_to_number, get_email_type
from felix.sms import SMSService
from felix.message import WhatsappService
from django.template.loader import get_template
from django.template.loader import render_to_string
from core.email.health_insurance_email import SendHealthInsuranceEmail
from healthinsurance.models.quote import Quote
from mortgage.constants import *
from core.email.constants import MORTGAGE_EMAIL_SUBJECTS
from felix.settings import DOMAIN
from django.template import Template
from django.shortcuts import get_object_or_404


class HandleEmailContent(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.list_health_deals'
    model = Deal    
    available_email_templates = [
        'latest',  # if this is provided, will check the deal's stage and return the email template accordingly
        'new_deal',
        'quote',
        'quote_updated',
        'documents',
        'final_quote',
        'payment',
        'payment_confirmation',
        'policy_issuance',
        'housekeeping',
        'closed',
        'basic',
        'renewal_deal_single_quote',
        'renewal_deal_multiple_quotes',
        'renewal_basic',
    ]

    @classmethod
    def _get_from_email_for_deal(cls, deal):
        if deal.user and deal.user.first_name:
            return f'{deal.user.first_name} at Nexus Insurance Brokers - ind.medical@nexusadvice.com'
        else:
            return f'Nexus Insurance Brokers - ind.medical@nexusadvice.com'

    @classmethod
    def _get_reply_to_for_deal(cls, deal):
        reply_to_name = 'Nexus Insurance Brokers'
        reply_to_address = 'ind.medical@nexusadvice.com'

        return f'{reply_to_name} - {reply_to_address}'

    @classmethod
    def _get_cc_mails_for_deal(cls, deal):
        if deal.referrer and deal.referrer.first_name:
            return f'{deal.user.first_name} at Nexus Insurance Brokers - ind.medical@nexusadvice.com'
        else:
            return f'Nexus Insurance Brokers - ind.medical@nexusadvice.com'

    def dispatch(self, *args, **kwargs):
        email_type = kwargs['type']
        deal_id = kwargs['pk']
        quote = Quote.objects.filter(deal_id = deal_id)
        if quote.exists():
            quote = quote[0]
        if email_type == 'latest':
            deal = self.get_object()
            if deal.stage == STAGE_NEW:
                kwargs['type'] = 'new_deal'
            elif deal.stage == STAGE_QUOTE:
                kwargs['type'] = 'quote_updated' if quote else 'quote'
            elif deal.stage == STAGE_DOCUMENTS:
                #kwargs['type'] = 'documents'
                kwargs['type'] = 'quote_updated' if quote else 'quote'
            elif deal.stage == STAGE_FINAL_QUOTE:
                kwargs['type'] = 'final_quote'
            elif deal.stage == STAGE_PAYMENT:
                kwargs['type'] = 'payment'
            elif deal.stage == STAGE_POLICY_ISSUANCE:
                kwargs['type'] = 'policy_issuance'
            elif deal.stage == STAGE_HOUSE_KEEPING or deal.stage == STAGE_WON:
                kwargs['type'] = 'policy_issuance'
            elif deal.stage == STAGE_BASIC:
                kwargs['type'] = 'basic'            

        return super().dispatch(*args, **kwargs)

    def _validate_fields(self):
        errors = {}

        to = self.request.POST.get('email')
        # cc_emails = self.request.POST['cc_emails']
        # bcc_emails = self.request.POST['bcc_emails']

        if to and not clean_and_validate_email_addresses(to):
            errors['email'] = 'Invalid format for email address(es).'

        # if cc_emails and not clean_and_validate_email_addresses(cc_emails):
        #     errors['cc_emails'] = 'Invalid format for email address(es).'

        # if bcc_emails and not clean_and_validate_email_addresses(bcc_emails):
        #     errors['bcc_emails'] = 'Invalid format for email address(es).'

        return errors

    def _get_allowed_templates(self):
        deal = self.get_object()
        deal_stage = deal_stages_to_number(deal.stage)
        
        allowed_templates = {'new_deal': 'New Deal'}
        if deal_stage >= 2:
            allowed_templates['quote'] = 'Quote'
            allowed_templates['quote_updated'] = 'Quote Updated'
            if deal and deal.deal_type == DEAL_TYPE_RENEWAL:
                allowed_templates['renewal_deal_single_quote'] = 'Renewal Deal Single Quote'
                allowed_templates['renewal_deal_multiple_quotes'] = 'Renewal Deal Multiple Quotes'
        if deal.stage == 'basic':
            allowed_templates['basic'] = 'Basic'
            if deal and deal.deal_type == DEAL_TYPE_RENEWAL:
                allowed_templates['renewal_basic'] = 'Renewal Basic'
            return allowed_templates
        if deal_stage >= 4:
            allowed_templates['final_quote'] = 'Final Quote'

        if deal_stage >= 5 and deal.current_sub_stage and deal.current_sub_stage.sub_stage == PAYMENT_CONFIRMATION:
            allowed_templates['payment'] = 'Payment'

        if deal_stage >= 6:
            allowed_templates['policy_issuance'] = 'Policy Issuance'

        if deal_stage >= 7:
            allowed_templates['housekeeping'] = 'Housekeeping'
        
        return allowed_templates

    def GetEmailContent(self, **kwargs):
        email_type = kwargs.get('email_type')
        deal = kwargs.get('deal')
        quote = kwargs.get('quote')
        emailer = SendHealthInsuranceEmail(Company.objects.last())
    
        quote = Quote.objects.filter(deal = deal)
        quote = quote[0] if quote.exists() else None
    
        if email_type == 'new_deal' or email_type == 'new' or email_type == 'new deal':
            setattr(deal, 'company', Company.objects.last())
            message = emailer.prepare_email_content_for_new_deal(deal)
    
        elif email_type == 'quote' or email_type == 'quote_updated':
            updated = email_type == 'quote_updated'
            message = emailer.prepare_email_content_for_quote(deal,quote, updated)

        elif email_type == 'order_confirmation':
            message = emailer.prepare_email_content_for_order_summary(deal)

        elif email_type == 'final_quote':
            message = emailer.prepare_email_content_for_final_quote(deal, quote)
            sms_content = ''
            
        elif email_type == 'final_quote_submitted':
            message = emailer.prepare_email_content_for_final_quote_submitted(deal)            

        elif email_type == 'payment':
            message = emailer.prepare_email_content_for_payment(deal, quote)
            sms_content = ''
            

        elif email_type == 'payment_confirmation':  #proof of payment shared
            message = emailer.prepare_email_content_for_payment_confirmation(deal)
            sms_content = ''
            

        elif email_type == 'policy_issuance':
            message = emailer.prepare_email_content_for_policy_issuance(deal, quote)
            sms_content = ''
            

        elif email_type == 'basic_plan_selected':
            message = emailer.prepare_email_content(deal, 'basic_plan_selected')
            
    
        return message
    
    def post(self, request, *args, **kwargs):
        deal = self.get_object()
        company = 'Nexus Insurance Brokers'
        email_type = kwargs['type']
        emailer = SendHealthInsuranceEmail(company)
        from_email = self._get_from_email_for_deal(deal)
        reply_to = self._get_reply_to_for_deal(deal)
        to = request.POST.get('email')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        cc_emails = request.POST['cc_emails']
        bcc_emails = request.POST['bcc_emails']
        sms_content = request.POST.get('sms_content')
        wa_msg_content = request.POST.get('wa_msg_content')
        attachments = []
        for file in request.FILES:
            attachments.append((request.FILES[file].name, request.FILES.get(file)))
        if not subject or not content:
            message = self.GetEmailContent(email_type = email_type,deal=deal)
            subject = message.get('subject')
            content = message.get('email_content')
        if not to:
            to = deal.primary_member.email if deal and deal.primary_member else ''
        validation_errors = self._validate_fields()

        

        if len(validation_errors):
            return JsonResponse({'success': False, 'errors': validation_errors})

        # if email_type == 'order_confirmation':
        #     order = deal.get_order()
        #     if order:
        #         source = order.get_pdf_url()
        #         pdf = PDF().get_pdf_content(source)
        #         file = io.BytesIO(pdf)
        #         attachments = [('order-summary.pdf', file)]

        cleaned_to = clean_and_validate_email_addresses(to)
        try:
            emailer.send_general_email(
                cleaned_to, subject, content, from_email,
                cc_emails=clean_and_validate_email_addresses(cc_emails),
                bcc_emails=clean_and_validate_email_addresses(bcc_emails),
                reply_to=reply_to,
                attachments=attachments
            )
            success = True

            # if (email_type == 'new_quote' or email_type == 'quote_updated') and not deal.quote_sent:
            #     deal.quote_sent = True
            #     deal.save(user=request.user)

            # if email_type == 'final_quote':
            #     current_stage = deal.stage
            #     current_sub_stage = 

            audit_trail = deal.get_audit_trail()

            process_email = ProcessEmail.objects.create(
                from_address=from_email,
                to_address=cleaned_to,
                subject=subject,
                text=content,
                html=content,
                deal = deal,
                cc_addresses=[],
                # cc_addresses = ArrayField(base_field=models.EmailField()),
                bcc_addresses=[],
                # bcc_addresses = ArrayField(base_field=models.EmailField()),
            )
            process_email.deal = deal
            process_email.save()
            # process_email.attachments.set(attachments) if attachments else ...
            for a in attachments:
                process_email.attachments.set(a[1].file) if a[1].file else ...
    
            audit_trail.save()
            audit_trail.record_generic_history(
                'email',
                f'Email sent to: {cleaned_to} | Subject: {subject} emailpk {process_email.pk}',
                self.request.user if self.request else ''
            )
            audit_trail.save()

        except EmailSendingException as e:
            print(e)
            success = False

        if bool(request.POST.get('send_sms', None)) and deal.primary_member.phone and sms_content:
            sms = SMSService()
            sms.send_sms(
                deal.primary_member.phone,
                sms_content
            )

        if bool(request.POST.get('send_wa_msg', None)) and deal.primary_member.phone and wa_msg_content:
            wa = WhatsappService()
            wa.send_whatsapp_msg(
                deal.primary_member.phone,
                wa_msg_content,
                app_name = 'health-insurance'
            )

        return JsonResponse({'success': success, 'email_type': email_type})

    def get(self, request, *args, **kwargs):
        deal = self.get_object()
        quote = Quote.objects.filter(deal = deal)
        quote = quote[0] if quote.exists() else None
        order = deal.get_order()
        policy = deal.get_policy()
        subject = ''
        content = ''
        sms_content = None
        wa_msg_content = None
        email_type = kwargs['type']
        updated = 'updated' in request.GET
        documents = []
        company = 'Nexus Insurance Brokers'
        # workspace_settings = company.workspacemotorsettings
        emailer = SendHealthInsuranceEmail(Company.objects.last())

        if email_type not in self.available_email_templates:
            return JsonResponse({'errors': 'Not a valid email type provided.'})

        if email_type == 'new_deal' or email_type == 'new':
            setattr(deal, 'company', Company.objects.last())
            message = emailer.prepare_email_content_for_new_deal(deal)
            subject = message.get('subject')
            content = message.get('email_content')
            wa_msg_content = message.get('wa_msg_content') 
            sms_content = f'Thank you for requesting health-insurance quotes from. ' \
                          f'We\'re preparing some options for you and will send you an email soon!'
            if not wa_msg_content:
                wa_msg_content = sms_content

        elif email_type == 'quote' or email_type == 'quote_updated':
            updated = email_type == 'quote_updated'
            message = emailer.prepare_email_content_for_quote(deal,quote, updated)
            subject = message.get('subject')
            content = message.get('email_content')
            wa_msg_content = message.get('wa_msg_content')
            quote_url = f"{DOMAIN}/health-insurance-quote/{quote.reference_number}/{deal.pk}/"
            sms_content = 'Hi {}, your health-insurance quotes are ready'.format(deal.customer.name)
            if not wa_msg_content:
                wa_msg_content = 'Hi {},\nWe\'ve updated your health-insurance quote. Click here to check them out:\n{}\n' \
                                    'If the link doesn’t work, simply reply to this message, and try the link again.\n'  \
                                    'Thanks,\n' \
                                    'Nexus Insurance Brokers'.format(deal.customer.name, quote_url)
            if updated:
                sms_content = 'Hi {}, we\'ve updated your quote. Click here to check them out:\n{}'.format(
                    deal.customer.name, quote_url
                )

        elif email_type == 'renewal_deal_multiple_quotes' or email_type == 'renewal_deal_single_quote' or email_type == 'renewal_basic':
            type = email_type.replace('_', ' ')
            message = emailer.prepare_email_content_for_renewal_deal(deal, type)
            subject = message.get('subject')
            content = message.get('email_content')
            wa_msg_content = message.get('wa_msg_content')
            if quote:
                quote_url = f"{DOMAIN}/health-insurance-quote/{quote.reference_number}/{deal.pk}/"
            sms_content = 'Hi {}, your health-insurance quotes are ready'.format(deal.customer.name)
            if not wa_msg_content:
                wa_msg_content = 'Hi {},\nWe\'ve updated your health-insurance quote. Click here to check them out:\n{}\n' \
                                'If the link doesn’t work, simply reply to this message, and try the link again.\n'  \
                                'Thanks,\n' \
                                'Nexus Insurance Brokers'.format(deal.customer.name, quote_url)
            if updated:
                sms_content = 'Hi {}, we\'ve updated your quote. Click here to check them out:\n{}'.format(
                    deal.customer.name, quote_url
                )


        elif email_type == 'documents':
            message = emailer.prepare_email_content_for_documents(deal)
            subject = message.get('subject')
            content = message.get('email_content')
            wa_msg_content = message.get('wa_msg_content')
            sms_content = 'Hi {}, your health-insurance documents is ready'.format(deal.customer.name)
            

        elif email_type == 'final_quote':
            message = emailer.prepare_email_content_for_final_quote(deal, quote)
            subject = message.get('subject')
            content = message.get('email_content')
            wa_msg_content = message.get('wa_msg_content')
            sms_content = ''
            
        
        elif email_type == 'payment':
            message = emailer.prepare_email_content_for_payment(deal, quote)
            subject = message.get('subject')
            content = message.get('email_content')
            wa_msg_content = message.get('wa_msg_content')
            sms_content = 'Hi {}, The details for the method of Payment are ready.'.format(deal.customer.name)
            
        
        elif email_type == 'payment_confirmation':
            message = emailer.prepare_email_content_for_payment_confirmation(deal, quote)
            subject = message.get('subject')
            content = message.get('email_content')
            wa_msg_content = message.get('wa_msg_content')
            sms_content = ''
            

        elif email_type == 'policy_issuance':
            message = emailer.prepare_email_content_for_policy_issuance(deal, quote)
            subject = message.get('subject')
            content = message.get('email_content')
            wa_msg_content = message.get('wa_msg_content')
            sms_content = 'Hi {}, your health insurance policy is ready.'.format(deal.customer.name)
            

        elif email_type == 'housekeeping':
            message = emailer.prepare_email_content_for_housekeeping(deal)
            subject = message.get('subject')
            content = message.get('email_content')
            wa_msg_content = message.get('wa_msg_content')            

        elif email_type == 'closed':
            message = emailer.prepare_email_content_for_deal_won(deal)
            subject = message.get('subject')
            content = message.get('email_content')
            wa_msg_content = message.get('wa_msg_content')
            sms_content = ''

        else:
            message = emailer.prepare_email_content(deal, 'basic')
            subject = message.get('subject')
            content = message.get('email_content')
            wa_msg_content = message.get('wa_msg_content')

        bcc_emails = list()
        cc_emails = list()
        if deal.user and deal.user.email:
            bcc_emails.append(deal.user.email)
        if deal.primary_member and deal.primary_member.visa == EMIRATE_ABU_DHABI:
            bcc_emails.append('auhpls.hotline@nexusadvice.com')
        else:
            bcc_emails.append('ind.medical@nexusadvice.com')

        if deal.referrer and deal.referrer.email:
            cc_emails.append(deal.referrer.email)
        # if deal.bcc_emails:
        #     bcc_emails.append("deal.bcc_emails")

        # checking workspace_settings and userprofile if we can send copy of all emails
        # to company and user (deal assigned to) email addresses.
        # if workspace_settings.bcc_all_emails and workspace_settings.email:
        #     bcc_emails.append(workspace_settings.email)
        # if deal.assigned_to and deal.assigned_to.email:
        #     bcc_emails.append(deal.assigned_to.email)
        # if deal.producer and deal.producer.email:
        #     bcc_emails.append(deal.producer.email)

        if len(bcc_emails):
            bcc_emails = ', '.join(
                set(sorted(bcc_emails, key=lambda v: v, reverse=True)))

        from_email = escape(self._get_from_email_for_deal(deal))
        reply_to = escape(self._get_reply_to_for_deal(deal))

        return JsonResponse({
            'from': from_email,
            'reply_to': reply_to,
            'to': deal.primary_member.email,
            'cc_emails': cc_emails,
            'bcc_emails': bcc_emails,
            'subject': subject,
            'content': content,
            'sms_content': sms_content,
            'whatsapp_msg_content': wa_msg_content,
            'attachments': [{
                'name': document[0],
                'url': document[1].url
            } for document in documents],

            'allowed_templates': self._get_allowed_templates(),
            'email_type': email_type,
            'stage': deal.stage,
        }, safe=False)


class StageEmailNotification(AuditTrailMixin):

    def __init__(self, deal, email_type, recipient, attachments=[], cc_addresses=[], bcc_addresses=[],  request=None):
        company = Company.objects.last()
        self.emailer = SendHealthInsuranceEmail(company)
        self.deal = deal
        self.email_type = email_type
        self.request = request
        self.context = {"customer_name": deal.customer.name if hasattr(deal, "customer") else ''}
        self.send_email = False
        self.cc_addresses = cc_addresses
        self.bcc_addresses = bcc_addresses
        if not deal.customer.email:
            raise ValidationError("Email is required")

        self.to_email = recipient if recipient else deal.customer.email
        self.attachments = attachments
        self.user = deal.user if deal.user else None

    def GetEmailContent(self, **kwargs):
        email_type = self.email_type
        deal = self.deal
        quote = kwargs.get('quote')
        emailer = SendHealthInsuranceEmail(Company.objects.last())
    
        quote = deal.get_quote()
    
        if email_type == 'new_deal' or email_type == 'new' or email_type == 'new deal' or email_type == 'basic new deal':
            setattr(deal, 'company', Company.objects.last())
            message = emailer.prepare_email_content_for_new_deal(deal)
            subject = message.get('subject')
            content = message.get('email_content')
    
        elif email_type == 'quote' or email_type == 'quote_updated':
            updated = email_type == 'quote_updated'
            message = emailer.prepare_email_content_for_quote(deal,quote, updated)
            subject = message.get('subject')
            content = message.get('email_content')

        elif email_type == 'order_confirmation' or email_type == 'order confirmation team notification':
            message = emailer.prepare_email_content_for_order_summary(deal, email_type)
            subject = message.get('subject')
            content = message.get('email_content')

        elif email_type == 'final_quote':
            message = emailer.prepare_email_content_for_final_quote(deal)
            subject = message.get('subject')
            content = message.get('email_content')
        
        elif email_type == 'final_quote_submitted':
            message = emailer.prepare_email_content_for_final_quote_submitted(deal)
            subject = message.get('subject')
            content = message.get('email_content')

        elif email_type == 'payment':
            message = emailer.prepare_email_content_for_payment(deal, quote)
            subject = message.get('subject')
            content = message.get('email_content')

        elif email_type == 'payment_confirmation':  #proof of payment shared
            message = emailer.prepare_email_content_for_payment_confirmation(deal)
            subject = message.get('subject')
            content = message.get('email_content')
            

        elif email_type == 'policy_issuance':
            message = emailer.prepare_email_content_for_policy_issuance(deal, quote)
            subject = message.get('subject')
            content = message.get('email_content')
        else:
            message = emailer.prepare_email_content(deal, email_type)
            subject = message.get('subject')
            content = message.get('email_content')
        
        return subject, content

    def stage_propagation_email(self, stage=True):
        if not self.send_email:
            ...
        from_email = HandleEmailContent._get_from_email_for_deal(self.deal)
        reply_to = HandleEmailContent._get_reply_to_for_deal(self.deal)
        cleaned_to = clean_and_validate_email_addresses(self.to_email)
        subject, content = self.GetEmailContent()
        cc_addresses = self.cc_addresses
        bcc_addresses = self.bcc_addresses
        cc_emails = list()
        bcc_emails = list()
        try:
            if len(cc_addresses):
                cc_emails = ', '.join(
                set(sorted(cc_addresses, key=lambda v: v, reverse=True)))
                
            if len(bcc_addresses):
                bcc_emails = ', '.join(
                set(sorted(bcc_addresses, key=lambda v: v, reverse=True)))

            if cc_emails and bcc_emails:
                self.emailer.send_general_email(
                    self.to_email, subject, content, from_email,
                    cc_emails=clean_and_validate_email_addresses(cc_emails),
                    bcc_emails=clean_and_validate_email_addresses(bcc_emails),
                    reply_to=reply_to,
                    attachments=self.attachments
                )
            else:
                self.emailer.send_general_email(
                    self.to_email, subject, content, from_email,
                    # bcc_emails=clean_and_validate_email_addresses(bcc_emails),
                    reply_to=reply_to,
                    attachments=self.attachments
                )

            success = True

            # if (email_type == 'new_quote' or email_type == 'quote_updated') and not deal.quote_sent:
            #     deal.quote_sent = True
            #     deal.save(user=request.user)

            # if email_type == 'final_quote':
            #     current_stage = deal.stage
            #     current_sub_stage = 

            audit_trail = self.deal.get_audit_trail()

            process_email = ProcessEmail.objects.create(
                from_address=from_email,
                to_address=cleaned_to,
                subject=subject,
                text=content,
                html=content,
                deal = self.deal,
                cc_addresses=cc_addresses,
                # cc_addresses = ArrayField(base_field=models.EmailField()),
                bcc_addresses=[],
                # bcc_addresses = ArrayField(base_field=models.EmailField()),
            )
            process_email.deal = self.deal
            process_email.save()
            process_email.attachments.set(self.attachments) if self.attachments else ...
            audit_trail.save()
            audit_trail.record_generic_history(
                'email',
                f'Email sent to: {cleaned_to} | Subject: {subject} emailpk {process_email.pk}',
                self.user if self.user else ''
            )
            audit_trail.save()
            return True

        except EmailSendingException as e:
            print(e)
            return False

    def prepare_email(self):
        self.rendered = render_to_string(self.template, self.context)
        self.from_email = HandleEmailContent._get_from_email_for_deal(self.deal)
        self.reply_to = HandleEmailContent._get_reply_to_for_deal(self.deal)
        self.email_content = {
            "from_address": self.from_email,
            "to_address": self.to_email,
            "subject": self.subject,
            "text": '',
            "attachments": self.attachments,
            "html": self.rendered,
            "cc_addresses": [],
            "bcc_addresses": self.bcc_addresses}

    def send_again(self, post_data):
        ...


class ProcessedEmailView(View):
    def get(self, request, *args, **kwargs):
        data = {}
        email = ProcessEmail.objects.get(pk=kwargs.get('pk'))
        data.update(**model_to_dict(email))
        data['from'] = email.from_address
        data['reply_to'] = HandleEmailContent._get_reply_to_for_deal(email.deal)
        data['stages'] = {x : y for x, y in DEAL_STAGES}
        data['current_stage'] = email.deal.stage
        return JsonResponse({"success": True, "content": data})
    
    def post(self, request, *args, **kwargs):
        post_data = request.POST.dict()
        post_data.pop('csrfmiddlewaretoken', None)
        stage_email = StageEmailNotification(request=request, deal=ProcessEmail.objects.get(pk=kwargs.get('pk')).deal)
        stage_email.send_again(post_data)
        return JsonResponse({"success": True, "message": "ok"})
