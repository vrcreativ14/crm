from django.core.management import BaseCommand
from core.email import Emailer, EmailSendingException

from accounts.models import Company, CompanySettings
from motorinsurance.models import Deal


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-c', '--company_id', type=int, help='Company ID')
        parser.add_argument('-did', '--deal_id', type=int, help='Deal ID')
        parser.add_argument('--update', action='store_true', help='set this if update email is required')
        parser.add_argument('-to', '--to',
                            type=str,
                            help='Recepient\'s email address(es) (for multiple use , or ; to separate)')
        parser.add_argument('-cc', '--cc',
                            type=str,
                            help='CC email address(es) (for multiple use , or ; to separate)')
        parser.add_argument('-bcc', '--bcc',
                            type=str,
                            help='BCC email address(es) (for multiple use , or ; to separate)')

    def handle(self, *args, **options):
        company_id = options['company_id']
        deal_id = options['deal_id']
        to = options['to']
        cc_emails = options['cc'] or None
        bcc_emails = options['bcc'] or None
        update = options['update'] or False

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            self.stdout.write('ERROR: Invalid company id')
            return

        company.activate()

        company_settings = company.companysettings

        try:
            deal = Deal.objects.get(pk=deal_id)
        except Deal.DoesNotExist:
            self.stdout.write('ERROR: Invalid deal id')
            return

        if not deal.quote:
            self.stdout.write('ERROR: No quote found for the deal id provided')
            return

        quote = deal.quote
        emailer = Emailer(company)

        subject, content = emailer.prepare_email_content_for_quote(quote, update)

        if not to:
            to = self.get_customer_email(deal)

        if not to:
            self.stdout.write('ERROR: Recepient email is empty.')
            return

        if not bcc_emails:
            bcc_emails = self.get_bcc_emails(deal)

        if not cc_emails:
            cc_emails = self.get_cc_emails(deal)

        from_email = self.get_from_email_for_deal(deal)
        reply_to = self.get_reply_to_for_deal(deal)

        try:
            emailer.send_general_email(
                to, subject, content, from_email,
                cc_emails=cc_emails,
                bcc_emails=bcc_emails,
                reply_to=reply_to,
                attachments=None
            )

        except EmailSendingException as e:
            self.stdout.write('ERROR: Cant send email {}'.format(e))

    def get_customer_email(self, deal):
        return deal.customer.email

    def get_bcc_emails(self, deal):
        bcc_emails = list()
        company = deal.company
        company_settings = deal.company.companysettings

        if deal.bcc_emails:
            bcc_emails.append(deal.bcc_emails)

        # checking company_settings and userprofile if we can send copy of all emails
        # to company and user (deal assigned to) email addresses.
        if company_settings.bcc_all_emails and company_settings.email:
            bcc_emails.append(company_settings.email)
        if deal.assigned_to and deal.assigned_to.email:
            bcc_emails.append(deal.assigned_to.email)

        if len(bcc_emails):
            bcc_emails = ', '.join(
                set(sorted(bcc_emails, key=lambda v: v, reverse=True)))

        return bcc_emails

    def get_cc_emails(self, deal):
        return deal.cc_emails

    def get_from_email_for_deal(self, deal):
        company = deal.company
        company_settings = company.companysettings

        if deal.assigned_to and deal.assigned_to.first_name:
            return f'{deal.assigned_to.first_name} at {company.name} <{company_settings.email}>'
        else:
            return f'{company.name} <{company_settings.email}>'

    def get_reply_to_for_deal(self, deal):
        company = deal.company
        company_settings = company.companysettings

        if deal.assigned_to and deal.assigned_to.email:
            reply_to_address = deal.assigned_to.email
        else:
            reply_to_address = company_settings.email

        if deal.assigned_to and deal.assigned_to.get_full_name():
            reply_to_name = deal.assigned_to.get_full_name()
        else:
            reply_to_name = company.name

        return f'{reply_to_name} <{reply_to_address}>'
