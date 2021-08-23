from django.core.management.base import BaseCommand

from django.conf import settings
from core.algolia import Algolia
from felix.constants import ITEMS_PER_PAGE

from accounts.models import Company
from motorinsurance.models import Policy


class Command(BaseCommand):
    help = 'Reindex motor policy records to Algolia'
    algolia = Algolia()
    env = settings.ALGOLIA['ENV']

    def add_arguments(self, parser):
        parser.add_argument('-c', '--company_id', type=int, help='Update records for the specified company only')

    def handle(self, *args, **options):
        company_id = options['company_id']

        active_companies = Company.objects.filter(status=Company.STATUS_ACTIVE)

        if company_id:
            active_companies = active_companies.filter(pk__in=str(company_id).split(','))

        for company in active_companies:
            if company.schema_name == 'public':
                continue

            company.activate()

            policies = Policy.objects.filter(company=company)
            self.stdout.write(f'\n\n------------------------------\nCompany: \t{company}\nPolicies:\t{policies.count()}\n------------------------------\n\n')
            k = 1
            for policy in policies:
                self.stdout.write(f'({k}/{policies.count()}) >> {policy}')
                k += 1
                self.algolia.upsert_motor_policy_record(policy)
