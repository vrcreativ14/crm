import datetime
from urllib.parse import urljoin
import logging

import requests

from django.conf import settings

from auto_quoter.auto_quoter_base import AutoQuoterBase
from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.utils import passes_common_auto_quoting_checks
from insurers.models import Insurer
from motorinsurance.models import Deal


class DroolsAutoQuoter(AutoQuoterBase):
    DATE_FORMAT = '%Y-%m-%d'

    def __init__(self):
        super(DroolsAutoQuoter, self).__init__()

        self.log = logging.getLogger('auto_quote.drools')
        self.api_url = settings.AUTO_QUOTERS['drools']

    @classmethod
    def license_age_choice_to_years(cls, license_age_text):
        return {
            "less than 6 months": 0,
            "less than 1 year": 0,
            "less than 2 years": 1,
            "more than 2 years": 2,
        }.get(license_age_text, 0)

    @classmethod
    def years_no_claims_choice_to_years(cls, no_claims_text):
        return dict([
            ("unknown", 0),
            ("never", 5),
            ("this year", 0),
            ("last year", 1),
            ("2 years ago", 2),
            ("3 years ago", 3),
            ("4 years ago", 4),
            ("5 years or more", 5),
        ])[no_claims_text]

    @classmethod
    def get_deal_missing_data_fields(cls, deal: Deal):
        """Returns a list of errors (if any) that prevent this deal from being auto quoted."""
        customer = deal.customer
        customer_profile = deal.customer.motorinsurancecustomerprofile

        missing_data_fields = []

        if not customer.dob:
            missing_data_fields.append('customer.dob')
        if not customer.gender:
            missing_data_fields.append('customer.gender')
        if not customer.nationality:
            missing_data_fields.append('customer.nationality')
        if not customer_profile.uae_license_age:
            missing_data_fields.append('customer_profile.uae_license_age')

        if deal.car_trim is None and not deal.custom_car_name:
            missing_data_fields.append('deal.custom_car_name')
        if not deal.current_insurance_type and deal.lead_type != 'new':
            missing_data_fields.append('deal.current_insurance_type')
        if not deal.date_of_first_registration and deal.lead_type != 'new':
            missing_data_fields.append('deal.date_of_first_registration')
        if not deal.place_of_registration:
            missing_data_fields.append('deal.place_of_registration')
        if not deal.vehicle_insured_value:
            missing_data_fields.append('deal.vehicle_insured_value')
        if not deal.years_without_claim:
            missing_data_fields.append('deal.years_without_claim')

        return missing_data_fields

    def get_quote_for_insurer_with_deal(self, insurer: Insurer, deal: Deal, form_data):
        """Because our rate book server works on a per product basis, we have to send it a request each for all possible
        products that can be auto quoted for this insurer for the current company.

        With the insurer APIs, a single request returns all possible products quoted for the active company. But our
        rate book server is pretty dumb, it just runs the rating logic for whichever product code you give it. It has
        no concept of companies or products assigned to companies, etc...

        To keep the same interface as the rest of the APIs, we have this smelly code in this one AutoQuoter so that all
        the other AutoQuoters can have a better interface."""
        company = deal.company
        available_products_for_insurer = company.get_motor_insurance_products().filter(insurer=insurer,
                                                                                       can_auto_quote=True)
        all_quotes = []
        for product in available_products_for_insurer:
            all_quotes += self.get_quote_for_product_with_deal(product, deal, form_data)

        return all_quotes

    def get_quote_for_product_with_deal(self, product, deal: Deal, form_data):
        product_code = product.code

        common_checks_passed, reason = passes_common_auto_quoting_checks(deal, form_data)
        if not common_checks_passed:
            return [{
                'name': product_code,
                'exception': True,
                'message': reason
            }]

        is_sports, is_suv = form_data['is_sports'], form_data['is_suv']

        if self.get_deal_missing_data_fields(deal):
            raise AutoQuoterException('Can not auto quote deal due to missing data')

        self.log.info(
            'Requesting quote from Drool Auto Quoter with product {}, deal id {}, sports {}, and suv {}'.format(
                product_code, deal.pk, is_sports, is_suv
            )
        )

        customer = deal.customer
        customer_profile = deal.customer.motorinsurancecustomerprofile

        person_data = {
            'dateOfBirth': customer.dob.strftime(self.DATE_FORMAT),
            'gender': customer.gender,
            'nationality': customer.nationality,
            'firstLicenseAge': self.license_age_choice_to_years(customer_profile.first_license_age),
            'uaeLicenseAge': self.license_age_choice_to_years(customer_profile.uae_license_age)
        }

        date_of_first_registration = deal.date_of_first_registration
        if date_of_first_registration is None:
            # Assume the car will be registered today. We do this because our Drools API expects a valid date for this
            # param
            date_of_first_registration = datetime.date.today()

        vehicle_data = {
            'manufactureYear': deal.car_year,
            'make': deal.car_make.name,
            'model': deal.car_trim.get_title_with_model() if deal.car_trim else deal.custom_car_name,
            'currentInsurer': deal.get_current_insurer_display(),
            'currentInsuranceType': deal.current_insurance_type,
            'dateOfFirstRegistration': date_of_first_registration.strftime(self.DATE_FORMAT),
            'placeOfRegistration': deal.place_of_registration,
            'insuredValue': float(deal.vehicle_insured_value),
            'yearsWithoutClaim': self.years_no_claims_choice_to_years(deal.years_without_claim),
            'claimsCertificateAvailable': False,  # For now we quote all products without looking at NCD
            'privateCar': deal.private_car,
            'unmodifiedCar': deal.car_unmodified,
            'gccSpecCar': deal.car_gcc_spec,
            'isSports': is_sports,
            'isSuv': is_suv,
        }

        request_dict = {
            'productCode': product_code,
            'person': person_data,
            'vehicle': vehicle_data
        }

        self.log.debug('Sending /get-quote request to Drools Auto Quoter with data {}'.format(request_dict))

        try:
            quotes_response = requests.post(urljoin(self.api_url, '/get-quote'), json=request_dict, timeout=30)
        except requests.Timeout:
            self.log.error('DroolsAutoQuoter: Request to Drools Auto Quoter timed out')
            raise AutoQuoterException('The API failed to respond. Please try later')

        try:
            quotes_response.raise_for_status()
        except requests.HTTPError as e:
            self.log.error('Error while trying to use Drool Auto Quoter. Error: {}'.format(e))
            if quotes_response.status_code == requests.codes.not_found:
                raise AutoQuoterException('Drools auto quoter not defined for product {}'.format(product_code))
            else:
                raise AutoQuoterException(str(e))
        else:
            quotes = quotes_response.json()
            self.log.debug('Received quotes from Drools Auto Quoter. Quotes: {}'.format(quotes))
            for quote in quotes:
                quote['premium'] = quote['premium'] * 1.05  # VAT
                quote['insuredCarValue'] = float(deal.vehicle_insured_value)
            return quotes
