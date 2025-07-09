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
from healthinsurance_shared.models import MessageTemplates
from healthinsurance.constants import DEAL_TYPE_RENEWAL, EMIRATE_DUBAI   

class SendHealthInsuranceEmail:
    def __init__(self, company):
        self.company = company

    def _get_email_address_for_deal(self, deal):
        if hasattr(deal, 'deal_type') and deal.deal_type != DEAL_TYPE_RENEWAL:
            if (hasattr(deal, 'primary_member') and deal.primary_member and 
                hasattr(deal.primary_member, 'visa') and deal.primary_member.visa == EMIRATE_DUBAI):
                return 'nbind.medical@nexusadvice.com'
            else:
                return 'ind.medical@nexusadvice.com'
        elif (hasattr(deal, 'deal_type') and deal.deal_type == DEAL_TYPE_RENEWAL and 
              hasattr(deal, 'primary_member') and deal.primary_member and 
              hasattr(deal.primary_member, 'visa') and deal.primary_member.visa == EMIRATE_DUBAI):  # Renewal for Dubai
            return 'rwind.medical@nexusadvice.com'
        else:
            return 'ind.medical@nexusadvice.com'

    def get_email_template(self,**kwargs):
        type = kwargs.get('type')
        insurer = kwargs.get('insurer')
        template = MessageTemplates.objects.filter(type__name__iexact = type)
        if insurer:
            insurer_template = template.filter(insurer = insurer)
            if insurer_template.exists():
                return insurer_template[0].subject,insurer_template[0].email_content
        
        if template.exists():
            return template[0].subject,template[0].email_content
        else:
            return '',''

    def get_message_templates(self,**kwargs):
        type = kwargs.get('type')
        insurer = kwargs.get('insurer')
        template = MessageTemplates.objects.filter(type__name__iexact = type)
        message = {}
        if insurer:
            insurer_template = template.filter(insurer = insurer)
            if insurer_template.exists():
                return insurer_template[0].subject,insurer_template[0].email_content
        
        if template.exists():
            message = {
                'subject': template[0].subject,
                'email_content': template[0].email_content,
                'wa_msg_content': template[0].whatsapp_msg_content,
            }
        else:
            message = {
                'subject': '',
                'email_content': '',
                'wa_msg_content': '',
            }

        return message

    def get_backend(self):
        # if settings.DEBUG:
        #     return Console()
        if POSTMARK_TOKEN:
            return Postmark(self.company)
        else:
            return Mailgun(self.company)

    def render_context(self, message, ctx):        
        template = Template(message.get('email_content'))
        message['email_content'] = template.render(Context(ctx))
        template = Template(message.get('subject'))
        message['subject'] = template.render(Context(ctx))
        template = Template(message.get('wa_msg_content'))
        message['wa_msg_content'] = template.render(Context(ctx))
        return message

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


    def prepare_email_content(self, deal, stage_type):
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.customer.name if deal.customer and deal.customer.name else deal.primary_member.name,
        }

        message = self.get_message_templates(type = stage_type)
        template = Template(message.get('email_content'))
        message['email_content'] = template.render(Context(ctx))
        template = Template(message.get('subject'))
        message['subject'] = template.render(Context(ctx))
        template = Template(message.get('wa_msg_content'))
        message['wa_msg_content'] = template.render(Context(ctx))
        return message

    def prepare_email_content_for_new_deal(self, deal):
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.customer.name if deal.customer and deal.customer.name else deal.primary_member.name,
        }
        if deal.stage == 'basic':
            quote = deal.get_quote()
            if quote:
                quote_url = f"https://{DOMAIN}/health-insurance-quote/{quote.reference_number}/{deal.pk}/" 
                ctx['quote_url'] = quote_url
            message = self.get_message_templates(type = 'basic new deal')
        else:
            message = self.get_message_templates(type = 'new deal')
        #subject = 'Thank you for trusting Nexus Brokers with your Health Insurance needs'
        #text_template = get_template('email/health_insurance_lead_received.html')
        return self.render_context(message, ctx)
        

    def prepare_email_content_for_quote(self, deal,quote,updated=False):
        
        quote_url = f"https://{DOMAIN}/health-insurance-quote/{quote.reference_number}/{deal.pk}/"        
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.primary_member.name,
            'quote_url' : quote_url,
        }
        if deal.referrer:
            ctx.update({'referrer':deal.referrer})
        if deal.user:
            ctx.update({'assigned_to':deal.user})
        if updated:
            message = self.get_message_templates(type = 'quote updated')
        else:
            message = self.get_message_templates(type = 'new quote')
        #text_template = get_template('email/health_insurance_quote_generated.html')
        return self.render_context(message, ctx)

    def prepare_email_content_for_renewal_deal(self, deal, email_type = ''):
        if deal:
            quote = deal.get_quote()
            if quote:
                quote_url = f"https://{DOMAIN}/health-insurance-quote/{quote.reference_number}/{deal.pk}/"
        policy = deal.get_policy()
        policy_number = policy.policy_number if policy else ''
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.primary_member.name,
            'quote_url' : quote_url,
            'policy_number':policy_number
        }
        if email_type == 'renewal basic':
            insurer_name = deal.selected_plan.insurer.name if deal and deal.selected_plan else ''
            ctx.update({'insurer_name':insurer_name})
        if deal.referrer:
            ctx.update({'referrer':deal.referrer})
        if deal.user:
            ctx.update({'assigned_to':deal.user})

        message = self.get_message_templates(type = email_type)
        return self.render_context(message, ctx)

    def prepare_email_content_for_documents(self, deal):
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.customer.name,
            "upload_url" : "/mortgage-quote/"+str(deal.mortgage_quote_deals.reference_number)+"/"+str(deal.pk)+"/"
        }
        message = self.get_message_templates(type = 'documents')
        return self.render_context(message, ctx)

    def prepare_email_content_for_order_summary(self, deal, email_type = ''):
        order = deal.get_order()
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.customer.name,
            'insurer_name': order.selected_plan.plan.insurer.name if order and order.selected_plan else '',
            'selected_plan': order.selected_plan.plan.name if order and order.selected_plan else '',
        }
        if 'team notification' in email_type.lower():
            ctx['deal_url'] = '{}/health-insurance/deals/{}'.format(settings.DOMAIN, deal.pk)
            message = self.get_message_templates(type = 'order confirmation team notification')
        else:
            message = self.get_message_templates(type = 'order')
            if deal.user:
                ctx.update({'assigned_to':deal.user})
        
        return self.render_context(message, ctx)

    def prepare_email_content_for_final_quote(self, deal, quote):
        order = deal.get_order()
        quote_url = f"https://{DOMAIN}/health-insurance-quote/{quote.reference_number}/{deal.pk}/"
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.customer.name,
            'quote_url' : quote_url,
            'insurer_name': order.selected_plan.plan.insurer.name if order and order.selected_plan else '',
            'selected_plan': order.selected_plan.plan.name if order and order.selected_plan else '',
        }
        if deal.user:
            ctx.update({'assigned_to':deal.user})
        message = self.get_message_templates(type = 'Final Quote')
        return self.render_context(message, ctx)

    def prepare_email_content_for_final_quote_submitted(self, deal):
        order = deal.get_order()
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.customer.name,
            'insurer_name': order.selected_plan.plan.insurer.name if order and order.selected_plan else '',
            'selected_plan': order.selected_plan.plan.name if order and order.selected_plan else '',
        }
        if deal.user:
            ctx.update({'assigned_to':deal.user})
        message = self.get_message_templates(type = 'Final Quote Submitted')
        return self.render_context(message, ctx)

    def prepare_email_content_for_payment(self, deal, quote):
        order = deal.get_order()
        payment_details = deal.get_payment_details()
        quote_url = f"https://{DOMAIN}/health-insurance-quote/{quote.reference_number}/{deal.pk}/"
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.primary_member.name,
            'insurer_name': order.selected_plan.plan.insurer.name if order and order.selected_plan else '',
            'selected_plan': order.selected_plan.plan.name if order and order.selected_plan else '',
            'currency': order.selected_plan.plan.currency if order and order.selected_plan else '',
            'premium': deal.total_premium,
            'payment_details': payment_details,
            'quote_url' : quote_url,
        }
        if deal.user:
            ctx.update({'assigned_to':deal.user})
        message = self.get_message_templates(type = 'payment')
        #text_template = get_template('email/heath_insurance_final_quote.html')
        return self.render_context(message, ctx)
    
    def prepare_email_content_for_payment_confirmation(self, deal):
        order = deal.get_order()
        payment_details = deal.get_payment_details()
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.primary_member.name,            
        }
        if deal.user:
            ctx.update({'assigned_to':deal.user})
        message = self.get_message_templates(type = 'payment confirmation')
        return self.render_context(message, ctx)

    def prepare_email_content_for_policy_issuance(self, deal, quote):
        quote_url = f"https://{DOMAIN}/health-insurance-quote/{quote.reference_number}/{deal.pk}/"
        insurer = deal.selected_plan.insurer if deal and deal.selected_plan else None
        policy = deal.get_policy()
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.customer.name,
            'quote_url' : quote_url,
            'insurer_name': insurer.name if insurer else '',
            'policy_number': policy.policy_number if policy else '',
        }
        if deal.user:
            ctx.update({'assigned_to':deal.user})

        message = self.get_message_templates(type = 'policy issuance', insurer = insurer)
        #text_template = get_template('email/heath_insurance_policy_issuance.html')
        return self.render_context(message, ctx)

    def prepare_email_content_for_housekeeping(self, deal):
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.customer.name
        }

        message = self.get_message_templates(type = 'housekeeping')
        return self.render_context(message, ctx)


    def prepare_email_content_for_deal_won(self, deal):
        ctx = {
            'company_name': 'Nexus Insurance Brokers',
            'customer_name': deal.customer.name
        }

        message = self.get_message_templates(type = 'deal won')
        template = Template(message.get('email_content'))
        return self.render_context(message, ctx)

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
        from_email = 'Nexus Insurance Brokers - ind.medical@nexusadvice.com'

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
        from_email = 'Nexus Insurance Brokers - ind.medical@nexusadvice.com'

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
