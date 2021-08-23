from auto_quoter.utils import passes_common_auto_quoting_checks
from motorinsurance.constants import INSURANCE_TYPE_COMPREHENSIVE
from motorinsurance.helpers import is_ncd_more_than, is_license_age_more_than

from auto_quoter.uic import car_exclusions


class UICRateBookBase:
    PRODUCT_NAME = None
    RATES_TABLE = None
    AGENCY_REPAIR_LOADING_TABLE = None

    def generate_name_for_product_we_cant_quote(self, deal, form_data, postfix=''):
        return 'Union Insurance {}{}'.format(self.PRODUCT_NAME, postfix)

    def assert_base_conditions_met(self, deal, form_data):
        """A safeguard method that is used to ensure that we do not generate a quote if the provided data is outside
        of the scope of the UIC rate book we are digitizing.

        It is the job of the caller of this class to ensure that any in-valid data is handled before the methods in this
        class are called."""
        assert self.can_generate_quote(deal, form_data)

    def can_generate_quote(self, deal, form_data):
        common_checks_passed, reason = passes_common_auto_quoting_checks(deal, form_data)
        if not common_checks_passed:
            return False, reason

        if car_exclusions.is_car_excluded(deal):
            return False, 'This make/model needs approval from Union Insurance'
        if car_exclusions.is_car_black_listed(deal):
            return False, 'This make/model is black listed from Union Insurance'

        if form_data['vehicle_type'] not in ['saloon', 'station_wagon', 'sports']:
            return False, 'This plan is not available for this type of vehicle'

        if form_data['insured_value'] > 500000:
            return False, 'This plan is not available for vehicles valued above Dhs 500K.'

        if not deal.customer.is_older_than(18):
            return False, 'This plan is not available for drivers younger than 18 years.'

        if not deal.private_car:
            return False, 'This plan is not available for commercial vehicles.'

        if not deal.car_unmodified:
            return False, 'This plan is not available for modified vehicles.'

        if not deal.car_gcc_spec:
            return False, 'This plan is not available for non-GCC spec vehicles.'

        return True, None

    def get_price_bracket(self, deal, form_data):
        insured_value = form_data['insured_value']

        price_bracket = None

        if insured_value <= 70000:
            price_bracket = '0 - 70K'
        elif insured_value <= 150000:
            price_bracket = '70K - 150K'
        elif insured_value <= 500000:
            price_bracket = '150K - 500K'

        return price_bracket

    def get_deductible(self, deal, form_data):
        insured_value = form_data['insured_value']
        if insured_value <= 50000:
            return 350
        elif insured_value <= 100000:
            return 500
        elif insured_value <= 250000:
            return 750
        elif insured_value <= 500000:
            return 1000

    def get_ncd_discount(self, deal):
        if not deal.claim_certificate_available:
            return 0.0

        if is_ncd_more_than(deal.years_without_claim, 3):
            return 10.0
        elif is_ncd_more_than(deal.years_without_claim, 2):
            return 7.5
        elif is_ncd_more_than(deal.years_without_claim, 1):
            return 5.0

        return 0.0

    def get_discounted_minimum_premium(self, deal, form_data, minimum_premium):
        if form_data['vehicle_type'] != 'station_wagon':
            return minimum_premium

        if deal.claim_certificate_available and is_ncd_more_than(deal.years_without_claim, 1):
            return minimum_premium - (minimum_premium * (10.0/100))

        return minimum_premium

    def maximum_rate_applicable(self, deal):
        customer = deal.customer

        if not customer.is_older_than(25):
            return True

        customer_profile = customer.motorinsurancecustomerprofile
        if not (is_license_age_more_than(customer_profile.uae_license_age, 12) or
                is_license_age_more_than(customer_profile.first_license_age, 12)):
            return True

        return False

    def get_non_agency_premium(self, deal, form_data):
        price_bracket = self.get_price_bracket(deal, form_data)
        if price_bracket is None:
            raise ValueError('Unable to find correct price bracket in UICStandardRateBook')

        vehicle_type = form_data['vehicle_type']
        price_bracket_rates = self.RATES_TABLE[price_bracket]

        rate = price_bracket_rates['garage'][vehicle_type]['rate']
        if self.maximum_rate_applicable(deal):
            rate = 5.0

        minimum_premium = price_bracket_rates['garage'][vehicle_type]['min']
        minimum_premium = self.get_discounted_minimum_premium(deal, form_data, minimum_premium)

        calculated_premium = (rate / 100.0) * form_data['insured_value']
        no_claims_discount = self.get_ncd_discount(deal)
        if no_claims_discount > 0:
            calculated_premium = calculated_premium - (calculated_premium * (no_claims_discount / 100.0))

        premium = max(minimum_premium, calculated_premium)

        return premium

    def can_quote_agency(self, deal, form_data):
        if not deal.is_new_car() and not deal.current_insurance_type == INSURANCE_TYPE_COMPREHENSIVE:
            return False, 'This plan is not available for vehicles whose current cover is not comprehensive insurance.'

        if not deal.is_new_car() and not form_data['previous_repair_condition_is_agency']:
            return False, 'This plan is not available if the previous year repair condition was not agency repair.'

        car_age = deal.get_age_of_car_since_registration()
        insured_value = form_data['insured_value']

        if insured_value <= 70000 and car_age > 2:
            return False, 'This plan is not available for vehicles older than 3 years and valued below Dhs 70K'
        elif car_age > 5:
            return False, 'This plan is not available for vehicles older than 5 years'

        if car_age == 2 and not (is_ncd_more_than(deal.years_without_claim, 1) and deal.claim_certificate_available):
            return False, 'This plan requires a 1 year no claim letter'
        elif car_age == 3 and not (is_ncd_more_than(deal.years_without_claim, 2) and deal.claim_certificate_available):
            return False, 'This plan requires a 2 year no claim letter'
        elif car_age == 4 and not (is_ncd_more_than(deal.years_without_claim, 3) and deal.claim_certificate_available):
            return False, 'This plan requires a 3 year no claim letter'
        elif car_age == 5 and not (is_ncd_more_than(deal.years_without_claim, 3) and deal.claim_certificate_available):
            return False, 'This plan requires a 3 year no claim letter'

        return True, ''

    def get_agency_premium(self, deal, form_data):
        car_age = deal.get_age_of_car_since_registration()
        insured_value = form_data['insured_value']

        assert car_age <= 5
        assert car_age <= 2 or insured_value > 70000

        price_bracket = self.get_price_bracket(deal, form_data)
        if price_bracket is None:
            raise ValueError('Unable to find correct price bracket in UICStandardRateBook')

        vehicle_type = form_data['vehicle_type']
        price_bracket_rates = self.RATES_TABLE[price_bracket]

        rate = price_bracket_rates['agency'][vehicle_type]['rate']
        if self.maximum_rate_applicable(deal):
            rate = 5.0

        minimum_premium = price_bracket_rates['agency'][vehicle_type]['min']

        calculated_premium = (rate / 100.0) * insured_value

        no_claims_discount = self.get_ncd_discount(deal)
        if no_claims_discount > 0:
            calculated_premium = calculated_premium - (calculated_premium * (no_claims_discount / 100.0))

        agency_repair_loading = self.AGENCY_REPAIR_LOADING_TABLE[price_bracket][car_age]

        minimum_premium = minimum_premium + (minimum_premium * (agency_repair_loading / 100.0))
        calculated_premium = calculated_premium + (calculated_premium * (agency_repair_loading / 100.0))

        premium = max(minimum_premium, calculated_premium)

        return premium

    def add_taxes(self, amount):
        """Adds any applicable taxes. Right now it's only VAT"""
        return amount * 1.05

    def get_product_name(self, deal, form_data):
        if form_data['insured_value'] <= 70000:
            return self.PRODUCT_NAME
        else:
            return f'{self.PRODUCT_NAME} ABOVE 70K'

    def get_quotes(self, deal, form_data):
        self.assert_base_conditions_met(deal, form_data)

        insured_value = form_data['insured_value']

        non_agency_premium = self.get_non_agency_premium(deal, form_data)
        non_agency_premium = self.add_taxes(non_agency_premium)

        non_agency_quote = {
            'productCode': self.get_product_name(deal, form_data),
            'quoteReference': '',
            'insuredCarValue': insured_value,
            'canInsure': True,
            'referralRequired': False,
            'agencyRepair': False,
            'ncd': self.get_ncd_discount(deal) > 0.0,
            'premium': non_agency_premium,
            'deductible': self.get_deductible(deal, form_data),
            'rulesTrace': ['Generated by rate book']
        }

        agency_product_name_if_not_quotable = self.generate_name_for_product_we_cant_quote(deal, form_data, ' (Agency)')
        can_quote_agency, reason = self.can_quote_agency(deal, form_data)
        if not can_quote_agency:
            return [non_agency_quote, {
                'name': agency_product_name_if_not_quotable,
                'exception': True,
                'message': reason
            }]

        agency_premium = self.get_agency_premium(deal, form_data)
        agency_premium = self.add_taxes(agency_premium)

        car_age = deal.get_age_of_car_since_registration()
        ncd_certificate_required_for_quote = self.get_ncd_discount(deal) > 0.0
        if car_age > 1:
            ncd_certificate_required_for_quote = True  # Required if car is older than 1 year

        agency_quote = {
            'productCode': self.get_product_name(deal, form_data),
            'quoteReference': '',
            'insuredCarValue': insured_value,
            'canInsure': True,
            'referralRequired': False,
            'agencyRepair': True,
            'ncd': ncd_certificate_required_for_quote,
            'premium': agency_premium,
            'deductible': self.get_deductible(deal, form_data),
            'rulesTrace': ['Generated by rate book']
        }

        return [non_agency_quote, agency_quote]
