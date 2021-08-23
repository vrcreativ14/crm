from django.core.management import BaseCommand
from core.email import Emailer, EmailSendingException

from accounts.models import Company, CompanySettings
from motorinsurance.models import Deal


class Command(BaseCommand):
    def handle(self, *args, **options):
        companies = Company.objects.filter(status=Company.STATUS_ACTIVE)

        for company in companies:
            if company.schema_name == 'public':
                continue

            company.activate()

            cs = company.companysettings

            settings_motor = company.workspacemotorsettings

            self.stdout.write(f'\n>>>> Executing for {company}:\n')

            # Motor Settings
            settings_motor.email = cs.email
            settings_motor.bcc_all_emails = cs.bcc_all_emails
            settings_motor.reply_to_company_email = cs.reply_to_company_email
            settings_motor.send_company_email_on_lead_form_submission = cs.send_company_email_on_motor_lead_form_submission
            settings_motor.send_company_email_on_order_created_online = cs.send_company_email_on_motor_order_created_online
            settings_motor.lead_notification_email_list = cs.lead_notification_email_list
            settings_motor.order_notification_email_list = cs.order_notification_email_list

            settings_motor.save()
            self.stdout.write(f'\t Motor 🚗 Settings Updated')
