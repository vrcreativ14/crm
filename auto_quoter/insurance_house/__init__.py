"""Auto quoters for Insurance House rate books"""
import logging

from auto_quoter.auto_quoter_base import AutoQuoterBase
from auto_quoter.constants import InsuranceHouseVehicleTypes
from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.insurance_house.car_exclusions import is_car_excluded
from auto_quoter.models import AutoQuoterConfig
from auto_quoter.utils import passes_common_auto_quoting_checks
from motorinsurance.helpers import is_ncd_more_than, is_license_age_more_than


class InsuranceHouseAutoQuoter(AutoQuoterBase):
    def __init__(self):
        super().__init__()

        self.log = logging.getLogger('api.insurance_house')

    def get_deal_missing_data_fields(self, deal):
        missing_fields = []

        if deal.get_age_of_car_since_registration() is None:
            missing_fields.append('deal.date_of_first_registration')

        customer = deal.customer
        customer_profile = customer.motorinsurancecustomerprofile

        if not customer_profile.first_license_age and not customer_profile.uae_license_age:
            missing_fields.append('customer_profile.uae_license_age')

        if not customer.dob:
            missing_fields.append('customer.dob')

        return missing_fields

    def can_quote_any_option(self, deal, form_data):
        """Checks conditions that apply to both agency & non-agency options"""
        common_checks_passed, reason = passes_common_auto_quoting_checks(deal, form_data)
        if not common_checks_passed:
            return False, reason

        customer_profile = deal.customer.motorinsurancecustomerprofile
        if not (is_license_age_more_than(customer_profile.uae_license_age, 12) or
                is_license_age_more_than(customer_profile.first_license_age, 12)):
            return (False,
                    'This plan is not available for drivers with less than 1 year UAE/home country driving license')

        if is_car_excluded(deal):
            return False, 'This vehicle is excluded'

        if form_data['insured_value'] > 250000:
            return False, 'This plan is not available for vehicles valued above Dhs 250K.'

        if deal.customer.get_age() < 25 or deal.customer.get_age() > 65:
            return False, 'This plan is only available for drivers between the ages of 25 and 65.'

        if not deal.car_gcc_spec or not deal.car_unmodified:
            return False, 'This plan is not available for non-GCC spec or modified vehicles.'

        if deal.get_age_of_car_since_registration() > 10:
            return False, 'This plan is not available for vehicles older than 10 years.'

        if form_data['vehicle_type'] == InsuranceHouseVehicleTypes.Bus and deal.number_of_passengers > 56:
            return False, 'This plan is not available for buses with more than 56 seats.'

        return True, None

    def can_quote_dynatrade_repair_for_deal(self, deal, form_data):
        if form_data['vehicle_type'] not in [InsuranceHouseVehicleTypes.Saloon, InsuranceHouseVehicleTypes.FourByFour]:
            return False, 'This plan is not available for this kind of vehicle.'

        if deal.get_age_of_car_since_registration() > 6:
            return False, 'This plan is not available for vehicles older than 6 years.'

        return True, None

    def can_quote_agency_for_deal(self, deal, form_data):
        if (form_data['vehicle_type'] not in [InsuranceHouseVehicleTypes.Saloon,
                                              InsuranceHouseVehicleTypes.FourByFour] and
                deal.get_age_of_car_since_registration() > 1):
            return False, 'This plan is not available for vehicles older than 1 year.'

        if deal.get_age_of_car_since_registration() > 2:
            return False, 'This plan is not available for vehicles older than 2 years.'

        if deal.get_age_of_car_since_registration() > 1 and (not deal.claim_certificate_available or
                                                             not is_ncd_more_than(deal.years_without_claim, 1)):
            return False, 'This plan requires a 1 year no claim letter.'

        return True, None

    def add_vat(self, amount):
        return amount * 1.05

    def get_deductible(self, deal, form_data):
        if form_data['vehicle_type'] in [InsuranceHouseVehicleTypes.Saloon, InsuranceHouseVehicleTypes.FourByFour]:
            if form_data['insured_value'] <= 50000:
                return 250
            elif form_data['insured_value'] <= 100000:
                return 700
            else:
                return 1000
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.Pickup3TonOrVan:
            return 1000
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.PickupAbove3TonOrTruck:
            return 1500
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.Bus:
            if deal.number_of_passengers <= 15:
                return 1500
            elif deal.number_of_passengers <= 26:
                return 2000
            elif deal.number_of_passengers <= 34:
                return 2500
            elif deal.number_of_passengers <= 56:
                return 3000
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.SchoolBus:
            if deal.number_of_passengers <= 15:
                return 1500
            elif deal.number_of_passengers <= 26:
                return 2000
            elif deal.number_of_passengers <= 34:
                return 2500
            elif deal.number_of_passengers <= 56:
                return 3000
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.EquipmentOrHeavy:
            return 3000

    def get_pab_driver_and_passengers(self, deal, form_data):
        vehicle_type = form_data['vehicle_type']

        if vehicle_type in [InsuranceHouseVehicleTypes.Saloon, InsuranceHouseVehicleTypes.FourByFour]:
            return 0.0

        if vehicle_type in [InsuranceHouseVehicleTypes.Pickup3TonOrVan,
                            InsuranceHouseVehicleTypes.PickupAbove3TonOrTruck,
                            InsuranceHouseVehicleTypes.EquipmentOrHeavy]:
            return 120.0

        if vehicle_type == InsuranceHouseVehicleTypes.Bus:
            pab_driver = 120.0
            pab_passenger = 30.0
        elif vehicle_type == InsuranceHouseVehicleTypes.SchoolBus:
            pab_driver = 60.0
            pab_passenger = 10.0
        else:
            raise ValueError('Unknown vehicle type.')

        return pab_driver + deal.number_of_passengers * pab_passenger

    def get_non_agency_quote(self, deal, form_data):
        trace = []

        if form_data['vehicle_type'] == InsuranceHouseVehicleTypes.Saloon:
            trace.append('Applying Saloon rates.')

            rate = 1.95
            min_premium = 1300
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.FourByFour:
            trace.append('Applying 4WD rates.')

            rate = 1.95
            min_premium = 2000
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.Pickup3TonOrVan:
            trace.append('Applying Pick up (<=3 ton) or Van rates.')

            rate = 2.50
            min_premium = 1550
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.PickupAbove3TonOrTruck:
            trace.append('Applying Pick up (>3 ton) or Van rates.')

            rate = 2.50
            min_premium = 2300
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.Bus:
            if deal.number_of_passengers <= 15:
                trace.append('Applying Bus (<=15 passengers) rates.')

                rate = 2.75
                min_premium = 2900
            elif deal.number_of_passengers <= 26:
                trace.append('Applying Bus (<=26 passengers) rates.')

                rate = 2.50
                min_premium = 2400
            elif deal.number_of_passengers <= 34:
                trace.append('Applying Bus (<=34 passengers) rates.')

                rate = 2.50
                min_premium = 2400
            elif deal.number_of_passengers <= 56:
                trace.append('Applying Bus (<=56 passengers) rates.')

                rate = 2.50
                min_premium = 2400
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.SchoolBus:
            trace.append('Applying School Bus rates.')

            rate = 1.75
            min_premium = 2400
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.EquipmentOrHeavy:
            trace.append('Applying Equipment or Heavy Vehicle rates.')

            rate = 3.00
            min_premium = 2500

        if is_ncd_more_than(deal.years_without_claim, 3):
            trace.append('Applying NCD for >=3 years.')

            ncd = 20.0
        elif is_ncd_more_than(deal.years_without_claim, 2):
            trace.append('Applying NCD for >=2 years.')

            ncd = 15.0
        elif is_ncd_more_than(deal.years_without_claim, 1):
            trace.append('Applying NCD for 2 year.')

            ncd = 10.0
        else:
            trace.append('No NCD applicable')

            ncd = 0.0

        rate = rate - (rate * ncd / 100.0)
        min_premium = min_premium - (min_premium * ncd / 100.0)

        premium = rate / 100.0 * form_data['insured_value']
        premium = max(min_premium, premium) + self.get_pab_driver_and_passengers(deal, form_data)

        return {
            "productCode": self.get_scheme_name('Non-Agency'),
            "quoteReference": "",
            "insuredCarValue": form_data['insured_value'],
            "canInsure": True,
            "referralRequired": False,
            "agencyRepair": False,
            "premium": self.add_vat(premium),
            "deductible": self.get_deductible(deal, form_data),
            "rulesTrace": trace
        }

    def get_agency_quote(self, deal, form_data):
        trace = []

        if form_data['vehicle_type'] == InsuranceHouseVehicleTypes.Saloon:
            if deal.get_age_of_car_since_registration() <= 1:
                trace.append('Applying 1st year Saloon rates.')

                rate = 2.30
                min_premium = 1600
            elif deal.get_age_of_car_since_registration() == 2:
                trace.append('Applying 1st year Saloon rates.')

                rate = 2.30
                min_premium = 1600

        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.FourByFour:
            if deal.get_age_of_car_since_registration() <= 1:
                trace.append('Applying 1st year 4WD rates.')

                rate = 2.30
                min_premium = 2000
            elif deal.get_age_of_car_since_registration() == 2:
                trace.append('Applying 1st year 4WD rates.')

                rate = 2.30
                min_premium = 2000
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.Pickup3TonOrVan:
            trace.append('Applying Pick up (<=3 ton) or Van rates.')

            rate = 2.75
            min_premium = 2000
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.PickupAbove3TonOrTruck:
            trace.append('Applying Pick up (>3 ton) or Van rates.')

            rate = 2.75
            min_premium = 2500
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.Bus:
            if deal.number_of_passengers <= 15:
                trace.append('Applying Bus (<=15 passengers) rates.')

                rate = 2.75
                min_premium = 3000
            elif deal.number_of_passengers <= 26:
                trace.append('Applying Bus (<=26 passengers) rates.')

                rate = 2.75
                min_premium = 2400
            elif deal.number_of_passengers <= 34:
                trace.append('Applying Bus (<=34 passengers) rates.')

                rate = 2.75
                min_premium = 2400
            elif deal.number_of_passengers <= 56:
                trace.append('Applying Bus (<=56 passengers) rates.')

                rate = 2.75
                min_premium = 2400
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.SchoolBus:
            trace.append('Applying School Bus rates.')

            rate = 1.75
            min_premium = 2400
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.EquipmentOrHeavy:
            trace.append('Applying Equipment or Heavy Vehicle rates.')

            rate = 3.00
            min_premium = 2500

        premium = rate / 100.0 * form_data['insured_value']
        premium = max(min_premium, premium) + self.get_pab_driver_and_passengers(deal, form_data)

        return {
            "productCode": self.get_scheme_name('Agency'),
            "quoteReference": "",
            "insuredCarValue": form_data['insured_value'],
            "canInsure": True,
            "referralRequired": False,
            "agencyRepair": True,
            "premium": self.add_vat(premium),
            "deductible": self.get_deductible(deal, form_data),
            "rulesTrace": trace
        }

    def get_dynatrade_quote(self, deal, form_data):
        trace = []

        if form_data['vehicle_type'] == InsuranceHouseVehicleTypes.Saloon:
            trace.append('Using Saloon rates.')

            rate = 2.30
            min_premium = 1600
        elif form_data['vehicle_type'] == InsuranceHouseVehicleTypes.FourByFour:
            trace.append('Using 4WD rates.')

            rate = 2.30
            min_premium = 2000

        premium = rate / 100.0 * form_data['insured_value']
        premium = max(min_premium, premium)

        return {
            "productCode": self.get_scheme_name('DynaTrade'),
            "quoteReference": "",
            "insuredCarValue": form_data['insured_value'],
            "canInsure": True,
            "referralRequired": False,
            "agencyRepair": False,
            "premium": self.add_vat(premium),
            "deductible": self.get_deductible(deal, form_data),
            "rulesTrace": trace
        }

    def get_quote_for_insurer_with_deal(self, insurer, deal, form_data):
        self.setup_for_company(deal.company)

        can_quote, reason = self.can_quote_any_option(deal, form_data)
        if not can_quote:
            return [{
                'name': self.get_scheme_name('Agency & Non-Agency'),
                'exception': True,
                'message': reason
            }, {
                'name': self.get_scheme_name('DynaTrade'),
                'exception': True,
                'message': reason
            }]

        quotes = [self.get_non_agency_quote(deal, form_data)]

        can_quote, reason = self.can_quote_agency_for_deal(deal, form_data)
        if can_quote:
            quotes.append(self.get_agency_quote(deal, form_data))
        else:
            quotes.append({
                'name': self.get_scheme_name('Agency'),
                'exception': True,
                'message': reason
            })

        can_quote, reason = self.can_quote_dynatrade_repair_for_deal(deal, form_data)
        if can_quote:
            quotes.append(self.get_dynatrade_quote(deal, form_data))
        else:
            quotes.append({
                'name': self.get_scheme_name('DynaTrade'),
                'exception': True,
                'message': reason
            })

        cleaned_quotes = []
        for quote in quotes:
            if not quote.get('exception'):
                mapped_product_code = self.get_product_code_for_scheme_name(quote['productCode'], deal, form_data)
                if mapped_product_code is None:
                    self.log.warning('InsuranceHouseAutoQuoter: Unable to map product code %s to anything in our'
                                     ' product DB', mapped_product_code)
                    continue
                else:
                    quote['productCode'] = mapped_product_code
                    cleaned_quotes.append(quote)

        return quotes

    def get_scheme_name(self, repair_type):
        return f'Insurance House Comprehensive 2019 Promotion ({repair_type})'

    def get_product_code_for_scheme_name(self, scheme_name, deal, form_data):
        vehicle_type = form_data['vehicle_type']
        scheme_name_with_vehicle_type = f'{scheme_name} ({vehicle_type.value})'

        product_code = self.config['mapping'].get(scheme_name_with_vehicle_type)
        if product_code is None:
            product_code = self.config['mapping'].get(scheme_name)

        return product_code

    def setup_for_company(self, company):
        self.log.debug('InsuranceHouseAutoQuoter: Setting up self for company %s', company.name)
        self.company = company
        try:
            self.config = AutoQuoterConfig.objects.get(company=company, insurer='insurance house').get_options_dict()
        except AutoQuoterConfig.DoesNotExist:
            raise AutoQuoterException('The Insurance House auto quoter is not configured')
