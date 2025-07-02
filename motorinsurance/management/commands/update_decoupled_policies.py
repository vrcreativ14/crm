from django.core.management import BaseCommand

from accounts.models import Company
from motorinsurance.models import Policy


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-c', '--company_id', type=int, help='Update records for the specified company only')

    def handle(self, *args, **options):
        company_id = options['company_id']

        self.stdout.write('Fetch all active companies from DB')

        active_companies = Company.objects.filter(status=Company.STATUS_ACTIVE)

        if company_id:
            active_companies = active_companies.filter(pk__in=str(company_id).split(','))
        else:
            self.stdout.write('Fetch all active companies from DB')

        for company in active_companies:
            if company.schema_name == 'public':
                continue

            company.activate()

            self.stdout.write('********* {} *********'.format(company.name))

            policies = Policy.objects.filter(company=company, premium=0)
            self.stdout.write('***** {} policies found *****'.format(policies.count()))

            for policy in policies:
                self.stdout.write('Updating {} - {}'.format(policy.pk, policy))

                if policy.deal:
                    policy.car_year = policy.deal.car_year
                    policy.car_make = policy.deal.car_make
                    policy.car_trim = policy.deal.car_trim
                    policy.custom_car_name = policy.deal.custom_car_name
                    policy.insurance_type = policy.deal.current_insurance_type

                    order = policy.deal.get_order()

                    if order:
                        product = order.selected_product
                        policy.agency_repair = product.agency_repair
                        policy.ncd_required = product.ncd_required

                        policy.premium = order.payment_amount
                        policy.deductible = product.deductible
                        policy.deductible_extras = product.deductible_extras
                        policy.insured_car_value = product.insured_car_value
                        policy.mortgage_by = order.mortgage_by

                        policy.default_add_ons = product.default_add_ons
                        policy.paid_add_ons = order.selected_add_ons

                    try:
                        policy.save()
                    except Exception as e:
                        self.stdout.write('ERROR >> C: {}, PID:{}, {}'.format(company, policy.pk, e))
                        pass
