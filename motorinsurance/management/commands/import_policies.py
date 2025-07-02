import datetime
import os
import pprint

import pandas as pd
from django.core.management import BaseCommand
from django.utils.text import slugify

from accounts.models import Company
from customers.models import Customer
from motorinsurance.constants import INSURANCE_TYPES
from motorinsurance.models import Policy, CustomerProfile
from motorinsurance_shared.models import CarTrim, CarMake, Product


class Command(BaseCommand):
    added_records = []
    skipped_records = []
    column_headers = {
        'policy-number': -1,
        'product': -1,
        'premium': -1,
        'deductible': -1,
        'customer-name': -1,
        'customer-phone': -1,
        'customer-email': -1,
        'car-year': -1,
        'car-make': -1,
        'car-modeltrim': -1,
        'sum-insured': -1,
        'policy-type': -1,
        'policy-start-date': -1,
        'policy-expiry-date': -1,
        'owner-id': -1,
    }

    def add_arguments(self, parser):
        parser.add_argument('-c', '--company_id', type=int, help='import policies for the specified company only')
        parser.add_argument('-f', '--file', type=str, help='CSV file to import.')
        parser.add_argument('-t', '--trim-id', type=str, help='Default trim to use if none found.', default=17120)

    def handle(self, *args, **options):
        company_id = options['company_id']
        file_path = options['file']

        try:
            company = Company.objects.get(pk=company_id)
            self.stdout.write(f'Importing policies to company {company.name}')
        except Company.DoesNotExist:
            self.stderr.write(f'Company with id {company_id} not found.')
            return

        company.activate()

        if not os.path.exists(file_path):
            self.stdout.write(f'File [{file_path}] does not exists')
            return

        data = pd.read_csv(file_path)

        # checking and setting the column placements (indexes) eg: Customer Name column # in the csv etc.
        for key, column in enumerate(data.columns):
            slugified_column = slugify(column)
            if slugified_column in self.column_headers:
                self.column_headers[slugified_column] = key

        print("Here are the matched columns:")
        pprint.pprint(self.column_headers)
        if input("Do you want to continue? (yes/no)") == "no":
            return

        NotSelectedCarTrim = CarTrim.objects.get(pk=options['trim_id'])  # Not Selected car trim

        # Parsing rows
        for record in data.values:
            # get all required fields first and make sure all available
            customer_name = self.get_item('customer-name', record)
            policy_number = self.get_item('policy-number', record)
            start_date = self.get_item('policy-start-date', record)
            expiry_date = self.get_item('policy-expiry-date', record)

            if not all([customer_name, policy_number, start_date, expiry_date]):
                self.stdout.write(f'\n\n >>>>> One or more required fields are missing. Skipping record {record}\n\n')
                self.skipped_records.append(record)
                continue

            customer_email = self.get_item('customer-email', record)
            customer_phone = self.get_item('customer-phone', record)

            premium = self.get_item('premium', record)
            deductible = self.get_item('deductible', record)

            car_year = self.get_item('car-year', record)
            car_make = self.get_item('car-make', record)
            car_modeltrim = self.get_item('car-modeltrim', record)

            try:
                make = CarMake.objects.get(name__iexact=car_make)
                self.stdout.write(f"Matching to make {make.name}")
            except CarMake.DoesNotExist:
                make = NotSelectedCarTrim.model.make

            car_make = make
            if car_year:
                car_year = str(int(car_year))  # Pandas reads this as a float
            else:
                car_year = NotSelectedCarTrim.year
            if not car_modeltrim:
                car_modeltrim = NotSelectedCarTrim.get_title_with_model()

            sum_insured = self.get_item('sum-insured', record)
            policy_type = self.get_item('policy-type', record)

            if start_date:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

            if expiry_date:
                expiry_date = datetime.datetime.strptime(expiry_date, '%Y-%m-%d')

            customer, created = Customer.objects.get_or_create(
                name=customer_name,
                email=customer_email,
                phone=str(customer_phone),
                defaults={'company': company}
            )

            if created:
                customer_profile = CustomerProfile.objects.create(
                    customer=customer
                )

            policy = Policy(
                company=company,
                customer=customer,
                reference_number=policy_number,
                policy_start_date=start_date,
                policy_expiry_date=expiry_date,

                car_year=car_year,
                car_make=car_make,
                custom_car_name='{} {} {}'.format(car_year, car_make, car_modeltrim),

                premium=self.get_float(premium),
                deductible=self.get_float(deductible),
                insured_car_value=self.get_float(sum_insured),
                default_add_ons=[],
                paid_add_ons=[]
            )

            policy_type = {
                'Motor Comprehensive': 'comprehensive',
                'Motor Third Party': 'tpl'
            }.get(policy_type, policy_type)
            if policy_type and len([item for item in INSURANCE_TYPES if item[0] == policy_type]):
                policy.insurance_type = policy_type

            product_code_or_name = self.get_item('product', record)
            try:
                product = Product.objects.get(code=product_code_or_name)
                policy.product = product
            except Product.DoesNotExist:
                policy.custom_product_name = product_code_or_name

            owner_id = self.get_item('owner-id', record)
            if owner_id:
                policy.owner_id = owner_id

            policy.save()
            self.stdout.write(f'\n\n *** NEW Policy record created for customer [{customer_name}]\n')
            self.added_records.append(record)

        self.stdout.write(f'\n\n + +++ + {len(self.added_records)} Record(s) Added \n')
        print(self.added_records)
        self.stdout.write(f'\n\n - --- - {len(self.skipped_records)} Record(s) Skipped \n')
        print(self.skipped_records)

    def get_float(self, val):
        if val and type(val) is str:
            val = float(val.replace(',', ''))

        return val or 0

    def get_item(self, key, record):
        if self.column_headers[key] > -1:
            r = record[self.column_headers[key]]

            return '' if str(r) == 'nan' else r

        return ''
