import csv
import datetime

from django.core.management import BaseCommand

from accounts.models import Company
from motorinsurance.models import Deal


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            help='Starting date in YYYY-MM-DD format',
            required=True
        )
        parser.add_argument(
            '--end-date',
            help='Ending date in YYYY-MM-DD format',
            required=True
        )
        parser.add_argument(
            '--output',
            help='Output file name',
            required=True
        )

    def handle(self, *args, **options):
        start_date_str = options['start_date']
        end_date_str = options['end_date']

        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')

        self.stdout.write(
            f'Exporting data from {start_date} to {end_date}.'
        )

        output_file = open(options['output'], 'w')
        writer = csv.writer(output_file)
        writer.writerow([
            'Company Name', 'Date', 'Quote Reference', 'Car Year', 'Car Make', 'Car Model', 'Sum Insured'
        ])

        for company in Company.objects.filter(status=Company.STATUS_ACTIVE).exclude(schema_name='public'):
            company.activate()

            self.stdout.write(
                f'Exporting data for company {company.name}'
            )

            deals_to_consider = Deal.objects.filter(is_deleted=False, created_on__range=(start_date, end_date))
            for deal in deals_to_consider:
                if deal.quote:
                    quote = deal.quote
                    quoted_products = quote.get_active_quoted_products()

                    car_year = deal.car_year
                    car_make = deal.car_make.name
                    if deal.car_trim:
                        car_model = deal.car_trim.title
                    else:
                        car_model = deal.custom_car_name

                    for quoted_product in quoted_products:
                        date = quoted_product.created_on
                        sum_insured = quoted_product.insured_car_value or quote.insured_car_value

                        writer.writerow([
                            company.name, date.strftime('%Y-%m-%d'), quote.pk, car_year, car_make, car_model,
                            sum_insured
                        ])

        output_file.close()
