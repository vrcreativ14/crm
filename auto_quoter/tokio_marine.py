import logging

from auto_quoter.auto_quoter_base import AutoQuoterBase
from auto_quoter.constants import TokioMarineVehicleTypes
from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.models import AutoQuoterConfig
from auto_quoter.utils import passes_common_auto_quoting_checks
from motorinsurance.constants import INSURER_TOKIO
from motorinsurance.helpers import is_license_age_more_than, is_ncd_more_than


class TokioMarineRateBookBase:
    smart_plus_name = None
    must_name = None

    def can_quote_any(self, deal, form_data):
        common_checks_passed, reason = passes_common_auto_quoting_checks(deal, form_data)
        if not common_checks_passed:
            return False, reason

        if deal.private_car:
            customer = deal.customer
            profile = customer.motorinsurancecustomerprofile

            if not customer.is_older_than(25):
                return False, 'Can not quote for driver younger than 25 years'
            if customer.is_older_than(65):
                return False, 'Can not quote for driver older than 65 years'

            if not is_license_age_more_than(profile.uae_license_age, 12):
                raise AutoQuoterException('Can not insure someone with a UAE license younger than 1 year')

        if deal.get_age_of_car_since_registration() > 8:
            return False, 'Can not quote a vehicle bought more than 8 years ago'

        if form_data['insured_value'] < 10000:
            return False, 'Can not quote vehicles worth less than AED 10,000'
        if form_data['insured_value'] > 400000:
            return False, 'Can not quote vehicles worth more than AED 400,000'

        return True, None

    def can_quote_smart_plus(self, deal, form_data):
        if form_data['vehicle_type'] not in [TokioMarineVehicleTypes.Saloon, TokioMarineVehicleTypes.FourByFour]:
            return False, 'This plan is not available for this type of vehicle'

        if form_data['vehicle_type'] == TokioMarineVehicleTypes.Saloon and form_data['insured_value'] < 80000:
            return False, 'The premiums for this vehicle type must be generated through the Tokio Marine portal'

        if deal.get_age_of_car_since_registration() > 3:
            return False, 'This plan is not available for vehicles older than 3 years'

        if not deal.is_new_car() and not (deal.has_no_claims_history() and deal.claim_certificate_available):
            return False, 'This plan requires a 1 year no claim letter'

        return True, None

    def can_quote_must(self, deal, form_data):
        if form_data['vehicle_type'] not in [TokioMarineVehicleTypes.Saloon, TokioMarineVehicleTypes.FourByFour]:
            return False, 'Can not quote a vehicle of this type'

        return True, None


class TokioMarineRateBookNexus(TokioMarineRateBookBase):
    smart_plus_name = 'Tokio Marine Smart Plus Plan (Agency)'
    must_name = 'Tokio Marine Must Ramadan Scheme (Non-Agency)'

    def can_quote_any(self, deal, form_data):
        common_checks_passed, reason = passes_common_auto_quoting_checks(deal, form_data)
        if not common_checks_passed:
            return False, reason

        if deal.private_car:
            customer = deal.customer
            profile = customer.motorinsurancecustomerprofile

            if not customer.is_older_than(25):
                return False, 'This plan is only available for drivers between the ages of 25 and 65'
            if customer.is_older_than(65):
                return False, 'This plan is only available for drivers between the ages of 25 and 65'

            if not is_license_age_more_than(profile.uae_license_age, 12):
                return False, 'This plan is not available to drivers with a UAE license less than 1 year'

        if form_data['vehicle_type'] == TokioMarineVehicleTypes.Saloon:
            max_car_age = 12
        elif form_data['vehicle_type'] == TokioMarineVehicleTypes.FourByFour:
            max_car_age = 13
        else:
            max_car_age = 10

        if deal.get_age_of_car_since_registration() > max_car_age:
            return False, 'This plan is not available for vehicles older than {} years'.format(max_car_age)

        if form_data['insured_value'] < 10000:
            return False, 'Can not quote vehicles worth less than AED 10,000'
        if form_data['insured_value'] > 400000:
            return False, 'Can not quote vehicles worth more than AED 400,000'

        return True, None

    def can_quote_smart_plus(self, deal, form_data):
        if form_data['vehicle_type'] == TokioMarineVehicleTypes.Saloon:
            return False, 'The premiums for this vehicle type must be generated through the Tokio Marine portal'

        can_quote, reason = super().can_quote_smart_plus(deal, form_data)
        if not can_quote:
            return can_quote, reason

        if not (10000 <= form_data['insured_value'] <= 400000):
            return False, 'Can only quote vehicles between 10K & 400K in value.'

        return True, None

    def get_smart_plus_quote(self, deal, form_data):
        vehicle_value = form_data['insured_value']
        vehicle_type = form_data['vehicle_type']

        if form_data['is_renewal']:
            rate = 2.25 if deal.get_age_of_car_since_registration() <= 2 else 2.70
            minimum_premium = 2300
        else:
            rate = 2.48 if deal.get_age_of_car_since_registration() <= 2 else 2.97
            minimum_premium = 2530

        if vehicle_type == TokioMarineVehicleTypes.FourByFour and vehicle_value <= 100000:
            deductible = 350
        elif vehicle_type == TokioMarineVehicleTypes.FourByFour and vehicle_value <= 400000:
            deductible = 500

        calculated_premium = (rate / 100.0) * vehicle_value
        premium = max(minimum_premium, calculated_premium)
        premium = premium * 1.05  # +VAT

        return {
            'productCode': 'Smart Plus',
            'quoteReference': '',
            'insuredCarValue': vehicle_value,
            'canInsure': True,
            'referralRequired': False,
            'agencyRepair': True,
            'premium': premium,
            'deductible': deductible,
            'rulesTrace': ['Generated using rate book']
        }

    def can_quote_must(self, deal, form_data):
        if form_data['vehicle_type'] == TokioMarineVehicleTypes.Bus and deal.number_of_passengers > 33:
            return False, 'Can not quote a bus with more than 33 passengers'

        # Base can_quote_must only allows saloons and 4x4s. Nexus can quote all car types
        return True, None

    def get_must_quote(self, deal, form_data):
        vehicle_value = form_data['insured_value']
        vehicle_type = form_data['vehicle_type']
        is_commercial = vehicle_type in [TokioMarineVehicleTypes.Pickups3TonsOrMore,
                                         TokioMarineVehicleTypes.Pickups3TonsOrLess,
                                         TokioMarineVehicleTypes.Bus]

        if vehicle_type == TokioMarineVehicleTypes.Saloon:

            rate = 2.45
            minimum_premium = 1300
            deductible = 250 if vehicle_value <= 150000 else 500

        elif vehicle_type == TokioMarineVehicleTypes.FourByFour:

            rate = 2.15
            minimum_premium = 2000
            deductible = 350 if vehicle_value <= 100000 else 500

        elif vehicle_type == TokioMarineVehicleTypes.Pickups3TonsOrLess:

            rate = 2.25
            minimum_premium = 1550
            deductible = 500

        elif vehicle_type == TokioMarineVehicleTypes.Pickups3TonsOrMore:

            rate = 2.25
            minimum_premium = 2000
            deductible = 500

        elif vehicle_type == TokioMarineVehicleTypes.Bus:

            rate = 2.25
            num_passengers = deal.number_of_passengers
            if num_passengers <= 15:
                minimum_premium = 1900
            elif num_passengers <= 26:
                minimum_premium = 2350
            elif num_passengers <= 33:
                minimum_premium = 2400

            deductible = 500

        calculated_premium = (rate / 100.0) * vehicle_value
        premium = max(minimum_premium, calculated_premium)

        is_renewal = form_data['is_renewal']
        ncd_discount = 0.0
        if not is_commercial:
            if is_renewal:
                ncd_discount = 10.0  # Loyalty discount

            if is_ncd_more_than(deal.years_without_claim, 1):
                ncd_discount = 20.0 if is_renewal else 10.0

            if is_ncd_more_than(deal.years_without_claim, 2):
                ncd_discount = 25.0 if is_renewal else 15.0

            if is_ncd_more_than(deal.years_without_claim, 3):
                ncd_discount = 30.0 if is_renewal else 20.0
        else:  # Commercial
            if is_renewal:
                ncd_discount = 10.0  # Loyalty discount

            if deal.claim_certificate_available:
                if is_ncd_more_than(deal.years_without_claim, 1):
                    ncd_discount = 20.0 if is_renewal else 10.0

                if is_ncd_more_than(deal.years_without_claim, 2):
                    ncd_discount = 25.0 if is_renewal else 15.0

                if is_ncd_more_than(deal.years_without_claim, 3):
                    ncd_discount = 30.0 if is_renewal else 20.0
            else:
                # Only 10% discount available without a no claims certificate
                if is_ncd_more_than(deal.years_without_claim, 1):
                    ncd_discount = 10.0

        premium = premium - (premium * (ncd_discount / 100.0))

        if is_commercial:
            premium = premium + 120 + deal.number_of_passengers * 30  # PAB driver and passenger required on commercial

        premium = premium * 1.05  # +VAT

        return {
            'productCode': 'Must Commercial' if is_commercial else 'Must',
            'quoteReference': '',
            'insuredCarValue': vehicle_value,
            'canInsure': True,
            'referralRequired': False,
            'agencyRepair': False,
            'premium': premium,
            'deductible': deductible,
            'rulesTrace': ['Generated using rate book']
        }


class TokioMarineAutoQuoter(AutoQuoterBase):
    def __init__(self):
        super(TokioMarineAutoQuoter, self).__init__()

        self.log = logging.getLogger('auto_quote.tokio_marine')
        self.rate_book = None

    def setup_for_company(self, company):
        self.log.debug('TokioMarineAutoQuoter: Setting up self for company %s', company.name)
        self.company = company
        try:
            self.config = AutoQuoterConfig.objects.get(company=company, insurer='tokio marine').get_options_dict()
        except AutoQuoterConfig.DoesNotExist:
            raise AutoQuoterException('The Tokio Marine auto quoter is not configured')

        self.rate_book = {
            'nexus': TokioMarineRateBookNexus,
        }[self.config['ratebook']]()

    def get_deal_missing_data_fields(self, deal):
        missing_data_fields = []

        if deal.date_of_first_registration is None:
            missing_data_fields.append('deal.date_of_first_registration')

        if deal.private_car:
            customer = deal.customer
            profile = customer.motorinsurancecustomerprofile

            if not profile.uae_license_age:
                missing_data_fields.append('customer_profile.uae_license_age')

            if not customer.dob:
                missing_data_fields.append('customer.dob')

        return missing_data_fields

    def rate_book_product_code_to_mapped_code(self, rate_book_code):
        try:
            return self.config['mapping'][rate_book_code]
        except KeyError:
            return None

    def get_quote_for_insurer_with_deal(self, insurer, deal, form_data):
        self.log.info('TokioMarineAutoQuoter: Generating quotes with deal id %s, and form data %s', deal.pk, form_data)

        self.setup_for_company(deal.company)

        if self.rate_book is None:
            self.log.warning('TokioMarineAutoQuoter: No rate book set.')
            raise AutoQuoterException('No rate book set for your company')

        quotes = []

        can_quote, reason = self.rate_book.can_quote_any(deal, form_data)
        if not can_quote:
            return [{
                'name': self.rate_book.must_name or 'Tokio Marine Must (Non-Agency)',
                'exception': True,
                'message': reason
            }]

        can_quote_smart_plus, reason = self.rate_book.can_quote_smart_plus(deal, form_data)
        if can_quote_smart_plus:
            smart_plus_quote = self.rate_book.get_smart_plus_quote(deal, form_data)

            company_product_code = self.rate_book_product_code_to_mapped_code(smart_plus_quote['productCode'])
            if company_product_code is None:
                self.log.warning('TokioMarineAutoQuoter: Unable to map Smart Plus product to a product code for '
                                 'company %s', deal.company.name)
            else:
                smart_plus_quote['productCode'] = company_product_code
                quotes.append(smart_plus_quote)
        else:
            quotes.append({
                'name': self.rate_book.smart_plus_name or 'Tokio Marine Smart Plus Plan (Agency)',
                'exception': True,
                'message': reason
            })

        can_quote_must, reason = self.rate_book.can_quote_must(deal, form_data)
        if can_quote_must:
            must_quote = self.rate_book.get_must_quote(deal, form_data)

            company_product_code = self.rate_book_product_code_to_mapped_code(must_quote['productCode'])
            if company_product_code is None:
                self.log.warning('TokioMarineAutoQuoter: Unable to map Must product to a product code for '
                                 'company %s', deal.company.name)
            else:
                must_quote['productCode'] = company_product_code
                quotes.append(must_quote)
        else:
            quotes.append({
                'name': self.rate_book.must_name or 'Tokio Marine Must (Non-Agency)',
                'exception': True,
                'message': reason
            })

        return quotes
