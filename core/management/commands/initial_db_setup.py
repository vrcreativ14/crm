import subprocess

from django.contrib.auth.models import User
from django.core.management import BaseCommand, call_command

from accounts.models import UserProfile
from accounts.models import Company, CompanySettings, Domain
from motorinsurance_shared.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Resetting Postgres DB')
        subprocess.run(['dropdb', 'felix_platform'])
        subprocess.run(['createdb', 'felix_platform'])

        call_command('migrate_schemas', '--shared')
        call_command('load_mmt_tree', up_to=2017)

        self.stdout.write('Loading sample products.')
        call_command('load_sample_products')

        self.stdout.write('Creating company tenant, settings, domains, and user accounts.')
        company = Company.objects.create(country_code='AE', status=Company.STATUS_ACTIVE,
                                         name='Felix Broker', schema_name='felix')
        domain = Domain.objects.create(tenant=company, domain='127.0.0.1:8000')

        CompanySettings.objects.create(
            company=company,
            displayed_name='Felix Broker',
            email='admin@felix.insure',
            currency='AED'
        )

        company.activate()  # Setup tenant for the user profile we will create

        admin = User.objects.create_superuser('admin', 'admin@felix.insure', 'admin')
        UserProfile.objects.create(
            user=admin,
            company=company
        )

        for product in Product.objects.all():
            company.available_motor_insurance_products.add(product)
