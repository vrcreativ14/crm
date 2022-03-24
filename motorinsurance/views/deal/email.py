import io

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from django.utils.html import escape
from django.views.generic import DetailView

from core.pdf import PDF
from core.utils import clean_and_validate_email_addresses
from core.email import Emailer, EmailSendingException

from motorinsurance.models import Deal

from felix.sms import SMSService
from felix.message import WhatsappService


class DealHandleEmailContent(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.list_motor_deals'
    model = Deal

    available_email_templates = [
        'latest',  # if this is provided, will check the deal's stage and return the email template accordingly
        'new_deal',
        'new_quote',
        'quote_updated',
        'order_confirmation',
        'policy_issued',
    ]

    @classmethod
    def _get_from_email_for_deal(cls, deal):
        company = deal.company
        company_settings = company.companysettings
        workspace_settings = company.workspacemotorsettings

        from_email = company_settings.from_email or workspace_settings.email

        if deal.assigned_to and deal.assigned_to.first_name:
            return f'{deal.assigned_to.first_name} at {company.name} <{from_email}>'
        else:
            return f'{company.name} <{from_email}>'

    @classmethod
    def _get_reply_to_for_deal(cls, deal):
        company = deal.company
        workspace_settings = company.workspacemotorsettings

        if workspace_settings.reply_to_company_email and workspace_settings.email:
            reply_to_name = company.name
            reply_to_address = workspace_settings.email
        else:
            if deal.assigned_to and deal.assigned_to.email:
                reply_to_address = deal.assigned_to.email
            else:
                reply_to_address = workspace_settings.email

            if deal.assigned_to and deal.assigned_to.get_full_name():
                reply_to_name = deal.assigned_to.get_full_name()
            else:
                reply_to_name = company.name

        return f'{reply_to_name} <{reply_to_address}>'

    def dispatch(self, *args, **kwargs):
        email_type = kwargs['type']

        if email_type == 'latest':
            deal = self.get_object()

            if deal.stage == Deal.STAGE_NEW:
                kwargs['type'] = 'new_deal'
            elif deal.stage == Deal.STAGE_QUOTE:
                kwargs['type'] = 'quote_updated' if deal.quote else 'new_quote'
            elif deal.stage == Deal.STAGE_ORDER:
                kwargs['type'] = 'order_confirmation'
            elif deal.stage in [Deal.STAGE_HOUSEKEEPING, Deal.STAGE_WON, Deal.STAGE_LOST]:
                kwargs['type'] = 'policy_issued'

        return super().dispatch(*args, **kwargs)

    def _validate_fields(self):
        errors = {}

        to = self.request.POST['email']
        cc_emails = self.request.POST['cc_emails']
        bcc_emails = self.request.POST['bcc_emails']

        if to and not clean_and_validate_email_addresses(to):
            errors['email'] = 'Invalid format for email address(es).'

        if cc_emails and not clean_and_validate_email_addresses(cc_emails):
            errors['cc_emails'] = 'Invalid format for email address(es).'

        if bcc_emails and not clean_and_validate_email_addresses(bcc_emails):
            errors['bcc_emails'] = 'Invalid format for email address(es).'

        return errors

    def _get_allowed_templates(self):
        deal = self.get_object()

        allowed_templates = {
            'new_deal': 'New Deal',
        }

        if deal.stage in [Deal.STAGE_QUOTE, Deal.STAGE_ORDER, Deal.STAGE_HOUSEKEEPING, Deal.STAGE_WON, Deal.STAGE_LOST]:
            allowed_templates['new_quote'] = 'New Quote'
            allowed_templates['quote_updated'] = 'Quote Updated'

        if deal.stage in [Deal.STAGE_ORDER, Deal.STAGE_HOUSEKEEPING, Deal.STAGE_WON, Deal.STAGE_LOST]:
            allowed_templates['order_confirmation'] = 'Order Confirmation'

        if deal.stage in [Deal.STAGE_HOUSEKEEPING, Deal.STAGE_WON, Deal.STAGE_LOST]:
            allowed_templates['policy_issued'] = 'Policy Issued'

        return allowed_templates

    def post(self, request, *args, **kwargs):
        deal = self.get_object()
        company = deal.company
        email_type = kwargs['type']

        emailer = Emailer(company)

        from_email = self._get_from_email_for_deal(deal)
        reply_to = self._get_reply_to_for_deal(deal)

        to = request.POST['email']
        subject = request.POST['subject']
        content = request.POST['content']
        cc_emails = request.POST['cc_emails']
        bcc_emails = request.POST['bcc_emails']
        sms_content = request.POST['sms_content']
        wa_msg_content = request.POST['wa_msg_content']
        attachments = None

        validation_errors = self._validate_fields()

        if len(validation_errors):
            return JsonResponse({'success': False, 'errors': validation_errors})

        if email_type == 'policy_issued':
            attachments = emailer.get_policy_attachments(deal.policy)

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
                cc_emails=clean_and_validate_email_addresses(cc_emails),
                bcc_emails=clean_and_validate_email_addresses(bcc_emails),
                reply_to=reply_to,
                attachments=attachments
            )
            success = True

            if (email_type == 'new_quote' or email_type == 'quote_updated') and not deal.quote_sent:
                deal.quote_sent = True
                deal.save(user=request.user)

            audit_trail = deal.get_audit_trail()
            audit_trail.record_generic_history(
                'email',
                f'Email sent to: {cleaned_to} | Subject: {subject}',
                request.user
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
                app_name = 'motor'
            )

        return JsonResponse({'success': success, 'email_type': email_type})

    def get(self, request, *args, **kwargs):
        deal = self.get_object()

        subject = ''
        content = ''
        sms_content = None
        email_type = kwargs['type']
        updated = 'updated' in request.GET
        documents = []

        company = deal.company
        workspace_settings = company.workspacemotorsettings

        emailer = Emailer(company)

        if email_type not in self.available_email_templates:
            return JsonResponse({'errors': 'Not a valid email type provided.'})

        if email_type == 'new_deal':
            subject, content = emailer.prepare_email_content_for_new_deal(deal)
            sms_content = f'Thank you for requesting car insurance quotes from {company.name}. We\'re preparing some options for you and will send you an email soon!'

        elif email_type == 'new_quote' or email_type == 'quote_updated':
            updated = email_type == 'quote_updated'
            subject, content = emailer.prepare_email_content_for_quote(deal.quote, updated)

            sms_content = 'Hi {}, your {} car insurance quotes are ready: {}'.format(
                deal.customer.name,
                deal.company.name,
                deal.quote.get_quote_short_url(),
            )

            if updated:
                sms_content = 'Hi {}, we\'ve updated your car insurance quotes. Click here to check them out: {}'.format(
                    deal.customer.name.title(),
                    deal.quote.get_quote_short_url(),
                )
        elif email_type == 'order_confirmation':
            subject, content = emailer.prepare_email_content_for_order_summary(deal)
            document_upload_url = deal.quote.get_document_upload_short_url()
            sms_content = 'Hi {}, thanks for your order! Please upload your documents here so we can issue your policy: {}'.format(
                deal.customer.name,
                document_upload_url
            )
        elif email_type == 'policy_issued':
            subject, content, documents = emailer.prepare_email_content_for_policy(deal.policy)

            if not updated:
                sms_content = 'Hi {}, we\'ve issued your insurance policy! Check your email for details.'.format(
                    deal.customer.name.title())

        bcc_emails = list()

        if deal.bcc_emails:
            bcc_emails.append(deal.bcc_emails)

        # checking workspace_settings and userprofile if we can send copy of all emails
        # to company and user (deal assigned to) email addresses.
        if workspace_settings.bcc_all_emails and workspace_settings.email:
            bcc_emails.append(workspace_settings.email)
        if deal.assigned_to and deal.assigned_to.email:
            bcc_emails.append(deal.assigned_to.email)
        if deal.producer and deal.producer.email:
            bcc_emails.append(deal.producer.email)

        if len(bcc_emails):
            bcc_emails = ', '.join(
                set(sorted(bcc_emails, key=lambda v: v, reverse=True)))

        from_email = escape(self._get_from_email_for_deal(deal))
        reply_to = escape(self._get_reply_to_for_deal(deal))

        return JsonResponse({
            'from': from_email,
            'reply_to': reply_to,
            'to': deal.customer.email,
            'cc_emails': deal.cc_emails,
            'bcc_emails': bcc_emails,
            'subject': subject,
            'content': content,
            'sms_content': sms_content,
            'whatsapp_msg_content': sms_content,
            'attachments': [{
                'name': document[0],
                'url': document[1].url
            } for document in documents],

            'allowed_templates': self._get_allowed_templates(),
            'email_type': email_type,
            'stage': deal.stage,
        }, safe=False)
