"""Utility classes to help with sending emails using various backends. The Emailer class encapsulates the sending logic
and deals with using the correct backend and templates based on the CompanySettings."""
import io
import datetime
import requests
import logging

from django.template import Context
from django.template import Template
from django.template.loader import get_template
from django.urls import reverse
from django.conf import settings

from core.email.backend_console import Console
from core.email.backend_mailgun import Mailgun
from core.email.backend_postmark import Postmark
from core.email.backend_sendgrid import Sendgrid
from core.email.exceptions import EmailSendingException
from core.utils import clean_and_validate_email_addresses
from felix.constants import INVITATION_EXPIRE_DAYS
from felix.settings import POSTMARK_TOKEN
from felix.settings import DOMAIN


class MortgageSendEmail:
    def __init__(self, company):
        self.company = company

    def get_backend(self):
        # if settings.DEBUG:
        #     return Console()

        if POSTMARK_TOKEN:
            return Postmark(self.company)
        else:
            return Mailgun(self.company)

    def send_general_email(self, to_email, subject, content, from_email, cc_emails=None, bcc_emails=None,
                           attachments=None, reply_to=None):
        try:
            self.get_backend().send_email(
                from_email,
                to_email,
                subject,
                '',
                html=content,
                attachments=attachments,
                cc_addresses=cc_emails,
                bcc_addresses=bcc_emails,
                reply_to=reply_to
            )
        except EmailSendingException as e:
            logger = logging.getLogger('user_facing')
            logger.error('Unable to send email to {} subject {}. Error: {}'.format(to_email, subject, str(e)))

    def send_lead_received_email(self, deal):
        try:
            ctx = {
                'company_name': 'Nexus Mortgage Brokers - quotes@nexusmb.com',
                'customer_name': deal.customer.name,
                'car_name': deal.get_car_title()
            }

            # if self.company_settings.motor_email_subject_lead_submitted:
            #     template = Template(self.company_settings.motor_email_subject_lead_submitted)
            #     subject = template.render(Context(ctx))
            # else:
            subject = f'Thank you for trusting {deal.company.name} with your motor insurance needs'

            # if self.company_settings.motor_email_content_lead_submitted:
            #     template = Template(self.company_settings.motor_email_content_lead_submitted)
            #     content = template.render(Context(ctx))
            # else:
            text_template = get_template('email/motor_insurance_lead_received.html')
            content = text_template.render(ctx)

            from_email = 'Nexus Mortgage Brokers - quotes@nexusmb.com'

            bcc_emails = clean_and_validate_email_addresses(
                self.company.workspacemotorsettings.lead_notification_email_list)

            if self.company.workspacemotorsettings.send_company_email_on_lead_form_submission:
                bcc_emails = clean_and_validate_email_addresses(
                    '{}, {}'.format(bcc_emails, self.company.workspacemotorsettings.email))

            if deal.assigned_to and deal.assigned_to.userprofile.bcc_all_emails:
                bcc_emails = clean_and_validate_email_addresses(
                    '{}, {}'.format(bcc_emails, deal.assigned_to.email))

            if deal.assigned_to and deal.assigned_to.userprofile.email_if_lead_created_using_personal_link:
                bcc_emails = clean_and_validate_email_addresses(
                    '{}, {}'.format(bcc_emails, deal.assigned_to.email))

            if deal.producer and deal.producer.userprofile.email_if_lead_created_using_personal_link:
                bcc_emails = clean_and_validate_email_addresses(
                    '{}, {}'.format(bcc_emails, deal.producer.email))

            self.get_backend().send_email(
                from_email, deal.customer.email, subject, '', html=content, bcc_addresses=bcc_emails)

        except EmailSendingException as e:
            logger = logging.getLogger('user_facing')
            logger.error('Unable to send lead received email for lead id {}. Error: {}'.format(deal.lead.pk, str(e)))

    def send_order_confirmation_email(self, deal, attachments=None):
        try:
            subject, content = self.prepare_email_content_for_order_summary(deal)
            from_email = 'Nexus Mortgage Brokers - quotes@nexusmb.com'

            bcc_emails = deal.bcc_emails

            if deal.assigned_to and deal.assigned_to.userprofile.bcc_all_emails:
                bcc_emails = clean_and_validate_email_addresses(
                    '{}, {}'.format(bcc_emails, deal.assigned_to.email))

            if deal.producer and deal.producer.userprofile.bcc_all_emails:
                bcc_emails = clean_and_validate_email_addresses(
                    '{}, {}'.format(bcc_emails, deal.producer.email))

            if self.company.workspacemotorsettings.bcc_all_emails:
                bcc_emails = clean_and_validate_email_addresses(
                    '{}, {}'.format(bcc_emails, self.company.workspacemotorsettings.email))

            self.get_backend().send_email(
                from_email,
                deal.customer.email,
                subject,
                '',
                html=content,
                attachments=attachments,
                cc_addresses=deal.cc_emails,
                bcc_addresses=bcc_emails
            )

        except EmailSendingException as e:
            logger = logging.getLogger('user_facing')
            logger.error('Unable to send order confirmation email for deal {}. Error: {}'.format(deal.pk, str(e)))

    def send_order_confirmation_email_to_agent(self, deal, attachments=None):
        try:
            subject = f'Order Confirmation for {deal.get_car_title()}'
            from_email = 'Nexus Mortgage Brokers <quotes@nexusmb.com>'

            ctx = {
                'customer_name': deal.customer.name,
                'assigned_to': deal.assigned_to.get_full_name() if deal.assigned_to else deal.company.name,
                'deal_url': "https://{}{}".format(
                    settings.DOMAIN,
                    reverse('motorinsurance:deal-edit', kwargs={'pk': deal.pk}),
                ),
                'deal_title': deal.get_car_title()
            }

            bcc_emails = ''

            if self.company.workspacemotorsettings.send_company_email_on_order_created_online:
                bcc_emails = clean_and_validate_email_addresses(
                    '{}, {}'.format(bcc_emails, self.company.workspacemotorsettings.email))

            text_template = get_template('email/motor_insurance_order_confirmation_agent_notification.html')
            content = text_template.render(ctx)

            self.get_backend().send_email(
                from_email,
                deal.assigned_to.email,
                subject,
                '',
                html=content,
                attachments=attachments,
                bcc_addresses=bcc_emails
            )

        except EmailSendingException as e:
            logger = logging.getLogger('user_facing')
            logger.error('Unable to send order confirmation email to Agent for deal {}. Error: {}'.format(deal.pk, str(e)))

    def send_tasks_summary_cron_email(self, user, todays_tasks=None, overdue_tasks=None):
        try:
            ctx = {
                'user_name': user.get_full_name(),
                'todays_tasks': todays_tasks,
                'overdue_tasks': overdue_tasks,
                'todays_tasks_link': "https://{}{}?page=1&filter_type=today&assigned_to={}".format(
                    settings.DOMAIN,
                    reverse('motorinsurance:tasks'),
                    user.pk
                ),
                'overdue_tasks_link': "https://{}{}?page=1&filter_type=overdue&assigned_to={}".format(
                    settings.DOMAIN,
                    reverse('motorinsurance:tasks'),
                    user.pk
                )
            }

            subject = 'Your InsureNex Tasks Reminder for {}'.format(
                datetime.datetime.today().strftime('%A, %d %B %Y'))

            text_template = get_template('email/cron_tasks_summary.html')
            content = text_template.render(ctx)

            self.get_backend().send_email(settings.DEFAULT_FROM_EMAIL, user.email, subject, '', html=content)

        except EmailSendingException as e:
            logger = logging.getLogger('workers')
            logger.error('Unable to send tasks cron email to user {}. Error: {}'.format(user.email, str(e)))

    def send_invitation_email(self, invitation):
        try:
            ctx = {
                'user_name': invitation.first_name or invitation.email,
                'expiry_days': INVITATION_EXPIRE_DAYS,
                'company_name': 'Nexus Mortgage Brokers - quotes@nexusmb.com',
                'sender_name': invitation.sender.get_full_name(),
                'invitation_url': "https://{}{}".format(
                    settings.DOMAIN,
                    invitation.get_absolute_url()
                )
            }

            subject = 'Join {} on InsureNex'.format(self.company.name)

            text_template = get_template('email/invitation_email.html')
            content = text_template.render(ctx)

            self.get_backend().send_email(settings.DEFAULT_FROM_EMAIL, invitation.email, subject, '', html=content)

        except EmailSendingException as e:
            logger = logging.getLogger('workers')
            logger.error('Unable to send invitation email to user {}. Error: {}'.format(invitation.email, str(e)))

    def prepare_email_content_for_new_deal(self, deal):
        ctx = {
            'company_name': 'Nexus Mortgage Brokers',
            'customer_name': deal.referrer,
        }
        subject = 'Thank you for trusting Nexus Mortgage Brokers with your mortgage needs'
        text_template = get_template('email/mortgage_lead_received.html')
        content = text_template.render(ctx)

        return subject, content

    def prepare_email_content_for_quote(self, deal, updated=False):
        quote_url = f"{DOMAIN}/mortgage-quote/{deal.mortgage_quote_deals.reference_number}/{deal.pk}/"
        
        ctx = {
            'company_name': 'Nexus Mortgage Brokers',
            'customer_name': deal.referrer,
            'quote_url' : quote_url,
        }

        subject = 'Mortgage Quote'
        text_template = get_template('email/mortgage_quote_generated.html')
        content = text_template.render(ctx)

        return subject, content

    def prepare_email_content_for_pre_approval(self, deal):
        ctx = {
            'company_name': 'Nexus Mortgage Brokers',
            'customer_name': deal.referrer,
            "upload_url" : "/mortgage-quote/"+str(deal.mortgage_quote_deals.reference_number)+"/"+str(deal.pk)+"/"
        }

        subject = 'Mortgage Pre Approval'
        text_template = get_template('email/mortgage_pre_approval.html')
        content = text_template.render(ctx)

        return subject, content

    def prepare_email_content_for_valuation(self, deal):
        ctx = {
            'company_name': 'Nexus Mortgage Brokers',
            'customer_name': deal.referrer
        }

        subject = 'Mortgage Valuation'
        text_template = get_template('email/mortgage_valuation_generated.html')
        content = text_template.render(ctx)

        return subject, content

    def prepare_email_content_for_final_offer(self, deal):
        ctx = {
            'company_name': 'Nexus Mortgage Brokers',
            'customer_name': deal.referrer
        }

        subject = 'Mortgage Final Offer'
        text_template = get_template('email/mortgage_offer_generated.html')
        content = text_template.render(ctx)

        return subject, content

    def prepare_email_content_for_settlement(self, deal):
        ctx = {
            'company_name': 'Nexus Mortgage Brokers',
            'customer_name': deal.referrer
        }

        subject = 'Mortgage Settlement'
        text_template = get_template('email/mortgage_settlement_generated.html')
        content = text_template.render(ctx)

        return subject, content

    def prepare_email_content_for_loan_disbursal(self, deal):
        ctx = {
            'company_name': 'Nexus Mortgage Brokers',
            'customer_name': deal.referrer
        }

        subject = 'Mortgage Loan Disbursal'
        text_template = get_template('email/mortgage_loan_disbursal.html')
        content = text_template.render(ctx)

        return subject, content

    def prepare_email_content_for_property_transfer(self, deal):
        ctx = {
            'company_name': 'Nexus Mortgage Brokers',
            'customer_name': deal.referrer
        }

        subject = 'Mortgage Property Transfer'
        text_template = get_template('email/mortgage_property_transfer.html')
        content = text_template.render(ctx)

        return subject, content

    def append_required_helpers_in_content(self, content):
        required_helpers = "{% load humanize %}{% load motorinsurance %}"

        return '{}{}'.format(required_helpers, content)

    def send_form_submission_emails(self, form_submission, agent):
        form = form_submission.form
        bcc_emails = ''
        documents = ''
        subject = '{} submitted by user'.format(form.title)
        email_body = f'<p>Hi,</p><p>A new submission has been made for the form "{form.title}".</p><p>Thanks,<br>Team InsureNex</p>'

        to_email = self.company.workspacemotorsettings.email
        from_email = 'Nexus Mortgage Brokers - quotes@nexusmb.com'

        if agent:
            bcc_emails = agent.email

        if form_submission.file:
            pdf_content = requests.get(form_submission.file)
            file = io.BytesIO(pdf_content.content)
            documents = [(f'{form.title}.pdf', file, 'application/pdf')]

        self.send_general_email(
            to_email=to_email,
            subject=subject,
            content=email_body,
            from_email=from_email,
            bcc_emails=bcc_emails,
            attachments=documents)

    def send_document_signed_email(self, form_submission, signer_email, signer_name="", agent=None, attachment=None):
        form = form_submission.form
        cc_emails = []
        documents = ''
        subject = 'Thank you for submitting {} on {}'.format(form.title, self.company.name)
        email_body = f'<p>Hi {signer_name},</p><p>Thank you for submitting {form.title}. We\'ve received your ' \
                     f'details and attached is the copy for your reference.</p><p>Thanks,<br>Team InsureNex</p>'

        cc_emails.append(self.company.workspacemotorsettings.email)
        from_email = 'Nexus Mortgage Brokers - quotes@nexusmb.com'

        if agent:
            cc_emails.append(agent.email)

        if attachment:
            attachment.seek(0)
            documents = [(f'{form.title}.pdf', attachment, 'application/pdf')]

        self.send_general_email(
            to_email=signer_email,
            subject=subject,
            content=email_body,
            from_email=from_email,
            cc_emails=cc_emails,
            attachments=documents)
