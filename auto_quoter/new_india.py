import logging

from auto_quoter.auto_quoter_base import AutoQuoterBase
from auto_quoter.constants import NewIndiaVehicleTypes
from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.models import AutoQuoterConfig
from auto_quoter.utils import passes_common_auto_quoting_checks
from motorinsurance.constants import INSURANCE_TYPE_COMPREHENSIVE
from motorinsurance.helpers import is_license_age_more_than, is_ncd_more_than


class NewIndiaRatebookBase:
    def can_quote(self, deal, form_data):
        common_checks_passed, reason = passes_common_auto_quoting_checks(deal, form_data)
        if not common_checks_passed:
            return False, reason

        age_of_car = deal.get_age_of_car_since_registration()

        if age_of_car > 10:
            return False, 'Can not insure cars older than 10 years'

        if deal.car_make.name == 'Mazda':
            return False, 'Can not insure Mazda make cars'

        if not deal.is_new_car() and deal.current_insurance_type != INSURANCE_TYPE_COMPREHENSIVE:
            return False, 'Can not convert a previous TPL insurance to a New India comprehensive one'

        if deal.private_car:
            customer = deal.customer
            profile = customer.motorinsurancecustomerprofile

            if not is_license_age_more_than(profile.uae_license_age, 12):
                return False, 'Can not insure someone with a UAE license younger than 1 year'

            if not customer.is_older_than(25):
                return False, 'Can not insure someone younger than 25 years old'

        if form_data['is_chinese_manufacturer']:
            return False, 'Can not insure Chinese manufacturer cars'

        insured_value = form_data['insured_value']
        if insured_value > 250000:
            return False, 'Can not insure cars valued higher than 250K AED'

        vehicle_type = form_data['vehicle_type']
        number_of_passengers = deal.number_of_passengers

        if vehicle_type == NewIndiaVehicleTypes.Sports:
            return False, 'Can not insure sports, coupes, or high performance vehicles'
        elif vehicle_type == NewIndiaVehicleTypes.Saloon and number_of_passengers > 4:
            return False, 'Number of passengers can not exceed 4 for a vehicle of this kind'
        elif vehicle_type == NewIndiaVehicleTypes.FourByFour and number_of_passengers > 6:
            return False, 'Number of passengers can not exceed 6 for a vehicle of this kind'

        return True, None

    def can_quote_agency(self, deal, form_data):
        age_of_car = deal.get_age_of_car_since_registration()
        vehicle_type = form_data['vehicle_type']

        if deal.car_make.name == 'Mitsubishi':
            return False, 'Can not provide agency repair quote for Mitsubishi cars'
        elif age_of_car > 2:
            return False, 'Can not provide agency repair quote for cars older than 2 years'
        elif age_of_car > 1:
            if not deal.claim_certificate_available or not is_ncd_more_than(deal.years_without_claim, 1):
                return False, 'No claims certificate or self-declaration needed for 2nd year agency repair'

            if vehicle_type in [NewIndiaVehicleTypes.Pickups3TonsOrLess, NewIndiaVehicleTypes.Pickups3TonsOrMore,
                                NewIndiaVehicleTypes.PrivateBus, NewIndiaVehicleTypes.SchoolBus,
                                NewIndiaVehicleTypes.PassengerTransport]:
                return False, 'Can not quote a vehicle of this type for 2nd year agency repair'

        return True, None


class NewIndiaAutoQuoter(AutoQuoterBase):
    def __init__(self):
        super().__init__()

        self.rate_book = None
        self.log = logging.getLogger('auto_quoter.new_india')

    def get_product_code_for_scheme_name(self, scheme_name):
        try:
            return self.config['mapping'][scheme_name]
        except KeyError:
            return None

    def setup_for_company(self, company):
        self.log.debug('NewIndiaAutoQuoter: Setting up self for company %s', company.name)
        self.company = company
        try:
            self.config = AutoQuoterConfig.objects.get(company=company, insurer='new india').get_options_dict()
        except AutoQuoterConfig.DoesNotExist:
            raise AutoQuoterException('The New India auto quoter is not configured')

        self.rate_book = {
        }[self.config['ratebook']]()

    def get_deal_missing_data_fields(self, deal):
        missing_data_fields = []

        if deal.date_of_first_registration is None:
            missing_data_fields.append('deal.date_of_first_registration')

        if not deal.current_insurance_type and not deal.is_new_car():
            missing_data_fields.append('deal.current_insurance_type')

        if deal.private_car:
            customer = deal.customer
            profile = customer.motorinsurancecustomerprofile

            if not profile.uae_license_age:
                missing_data_fields.append('customer_profile.uae_license_age')

            if not customer.dob:
                missing_data_fields.append('customer.dob')

        return missing_data_fields

    def get_deductible(self, deal, form_data):
        insured_value = form_data['insured_value']

        if insured_value <= 50000:
            deductible = 250
        elif insured_value <= 100000:
            deductible = 350
        elif insured_value <= 250000:
            deductible = 500
        else:
            deductible = 1000

        return deductible

    def get_quote_for_insurer_with_deal(self, insurer, deal, form_data):
        """Response data format:
            {
                'productCode': Our Product Code,
                'quoteReference': Ref. No,
                'insuredCarValue': Insured Value,
                'canInsure': True/False,
                'referralRequired': True/False,
                'agencyRepair': True/False,
                'premium': Premium,
                'deductible': Deductible,
                'rulesTrace': Array of strings with info on how quote was generated
            }
        """
        self.setup_for_company(deal.company)

        can_quote, reason = self.rate_book.can_quote(deal, form_data)
        if not can_quote:
            return [{
                'name': 'New India',
                'exception': True,
                'message': reason
            }]

        insured_value = form_data['insured_value']

        quotes = []

        non_agency_premium = self.rate_book.get_non_agency_premium(deal, form_data)
        non_agency_premium = non_agency_premium * 1.05  # VAT

        non_agency_product_code_base = 'NEW INDIA NON AGENCY'
        if not deal.private_car:
            non_agency_product_code_base = 'NEW INDIA NON AGENCY COMMERCIAL'

        non_agency_product_code = self.get_product_code_for_scheme_name(non_agency_product_code_base)
        if non_agency_product_code is None:
            self.log.warning('NewIndiaAutoQuoter: Unable to map scheme name "%s" to a product in '
                             'our DB. Please check auto quoter configuration for New India and company %s',
                             non_agency_product_code_base, deal.company.name)
        else:
            quotes.append({
                'productCode': non_agency_product_code,
                'quoteReference': '',
                'insuredCarValue': insured_value,
                'canInsure': True,
                'referralRequired': False,
                'agencyRepair': False,
                'premium': non_agency_premium,
                'deductible': self.get_deductible(deal, form_data),
                'rulesTrace': ['Generated using rate book']
            })

        agency_product_code_base = 'NEW INDIA AGENCY'
        if not deal.private_car:
            agency_product_code_base = 'NEW INDIA AGENCY COMMERCIAL'

        can_quote_agency, reason = self.rate_book.can_quote_agency(deal, form_data)
        if can_quote_agency:
            agency_premium = self.rate_book.get_agency_premium(deal, form_data)
            agency_premium = agency_premium * 1.05  # VAT

            agency_product_code = self.get_product_code_for_scheme_name(agency_product_code_base)
            if agency_product_code is None:
                self.log.warning('NewIndiaAutoQuoter: Unable to map scheme name "%s" to a product in '
                                 'our DB. Please check auto quoter configuration for New India and company %s',
                                 agency_product_code_base, deal.company.name)
            else:
                quotes.append({
                    'productCode': agency_product_code,
                    'quoteReference': '',
                    'insuredCarValue': insured_value,
                    'canInsure': True,
                    'referralRequired': False,
                    'agencyRepair': True,
                    'premium': agency_premium,
                    'deductible': self.get_deductible(deal, form_data),
                    'rulesTrace': ['Generated using rate book']
                })
        else:
            quotes.append({
                'name': 'New India Agency',
                'exception': True,
                'message': reason
            })

        return quotes
