import csv

from django.core.management import BaseCommand

from accounts.models import Company
from motorinsurance.models import Deal


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'company_id', type=int
        )
        parser.add_argument(
            'out', type=str, help='Path to output CSV file'
        )

    def handle(self, *args, **options):
        company_id = options['company_id']
        try:
            company = Company.objects.get(pk=company_id)
            self.stdout.write(f'Generating deals report for company {company.name}')
        except Company.DoesNotExist:
            self.stderr.write(f'Company with id {company_id} not found.')
            return

        company.activate()

        of = open(options['out'], 'w')
        self.stdout.write(f'Writing output to {of.name}.')
        w = csv.writer(of)
        w.writerow(
            ['Name', 'Phone', 'Email', 'Nationality', 'Gender', 'DOB', 'UAE License Age', 'Vehicle', 'Sum Insured',
             'First Registration Date', 'Emirate of Registration', 'Current Insurer', 'Current Cover',
             'Deal Created Date', 'Deal Stage', 'Deal Status', 'Deal Source']
        )

        deals = Deal.objects.filter(company=company, is_deleted=False)
        for deal in deals:
            customer = deal.customer
            customer_profile = customer.motorinsurancecustomerprofile
            lead = deal.lead

            row = [customer.name or 'NULL', customer.phone or 'NULL', customer.email or 'NULL',
                   (customer.nationality and customer.get_nationality_display()) or 'NULL',
                   (customer.gender and customer.get_gender_display()) or 'NULL',
                   (customer.dob and customer.dob.strftime('%Y-%m-%d')) or 'NULL',
                   (customer_profile.uae_license_age and customer_profile.get_uae_license_age_display()) or 'NULL',
                   (deal.car_make and deal.get_car_title()) or 'NULL', deal.vehicle_insured_value,
                   (deal.date_of_first_registration and deal.date_of_first_registration.strftime('%m-%Y')) or 'NULL',
                   (deal.place_of_registration and deal.get_place_of_registration_display()) or 'NULL',
                   (deal.current_insurer and deal.get_current_insurer_display()) or 'NULL',
                   (deal.current_insurance_type and deal.get_current_insurance_type_display()) or 'NULL',
                   deal.created_on.strftime('%Y-%m-%d'),
                   deal.get_stage_display(),
                   ', '.join(deal.get_tags())]

            if lead and lead.meta_info and 'utm_source' in lead.meta_info:
                row.append(lead.meta_info['utm_source'])
            else:
                row.append('NR')

            w.writerow(row)