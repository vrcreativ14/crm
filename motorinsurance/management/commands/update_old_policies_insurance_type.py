from django.core.management import BaseCommand

from accounts.models import Company
from motorinsurance.models import Policy
from motorinsurance.constants import INSURANCE_TYPE_COMPREHENSIVE, INSURANCE_TYPE_TPL


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-c', '--company_id', type=int, help='Update records for the specified company only')

    def handle(self, *args, **options):
        company_id = options['company_id']

        active_companies = Company.objects.filter(status=Company.STATUS_ACTIVE)

        if company_id:
            active_companies = active_companies.filter(pk__in=str(company_id).split(','))
        else:
            self.stdout.write('Running for all active companies')

        for company in active_companies:
            if company.schema_name == 'public':
                continue

            company.activate()

            self.stdout.write('********* {} *********'.format(company.name))

            policies = Policy.objects.filter(company=company, product__isnull=False)
            self.stdout.write('***** {} policies found *****'.format(policies.count()))

            for policy in policies:
                new_insurance_type = INSURANCE_TYPE_TPL if policy.product.is_tpl_product else INSURANCE_TYPE_COMPREHENSIVE
                self.stdout.write('Updating {} - old: {}, new: {}'.format(
                    policy.pk, policy.insurance_type, new_insurance_type
                ))
                policy.insurance_type = new_insurance_type
                policy.save()
