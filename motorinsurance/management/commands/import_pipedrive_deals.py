import csv
import datetime

import pytz
import requests
from dateutil.relativedelta import relativedelta
from django.core.files.base import ContentFile
from django.core.management import BaseCommand, CommandError

from accounts.models import Company
from core.models import Attachment, Task
from customers.models import Customer
from felix.constants import COUNTRIES, EMIRATES_LIST
from motorinsurance.constants import LICENSE_AGE_LIST, LEAD_TYPES_OWN_CAR, TOP_TIER_INSURERS
from motorinsurance.models import CustomerProfile, Deal
from motorinsurance_shared.models import CarMake


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('company_id', type=int, help='Company Id for account to import data into.')
        parser.add_argument('in_file', type=str, help='CSV file to import.')
        parser.add_argument('--no-output', action='store_true', dest='no_output', help='Suppress debug logging output')
        parser.add_argument('--no-files', action='store_true', dest='no_files', help='Skip downloading files')

    def get_country_code_from_name(self, country_name):
        """Cleans and gets the country code for the given country name"""
        name_conversions = {
            'American': 'United States',
            'Indian': 'India',
            'Philipines': 'Philippines',
            'Iranian': 'Iran, Islamic Republic of',
            'Palestine': 'Palestine, State of',
            'Lithuanian': 'Lithuania',
            'British': 'United Kingdom',
            'UK': 'United Kingdom',
            'Emarati': 'United Arab Emirates',
            'UAE': 'United Arab Emirates',
        }
        country_name = name_conversions.get(country_name, country_name)

        reverse_countries = {
            country_pair[1]: country_pair[0]
            for country_pair in COUNTRIES
        }
        return reverse_countries[country_name]

    def get_license_age_code_from_label(self, license_age):
        transformations = {
            'More than 1 year': 'less than 2 years',
            'More than 2 yrs': 'more than 2 year',
            'More than 5 years': 'more than 2 years'
        }
        if license_age in transformations:
            return transformations[license_age]

        for k, v in LICENSE_AGE_LIST:
            if v.lower() == license_age.lower():
                return k

        raise ValueError(f'Unable to convert {license_age} to code')

    def get_emirate_code_from_name(self, emirate):
        for k, v in EMIRATES_LIST:
            if v.lower() == emirate.lower():
                return k

        raise ValueError(f'Unable to convert {emirate} to code')

    def handle(self, *args, **options):
        if options['no_output']:
            class NoOpOut:
                def write(self, msg):
                    pass

            self.stdout = NoOpOut()

        company_id = options['company_id']

        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            raise CommandError(f'Company with id {company_id} does not exist.')

        company.activate()

        with open(options['in_file'], 'r') as _if:
            reader = csv.reader(_if)
            next(reader)  # Skip header

            for row in reader:
                customer_name, customer_phones, customer_emails, customer_nationality, customer_dob = row[2:7]
                customer = Customer.objects.create(
                    company=company,

                    name=customer_name,
                    phone=customer_phones.split(',')[0].strip(),
                    email=customer_emails.split(',')[0].strip(),
                    dob=datetime.datetime.strptime(customer_dob, '%Y-%m-%d') if customer_dob else None,
                    nationality=self.get_country_code_from_name(customer_nationality) if customer_nationality else ''
                )
                self.stdout.write(f'Created customer {customer}.')

                (first_license_country, first_license_age, uae_license_age,
                 first_license_issue_date, uae_license_issue_date) = row[7:12]

                customer_profile = CustomerProfile.objects.create(
                    customer=customer,

                    first_license_age=self.get_license_age_code_from_label(
                        first_license_age) if first_license_age else '',
                    uae_license_age=self.get_license_age_code_from_label(uae_license_age) if uae_license_age else '',

                    first_license_country=self.get_country_code_from_name(
                        first_license_country) if first_license_country else '',
                    first_license_issue_date=datetime.datetime.strptime(first_license_issue_date,
                                                                        '%Y-%m-%d') if first_license_issue_date else None,
                    uae_license_issue_date=datetime.datetime.strptime(uae_license_issue_date,
                                                                      '%Y-%m-%d') if uae_license_issue_date else None,
                )
                self.stdout.write(f'Created customer profile {customer_profile}.')

                lead_type = LEAD_TYPES_OWN_CAR
                car_year, car_make_str, car_model_and_trim, car_value, emirate, insurance_type, insurer = row[14:21]

                car_value = car_value.strip().replace(',', '')
                try:
                    car_value = float(car_value)
                except (ValueError, TypeError):
                    self.stderr.write(f'Can not convert {car_value} into float. Assuming 0.')
                    car_value = 0.0

                try:
                    car_make = CarMake.objects.get(name__icontains=car_make_str)
                except CarMake.DoesNotExist:
                    self.stderr.write(f'Can not find make for name {car_make_str}.')
                    continue

                if insurance_type == 'Comprehensive':
                    insurance_type = 'comprehensive'
                else:
                    insurance_type = 'tpl'

                current_insurer = {
                    'Dar Al Takaful': 'dat',
                    'Dubai Insurance': 'di',
                    'Emirates Insurance': 'eic',
                    'Insurance House': 'ih',
                    'Oman Insurance': 'oic',
                    'Qatar Insurance': 'qic',
                    'RSA': 'rsa',
                }.get(insurer, 'other')

                deal = Deal.objects.create(
                    company=company,
                    customer=customer,
                    lead_type=lead_type,

                    car_year=car_year,
                    car_make=car_make,
                    custom_car_name=car_model_and_trim,
                    place_of_registration=self.get_emirate_code_from_name(emirate),
                    vehicle_insured_value=car_value,

                    current_insurance_type=insurance_type,
                    current_insurer=current_insurer
                )
                self.stdout.write(f'Created deal {deal}.')

                insurance_start_date = datetime.datetime.strptime(row[-1], '%Y-%m-%d').replace(
                    tzinfo=pytz.timezone('Asia/Dubai'))
                insurance_end_date = datetime.datetime.strptime(row[-2], '%Y-%m-%d').replace(
                    tzinfo=pytz.timezone('Asia/Dubai'))

                first_reminder_date = insurance_start_date + relativedelta(years=1, weeks=-2)
                Task.objects.create(attached_to=deal, title='Prepare Renewal Terms',
                                    due_datetime=first_reminder_date)

                second_reminder_date = insurance_end_date
                Task.objects.create(attached_to=deal, title='Insurance Policy Expiry Date',
                                    due_datetime=second_reminder_date)

                if options['no_files']:
                    continue

                deal_id = row[0]
                self.stdout.write(f'Downloading files for deal id {deal_id}.')

                api_token = '3396aa72dabd45927f51cb3086f9d1619616de63'
                files_resp = requests.get(f'http://myfelix.pipedrive.com/v1/deals/{deal_id}/files', params={
                    'api_token': api_token
                })
                try:
                    files_resp.raise_for_status()
                except requests.HTTPError:
                    self.stderr.write(f'Error while getting files for deal {deal_id}.')
                    continue

                files_json = files_resp.json()
                if not files_json['success']:
                    self.stderr.write(f'Error while getting files for deal {deal_id}.')
                    continue

                if files_json['data']:
                    for file_info in files_json['data']:
                        file_id = file_info['id']
                        file = requests.get(f'http://myfelix.pipedrive.com/v1/files/{file_id}/download', params={
                            'api_token': api_token
                        })

                        file_name = file_info['file_name']
                        attachment = Attachment(company=company, attached_to=customer, label=file_name)
                        attachment.file.save(file_name, ContentFile(file.content))
                        self.stdout.write(f'Downloaded attachment with file name {file_name}')
