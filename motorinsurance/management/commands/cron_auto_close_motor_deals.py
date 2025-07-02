import datetime

from django.core.management.base import BaseCommand
from django.utils.timezone import now as tz_now

from accounts.models import Company, WorkspaceMotorSettings
from motorinsurance.models import Quote
from motorinsurance.tasks import add_note_to_deal


class Command(BaseCommand):
    help = 'Auto Close Quoted Motor Deals'

    def add_arguments(self, parser):
        parser.add_argument('-c', '--company_id', type=int, help='Update deals for the specified company only')
        parser.add_argument('-n', '--dry_run', action='store_true',
                            help='Print changes that would be made without making those changes')

    def handle(self, *args, **options):
        company_id = options['company_id']
        print_only = options['dry_run']

        cs_active_companies = WorkspaceMotorSettings.objects.filter(
            auto_close_quoted_deals_in_days__gt=0, company__status=Company.STATUS_ACTIVE)

        if company_id:
            cs_active_companies = cs_active_companies.filter(company__in=str(company_id).split(','))

        for cs in cs_active_companies:
            if cs.company.schema_name == 'public':
                continue

            cs.company.activate()

            self.stdout.write(f'\n>>>> Executing for {cs.company}:')
            self.stdout.write(f'\t>>>> Checking for quotes older than {cs.auto_close_quoted_deals_in_days} days')

            threshold_date = tz_now() - datetime.timedelta(days=cs.auto_close_quoted_deals_in_days)

            quotes = Quote.objects.filter(deal__stage='quote',
                                          updated_on__lt=threshold_date,
                                          deal__updated_on__lt=threshold_date)

            for quote in quotes:
                if print_only:
                    self.stdout.write('\t\t>>>> Running in Dry Run mode. Not saving changes')
                else:
                    quote.deal.stage = 'lost'
                    quote.deal.save()

                    note_content = (
                        f'Deal was closed automatically after being inactive for '
                        f'{cs.auto_close_quoted_deals_in_days} days'
                    )

                    add_note_to_deal(quote.deal, note_content)

                self.stdout.write(f'\t\t>>>> Closed Deal: {quote.deal}')
