from django.core.management.base import BaseCommand

from django.conf import settings
from core.algolia import Algolia
from felix.constants import ITEMS_PER_PAGE

from accounts.models import Company
from customers.models import Customer


class Command(BaseCommand):
    help = 'Reindex deal and customer records to Algolia'
    algolia = Algolia()
    env = settings.ALGOLIA['ENV']
    product_lines = ['motor']

    def add_arguments(self, parser):
        parser.add_argument('-l', '--product_line', type=str, help='Specify product line [motor].')
        parser.add_argument('-s', '--settings_only', action='store_true', help='Update settings only')
        parser.add_argument('-i', '--reindex_only', action='store_true', help='Reindex only')

    def handle(self, *args, **options):
        product_line = options['product_line']
        settings_only = options['settings_only'] or not options['reindex_only']
        reindex_only = options['reindex_only'] or not options['settings_only']

        if product_line and product_line not in self.product_lines:
            self.stdout.write('\nERROR: Invalid product line "{}". Please choose from {}\n'.format(
                product_line, self.product_lines))
            return

        company = Company.objects.first()

        self.stdout.write(f'\n>>>> Executing for {company}:\n')

        if reindex_only:
            self.update_indexes(Customer.objects.all())

        if settings_only:
            self.update_settings(company.pk, product_line)

    def update_indexes(self, customers):
        c = 0
        for customer in customers:
            c += 1
            self.algolia.upsert_customer_record(customer)
            self.stdout.write(f'{c} - Pushing [{customer}] with deals:')

    def update_settings(self, company_id, product_line):
        # Customer settings
        customers_index_name = f'{self.env}_customers_{company_id}'
        customers_index = self.algolia.get_index(customers_index_name)
        customers_index.set_settings({
            'searchableAttributes': [
                'name', 'email', 'phone', 'nationality', 'phone_number_suffixes'
            ],
            'attributesForFaceting': [
                'searchable(status)',
            ],
            'ranking': [
                'desc(created_on)'
            ],
            'hitsPerPage': ITEMS_PER_PAGE,
        })

        self.create_or_update_replicas(customers_index_name)

        self.stdout.write(f'\n🚶 Customers Index settings updated\n')

        if product_line is None or product_line == 'motor':
            self.update_motor_settings(company_id)

    def update_motor_settings(self, company_id):
        # Motor Deals settings
        index_name = f'{self.env}_motor_deals_{company_id}'
        index = self.algolia.get_index(index_name)
        index.set_settings({
            'searchableAttributes': [
                'customer_name', 'customer_email', 'customer_phone', 'customer_nationality',
                'stage', 'car_year', 'car_make', 'custom_car_name', 'cached_car_name',
                'vehicle_insured_value', 'premium', 'assigned_to_name', 'tags'
            ],
            'attributesForFaceting': [
                'searchable(stage)',
                'searchable(assigned_to_id)',
                'searchable(producer_id)',
                'searchable(status)',
                'searchable(tags)',
                'searchable(premium)',
            ],
            'ranking': [
                'desc(created_on)'
            ],
            'hitsPerPage': ITEMS_PER_PAGE,
        })

        self.create_or_update_replicas(index_name)

        self.stdout.write(f'\n🚗 Motor deals Index settings updated\n')

        # Motor policy settings
        policies_index_name = f'{self.env}_motor_policies_{company_id}'
        policies_index = self.algolia.get_index(policies_index_name)
        policies_index.set_settings({
            'searchableAttributes': [
                'customer_name', 'customer_email', 'customer_phone', 'customer_nationality',
                'car_year', 'car_make', 'car_trim', 'custom_car_name', 'car_value',
                'premium', 'policy_title', 'reference_number', 'invoice_number',
                'renewal_deal_stage', 'renewal_deal_id', 'renewal_deal_status', 'has_renewal_deal',
                'owner_id', 'owner_name'
            ],
            'attributesForFaceting': [
                'searchable(product_id)',
                'searchable(insurer_id)',
                'searchable(customer_id)',
                'searchable(insurer_name)',
                'searchable(product_name)',
                'searchable(status)',
                'searchable(premium)',
                'searchable(has_renewal_deal)',
                'searchable(owner_id)',
            ],
            'ranking': [
                'desc(policy_start_date)'
            ],
            'hitsPerPage': ITEMS_PER_PAGE,
        })

        self.create_or_update_replicas(
            policies_index_name,
            [
                {'field': 'policy_start_date', 'order': 'asc'},
                {'field': 'policy_expiry_date', 'order': 'asc'},
                {'field': 'policy_expiry_date', 'order': 'desc'},
            ]
        )

        self.stdout.write(f'\n>> Motor policies Index settings updated\n')

    def create_or_update_replicas(self, parent_index_name, replicas=None):
        if replicas is None:
            replicas = [
                {'field': 'created_on', 'order': 'asc'},
                {'field': 'updated_on', 'order': 'asc'},
                {'field': 'updated_on', 'order': 'desc'}
            ]

        # Creating replicas
        slaves = []
        for replica in replicas:
            slaves.append(f'{parent_index_name}_{replica["field"]}_{replica["order"]}')

        parent_index = self.algolia.get_index(parent_index_name)

        parent_index.set_settings({
            'replicas': slaves
        })

        # Updating ranking in replicas settings
        for replica in replicas:
            replica_name = f'{parent_index_name}_{replica["field"]}_{replica["order"]}'
            self.stdout.write(f'\n>> Creating/updating replica {replica_name}')

            replica_index = self.algolia.get_index(replica_name)

            replica_index.set_settings({
                'ranking': [f'{replica["order"]}({replica["field"]})']
            })
