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

from mortgage.models import Deal, ProcessEmail
from mortgage.constants import *
from felix.sms import SMSService
from felix.message import WhatsappService
from django.template.loader import get_template
from django.template.loader import render_to_string
from core.email.mortgage_email import MortgageSendEmail
from mortgage.constants import *
from core.email.constants import MORTGAGE_EMAIL_SUBJECTS
from felix.settings import DOMAIN
from mortgage.models import ProcessEmail


class MortgageHandleEmailContent(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.list_motor_deals'
    model = Deal

    available_email_templates = [
        'latest',  # if this is provided, will check the deal's stage and return the email template accordingly
        'new_deal',
        'new_quote',
        'quote_updated',
        'pre_approval',
        'new_valuation',
        'valuation_updated',
        'final_offer',
        'settlement',
        'loan_disbursal',
        'property_transfer'
    ]

    @classmethod
    def _get_from_email_for_deal(cls, deal):
        if deal.referrer and deal.referrer.first_name:
            return f'{deal.referrer.first_name} at Nexus Mortgage Brokers - quotes@nexusmb.com'
        else:
            return f'Nexus Mortgage Brokers - quotes@nexusmb.com'

    @classmethod
    def _get_reply_to_for_deal(cls, deal):
        reply_to_name = 'Nexus Mortgage Brokers'
        reply_to_address = 'quotes@nexusmb.com'

        return f'{reply_to_name} - {reply_to_address}'

    def dispatch(self, *args, **kwargs):
        email_type = kwargs['type']

        if email_type == 'latest':
            deal = self.get_object()

            if deal.stage == STAGE_NEW:
                kwargs['type'] = 'new_deal'
            elif deal.stage == STAGE_QUOTE:
                kwargs['type'] = 'quote_updated' if deal.get_quote else 'new_quote'
            elif deal.stage == STAGE_PREAPPROVAL:
                kwargs['type'] = 'pre_approval'
            elif deal.stage == STAGE_VALUATION:
                kwargs['type'] = 'new_valuation'
            elif deal.stage == STAGE_FINAL_OFFER:
                kwargs['type'] = 'final_offer'
            elif deal.stage == STAGE_SETTLEMENT:
                kwargs['type'] = 'settlement'
            elif deal.stage == STAGE_LOAN_DISBURSAL:
                kwargs['type'] = 'loan_disbursal'
            elif deal.stage == STAGE_PROPERTY_TRANSFER:
                kwargs['type'] = 'property_transfer'

        return super().dispatch(*args, **kwargs)

    def _validate_fields(self):
        errors = {}

        to = self.request.POST['email']
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

        allowed_templates = {
            'new_deal': 'New Deal',
            'new_quote': 'Quote',
            'pre_approval': 'Pre Approval',
            'new_valuation': 'Valuation',
            # 'valuation_updated': 'Valuation Update',
            'final_offer': 'Final Offer',
            'settlement': 'Settlement',
            'loan_disbursal': 'Loan Disbursal',
            'property_transfer': 'Property Transfer'
        }

        # if deal.stage in [STAGE_QUOTE, STAGE_FINAL_OFFER, STAGE_VALUATION, STAGE_ClosedWON, STAGE_ClosedLOST]:
        #     allowed_templates['new_quote'] = 'New Quote'
        #     allowed_templates['pre_approval'] = 'Pre Approval'
        #     allowed_templates['new_valuation'] = 'New Valuation'
        #     allowed_templates['valuation_updated'] = 'Valuation Update'
        #     allowed_templates['final_offer'] = 'Final Offer'
        #     allowed_templates['settlement'] = 'Settlement'
        #     allowed_templates['loan_disbursal'] = 'Loan Disbursal'
        #     allowed_templates['property_transfer'] = 'Property Transfer'

        return allowed_templates

    def post(self, request, *args, **kwargs):
        deal = self.get_object()
        company = 'Nexus Mortgage Brokers'
        email_type = kwargs['type']

        emailer = MortgageSendEmail(company)

        from_email = self._get_from_email_for_deal(deal)
        reply_to = self._get_reply_to_for_deal(deal)

        to = request.POST['email']
        subject = request.POST['subject']
        content = request.POST['content']
        # cc_emails = request.POST['cc_emails']
        # bcc_emails = request.POST['bcc_emails']
        sms_content = request.POST['sms_content']
        wa_msg_content = request.POST['wa_msg_content']
        attachments = None

        validation_errors = self._validate_fields()

        if len(validation_errors):
            return JsonResponse({'success': False, 'errors': validation_errors})

        if email_type == 'order_confirmation':
            order = deal.get_order()

            if order:
                source = order.get_pdf_url()
                pdf = PDF().get_pdf_content(source)
                file = io.BytesIO(pdf)
                attachments = [('order-summary.pdf', file)]

        cleaned_to = clean_and_validate_email_addresses(to)
        try:
            emailer.send_general_email(
                cleaned_to, subject, content, from_email,
                # cc_emails=clean_and_validate_email_addresses(cc_emails),
                # bcc_emails=clean_and_validate_email_addresses(bcc_emails),
                reply_to=reply_to,
                attachments=attachments
            )
            success = True

            if (email_type == 'new_quote' or email_type == 'quote_updated') and not deal.quote_sent:
                deal.quote_sent = True
                deal.save(user=request.user)

            audit_trail = deal.get_audit_trail()

            process_email = ProcessEmail(
                from_address=from_email,
                to_address=cleaned_to,
                subject=subject,
                text=content,
                html=content,
                cc_addresses=[],
                # cc_addresses = ArrayField(base_field=models.EmailField()),
                bcc_addresses=[],
                # bcc_addresses = ArrayField(base_field=models.EmailField()),
            )
            process_email.deal = deal
            process_email.save()
            process_email.attachments.set(attachments) if attachments else ...
            audit_trail.save()
            audit_trail.record_generic_history(
                'email',
                f'Email sent to: {cleaned_to} | Subject: {subject} emailpk {process_email.pk}',
                self.request.user if self.request else ''
            )
            audit_trail.save()

        except EmailSendingException:
            success = False

        if request.POST.get('send_sms', None) and deal.customer.phone and sms_content:
            sms = SMSService()
            sms.send_sms(
                deal.customer.phone,
                sms_content
            )

        if request.POST.get('send_wa_msg', None) and deal.customer.phone and wa_msg_content:
                wa = WhatsappService()
                wa.send_whatsapp_msg(
                    deal.customer.phone,
                    wa_msg_content,
                    app_name = 'mortgage'
                )

        return JsonResponse({'success': success, 'email_type': email_type})

    def get(self, request, *args, **kwargs):
        deal = self.get_object()

        subject = ''
        content = ''
        sms_content = None
        wa_msg_content = None
        email_type = kwargs['type']
        updated = 'updated' in request.GET
        documents = []

        company = 'Nexus Mortgage Brokers'
        # workspace_settings = company.workspacemotorsettings

        emailer = MortgageSendEmail(Company.objects.last())

        if email_type not in self.available_email_templates:
            return JsonResponse({'errors': 'Not a valid email type provided.'})

        if email_type == 'new_deal':
            setattr(deal, 'company', Company.objects.last())
            subject, content = emailer.prepare_email_content_for_new_deal(deal)
            sms_content = f'Thank you for requesting mortgage quotes from Nexus Mortgage Brokers. ' \
                          f'We\'re preparing some options for you and will send you an email soon!'
            wa_msg_content = sms_content

        elif email_type == 'new_quote' or email_type == 'quote_updated':
            updated = email_type == 'quote_updated'
            subject, content = emailer.prepare_email_content_for_quote(deal, updated)

            sms_content = 'Hi {}, your mortgage quotes are ready'.format(deal.referrer)
            wa_msg_content = sms_content
            if updated:
                quote_url = f"{DOMAIN}/mortgage-quote/{deal.mortgage_quote_deals.reference_number}/{deal.pk}/"
                sms_content = 'Hi {}, we\'ve updated your quote. Click here to check them out:'.format(
                    deal.referrer, quote_url
                )
                wa_msg_content = 'Hi {},\nWe\'ve updated your mortgage quote. Click here to check them out:\n{}\n' \
                                'If the link doesn’t work, simply reply to this message, and try the link again.\n'  \
                                'Thanks,\n' \
                                'Nexus Mortgage Brokers'.format(deal.referrer, quote_url)

        elif email_type == 'pre_approval':
            subject, content = emailer.prepare_email_content_for_pre_approval(deal)

            sms_content = 'Hi {}, your mortgage pre approval is ready'.format(deal.referrer)
            wa_msg_content = 'Dear {},\n' \
                            'Congrats! You have been pre-approved.\n' \
                            'We have sent you an email, please check to find out more.\n' \
                            'Thanks,\n' \
                            'Nexus Mortgage Brokers'.format(deal.referrer)

        elif email_type == 'new_valuation':
            subject, content = emailer.prepare_email_content_for_valuation(deal)

            sms_content = 'Hi {}, your mortgage valuation is ready.'.format(deal.referrer)
            wa_msg_content = 'Dear {},\n' \
                            'The valuation process has been initiated and we will have the report within few days.\n' \
                            'Thanks,\n' \
                            'Nexus Mortgage Brokers'.format(deal.referrer)
        
        elif email_type == 'final_offer':
            subject, content = emailer.prepare_email_content_for_final_offer(deal)

            sms_content = 'Hi {}, your mortgage offer is ready.'.format(deal.referrer)
            wa_msg_content = 'Dear {},\n' \
                             'Your Final Offer Letter is in process and meanwhile we can proceed with the bank account opening.\n' \
                            'For that you can visit a branch with copy of your salary certificate, or you can get in touch with us so we can help you out.\n' \
                            'Thanks,\n' \
                            'Nexus Mortgage Brokers'.format(deal.referrer)

        elif email_type == 'settlement':
            subject, content = emailer.prepare_email_content_for_settlement(deal)

            sms_content = 'Hi {}, your mortgage settlement is ready.'.format(deal.referrer)
            wa_msg_content = 'Dear {},\n' \
                            'Thanks for meeting the bank.\n' \
                            'We will now request the seller to apply for his mortgage Liability Letter and once ready we will proceed with the settlement.\n' \
                            'Thanks,\n' \
                            'Nexus Mortgage Brokers'.format(deal.referrer)

        elif email_type == 'loan_disbursal':
            subject, content = emailer.prepare_email_content_for_loan_disbursal(deal)

            sms_content = 'Hi {}, your mortgage loan disbursal is ready.'.format(deal.referrer)
            wa_msg_content = 'Dear {},\n' \
                            'We inform you that seller mortgage settlement is completed, and we will now wait for the bank to release the original property documents.\n' \
                            'Thanks,\n' \
                            'Nexus Mortgage Brokers'.format(deal.referrer)

        elif email_type == 'property_transfer':
            subject, content = emailer.prepare_email_content_for_property_transfer(deal)
            wa_msg_content = 'Dear {},\n' \
                             'Property documents are received, and we will now book the trustee office for the property transfer.\n' \
                             'Thanks,\n' \
                             'Nexus Mortgage Brokers'.format(deal.referrer)

            sms_content = 'Hi {}, your mortgage property transfer is ready.'.format(deal.referrer)

        bcc_emails = list()

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
            'to': deal.customer.email,
            # 'cc_emails': deal.cc_emails,
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


class StageEmail(AuditTrailMixin):

    def __init__(self, deal, attachments=[], bcc_addresses=[],  request=None):
        company = Company.objects.last()
        self.emailer = MortgageSendEmail(company)
        self.deal = deal
        stage = deal.stage
        self.request = request
        self.context = {"customer_name": deal.customer.name if hasattr(deal, "customer") else ''}
        self.send_email = False

        if hasattr(deal, "mortgage_quote_deals"):
            deal.mortgage_quote_deals.is_sent = True
            deal.mortgage_quote_deals.save()

        if stage == STAGE_NEW:
            self.context = {"customer_name": deal.customer.name if hasattr(deal.customer) else ''}
            self.template = "email/mortgage_lead_received.html"
            self.subject = MORTGAGE_EMAIL_SUBJECTS.get("NEW_DEAL")

        elif stage == STAGE_QUOTE:
            self.template = "email/mortgage_quote_generated.html"
            self.subject = MORTGAGE_EMAIL_SUBJECTS.get("QUOTE_NEW")
            # host = "http://127.0.0.1:8000"
            self.context['quote_url'] = f"{DOMAIN}/mortgage-quote/{deal.pk}/"

        elif stage == STAGE_PREAPPROVAL:
            self.template = "email/mortgage_pre_approval.html"
            self.subject = MORTGAGE_EMAIL_SUBJECTS.get("PRE_APPROVAL")
            # host = "http://127.0.0.1:8000"
            self.context['quote_url'] = f"{DOMAIN}/mortgage-quote/{deal.pk}/"

        elif stage == STAGE_VALUATION:
            self.template = "email/mortgage_valuation_generated.html"
            self.subject = MORTGAGE_EMAIL_SUBJECTS.get("VALUATION_NEW")
            self.context['key'] = "value"

        elif stage == STAGE_FINAL_OFFER:
            self.subject = MORTGAGE_EMAIL_SUBJECTS.get("OFFER")
            self.template = "email/mortgage_offer_generated.html"
            self.context['key'] = "value"

        elif stage == STAGE_SETTLEMENT:
            self.subject = MORTGAGE_EMAIL_SUBJECTS.get("SETTLEMENT")
            self.template = "email/mortgage_settlement_generated.html"
            self.context['key'] = "value"

        elif stage == STAGE_LOAN_DISBURSAL:
            self.subject = MORTGAGE_EMAIL_SUBJECTS.get("LOAN_DISBURSAL")
            self.template = "email/mortgage_loan_disbursal.html"
            self.context['key'] = "value"

        elif stage == STAGE_PROPERTY_TRANSFER:
            self.subject = MORTGAGE_EMAIL_SUBJECTS.get("PROPERTY_TRANSFER")
            self.template = "email/mortgage_property_transfer.html"
            self.context['key'] = "value"

        elif stage == STAGE_ClosedWON:
            # self.subject = MORTGAGE_EMAIL_SUBJECTS.get("NEW_DEAL")
            self.send_email = False
            # self.template = "email/mortgage_lead_received.html"

        elif stage == STAGE_ClosedLOST:
            # self.subject = MORTGAGE_EMAIL_SUBJECTS.get("NEW_DEAL")
            self.send_email = False
            # self.template = "email/mortgage_lead_received.html"

        else:
            self.context = ''
            self.subject = ''

        self.bcc_addresses = bcc_addresses
        if not deal.customer.email:
            raise ValidationError("Email is required")

        self.to_email = deal.customer.email
        self.attachments = attachments

    def stage_propagation_email(self, stage=True):
        if not self.send_email:
            ...
        self.rendered = render_to_string(self.template, self.context)
        self.from_email = "quotes@nexusmb.com"
        self.prepare_email()
        self.emailer.get_backend().send_email(**self.email_content)
        from mortgage.models import ProcessEmail
        self.email_content.pop('attachments')
        process_email = ProcessEmail(**self.email_content)
        process_email.deal = self.deal
        process_email.save()
        process_email.attachments.set(self.attachments)
        audit_trail = self.deal.get_audit_trail()
        audit_trail.record_generic_history(
            'email',
            f'Email sent to: {self.to_email} | Subject: {self.subject} emailpk {process_email.pk}',
            self.request.user if self.request else ''
        )
        audit_trail.save()

    def prepare_email(self):
        self.rendered = render_to_string(self.template, self.context)
        self.from_email = MortgageHandleEmailContent._get_from_email_for_deal(self.deal)
        self.reply_to = MortgageHandleEmailContent._get_reply_to_for_deal(self.deal)
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
        from mortgage.constants import DEAL_STAGES
        data = {}
        email = ProcessEmail.objects.get(pk=kwargs.get('pk'))
        data.update(**model_to_dict(email))
        data['from'] = email.from_address
        data['reply_to'] = MortgageHandleEmailContent._get_reply_to_for_deal(email.deal)
        data['stages'] = {x : y for x, y in DEAL_STAGES}
        data['current_stage'] = email.deal.stage
        return JsonResponse({"success": True, "content": data})
    
    def post(self, request, *args, **kwargs):
        post_data = request.POST.dict()
        post_data.pop('csrfmiddlewaretoken', None)
        stage_email = StageEmail(request=request, deal=ProcessEmail.objects.get(pk=kwargs.get('pk')).deal)
        stage_email.send_again(post_data)
        return JsonResponse({"success": True, "message": "ok"})
