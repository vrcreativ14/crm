import datetime
import json
import logging
from enum import Enum

import requests
from django.conf import settings

from auto_quoter.auto_quoter_base import AutoQuoterBase
from auto_quoter.constants import AmanVehicleTypes, AMAN_API
from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.models import AutoQuoterConfig, InsurerApiTransactionLog
from auto_quoter.utils import passes_common_auto_quoting_checks, AutoQuoterResponse
from motorinsurance.helpers import is_ncd_more_than
from motorinsurance.models import Deal

logger = logging.getLogger('auto_quoter.aman')


def get_deductible(deal, form_data):
    if form_data['vehicle_type'] in [AmanVehicleTypes.Bus, AmanVehicleTypes.Pickup5TonOrTruck]:
        return 4500
    else:
        if deal.number_of_passengers <= 9:
            if form_data['insured_value'] <= 50000:
                return 350
            elif form_data['insured_value'] <= 100000:
                return 700
            elif form_data['insured_value'] <= 250000:
                return 1000
            elif form_data['insured_value'] <= 500000:
                return 1200
            else:
                return 1400
        elif deal.number_of_passengers <= 12:
            return 1500
        else:
            return 1700


class AmanMotorTakafulLvvRateBook:
    regular_rate_table = {
        AmanVehicleTypes.Saloon: {
            'agency': {
                'rate': 3.0,
                'minimum': 1300
            },
            'non-agency': {
                'rate': 2.5,
                'minimum': 1300
            }
        },
        AmanVehicleTypes.Coupe: {
            '4 seats': {
                'agency': {
                    'rate': 3.0,
                    'minimum': 1300
                },
                'non-agency': {
                    'rate': 2.5,
                    'minimum': 1300
                }
            },
            '2 seats': {
                'agency': {
                    'rate': 4.25,
                    'minimum': 2500
                },
                'non-agency': {
                    'rate': 3.5,
                    'minimum': 2500
                }
            }
        },
        AmanVehicleTypes.Sports: {
            'agency': {
                'rate': 4.25,
                'minimum': 2500
            },
            'non-agency': {
                'rate': 3.5,
                'minimum': 2500
            }
        },
        AmanVehicleTypes.FourByFour: {
            'agency': {
                'rate': 2.75,
                'minimum': 2000
            },
            'non-agency': {
                'rate': 2.25,
                'minimum': 2000
            }
        },
        AmanVehicleTypes.Pickup3TonOrVan: {
            'agency': {
                'rate': 3.5,
                'minimum': 1700
            },
            'non-agency': {
                'rate': 3.0,
                'minimum': 1550
            }
        },
        AmanVehicleTypes.Pickup5TonOrTruck: {
            'agency': {
                'rate': 3.5,
                'minimum': 2500
            },
            'non-agency': {
                'rate': 3.25,
                'minimum': 2000
            }
        },
        AmanVehicleTypes.Bus: {
            '<= 15 seats': {
                'agency': {
                    'rate': 4.0,
                    'minimum': 2500
                },
                'non-agency': {
                    'rate': 3.5,
                    'minimum': 1950
                }
            },
            '> 15 seats': {
                'agency': {
                    'rate': 3.5,
                    'minimum': 2500
                },
                'non-agency': {
                    'rate': 2.75,
                    'minimum': 2400
                }
            }
        }
    }

    below_25_rate_table = {
        AmanVehicleTypes.Saloon: {
            'agency': {
                'rate': 4.75,
                'minimum': 1900
            },
            'non-agency': {
                'rate': 4.25,
                'minimum': 1300
            },
        },
        AmanVehicleTypes.FourByFour: {
            'agency': {
                'rate': 6.50,
                'minimum': 2000
            },
            'non-agency': {
                'rate': 4.75,
                'minimum': 2000
            }
        },
    }

    def is_restricted_vehicle(self, deal):
        # Need to check for Alpha Romeo, Fiat, Seat, and Chinese brand vehicles
        return deal.car_make.name in ['Alfa Romeo', 'Fiat', 'SEAT', 'MG', 'GAC', 'Changan', 'JAC', 'Geely']

    def can_quote_agency_repair(self, deal, form_data):
        car_age = deal.get_age_of_car_since_registration()
        if car_age > 3:
            return False, 'This plan is not available for vehicles older than 3 years'

        if car_age == 1:
            return True, ''
        elif not form_data['previous_year_agency']:
            return False, 'Agency repair only available when previous year repair condition is agency repair'

        if car_age > 1 and form_data['vehicle_type'] in [AmanVehicleTypes.Pickup3TonOrVan,
                                                         AmanVehicleTypes.Pickup5TonOrTruck, AmanVehicleTypes.Bus]:
            return False, 'This plan is not available for this kind of vehicle'

        if deal.has_no_claims_history() and deal.claim_certificate_available:
            if car_age == 2:
                return (is_ncd_more_than(deal.years_without_claim, 1),
                        'This plan requires a 1 year no claim letter')
            elif car_age == 3:
                return (is_ncd_more_than(deal.years_without_claim, 1),
                        'This plan requires a 1 year no claim letter')

        return False, 'This plan requires a 1 year no claim letter'

    def can_quote(self, deal, form_data):
        common_checks_passed, reason = passes_common_auto_quoting_checks(deal, form_data)
        if not common_checks_passed:
            return False, reason

        if deal.customer.get_age() > 65:
            return False, 'This plan is only available for drivers between the ages of 25 and 65'

        if deal.customer.get_age() < 25 and form_data['vehicle_type'] not in [AmanVehicleTypes.Saloon,
                                                                              AmanVehicleTypes.Coupe,
                                                                              AmanVehicleTypes.FourByFour]:
            return False, 'This plan is only available for drivers between the ages of 25 and 65'

        # Can't quote a 2 seat saloon for driver younger than 25 years
        if (deal.customer.get_age() < 25 and
                form_data['vehicle_type'] in (AmanVehicleTypes.Saloon, AmanVehicleTypes.Coupe)
                and deal.number_of_passengers == 1):
            return False, 'This plan is only available for drivers between the ages of 25 and 65'

        if form_data['insured_value'] > 200000:
            return False, 'This plan is not available for vehicles valued above Dhs 200K'

        if not deal.car_gcc_spec:
            return False, 'This plan is not available for non-GCC spec vehicles'

        if deal.get_age_of_car_since_registration() > 10:
            return False, 'This plan is not available for vehicles older than 10 years'

        if form_data['vehicle_type'] == AmanVehicleTypes.Sports:
            return False, 'Sports & high performance vehicles must be referred to AMAN for underwriting'

        if self.is_restricted_vehicle(deal):
            return False, 'This vehicle must be referred to AMAN for underwriting'

        return True, ''

    def get_agency_quote(self, deal, form_data):
        trace = []

        if deal.customer.get_age() >= 25:
            trace.append("Using rates for a customer above 25 years of age")

            if form_data['vehicle_type'] == AmanVehicleTypes.Saloon:
                rating_values = self.regular_rate_table[AmanVehicleTypes.Saloon]['agency']
                trace.append("Using Saloon rates")
            elif form_data['vehicle_type'] == AmanVehicleTypes.Coupe:
                seats_key = '4 seats' if deal.number_of_passengers > 1 else '2 seats'
                rating_values = self.regular_rate_table[AmanVehicleTypes.Coupe][seats_key]['agency']

                trace.append('Using Coupe {} rate'.format(seats_key))
            elif form_data['vehicle_type'] == AmanVehicleTypes.Sports:
                rating_values = self.regular_rate_table[AmanVehicleTypes.Sports]['agency']
                trace.append("Using Sports rates")
            elif form_data['vehicle_type'] == AmanVehicleTypes.Bus:
                seats_key = '<= 15 seats' if deal.number_of_passengers < 15 else '> 15 seats'
                rating_values = self.regular_rate_table[AmanVehicleTypes.Bus][seats_key]['agency']

                trace.append(
                    "Using Bus ({}) rates".format(seats_key)
                )
            else:
                rating_values = self.regular_rate_table[form_data['vehicle_type']]['agency']

                trace.append(
                    "Using rates for vehicle type {}".format(form_data['vehicle_type'].name)
                )

            premium = max(rating_values['minimum'], form_data['insured_value'] * (rating_values['rate'] / 100.0))
        else:
            if form_data['vehicle_type'] in (AmanVehicleTypes.Saloon, AmanVehicleTypes.Coupe):
                rating_values = self.below_25_rate_table[AmanVehicleTypes.Saloon]['agency']

                trace.append(
                    "Using Saloon/Coupe (4 seats) rates"
                )
            else:
                rating_values = self.below_25_rate_table[form_data['vehicle_type']]['agency']

                trace.append(
                    "Using rates for vehicle type {}".format(form_data['vehicle_type'].name)
                )

            premium = max(rating_values['minimum'], form_data['insured_value'] * (rating_values['rate'] / 100.0))

        return {
            "productCode": "Aman Comprehensive LVV",
            "quoteReference": "",
            "insuredCarValue": form_data['insured_value'],
            "canInsure": True,
            "referralRequired": False,
            "agencyRepair": True,
            "premium": premium,
            "deductible": get_deductible(deal, form_data),
            "rulesTrace": trace
        }

    def get_non_agency_quote(self, deal, form_data):
        trace = []

        if deal.customer.get_age() >= 25:
            trace.append("Using rates for a customer above 25 years of age")

            if form_data['vehicle_type'] == AmanVehicleTypes.Saloon:
                rating_values = self.regular_rate_table[AmanVehicleTypes.Saloon]['non-agency']
                trace.append("Using Saloon rates")
            elif form_data['vehicle_type'] == AmanVehicleTypes.Coupe:
                seats_key = '4 seats' if deal.number_of_passengers > 1 else '2 seats'
                rating_values = self.regular_rate_table[AmanVehicleTypes.Coupe][seats_key]['non-agency']

                trace.append('Using Coupe {} rate'.format(seats_key))
            elif form_data['vehicle_type'] == AmanVehicleTypes.Sports:
                rating_values = self.regular_rate_table[AmanVehicleTypes.Sports]['non-agency']
                trace.append("Using Sports rates")
            elif form_data['vehicle_type'] == AmanVehicleTypes.Bus:
                seats_key = '<= 15 seats' if deal.number_of_passengers < 15 else '> 15 seats'
                rating_values = self.regular_rate_table[AmanVehicleTypes.Bus][seats_key]['non-agency']

                trace.append(
                    "Using Bus ({}) rates".format(seats_key)
                )
            else:
                rating_values = self.regular_rate_table[form_data['vehicle_type']]['non-agency']

                trace.append(
                    "Using rates for vehicle type {}".format(form_data['vehicle_type'].name)
                )

            premium = max(rating_values['minimum'], form_data['insured_value'] * (rating_values['rate'] / 100.0))
        else:
            if form_data['vehicle_type'] in (AmanVehicleTypes.Saloon, AmanVehicleTypes.Coupe):
                rating_values = self.below_25_rate_table[AmanVehicleTypes.Saloon]['non-agency']

                trace.append(
                    "Using Saloon/Coupe (4 seats) rates"
                )
            else:
                rating_values = self.below_25_rate_table[form_data['vehicle_type']]['non-agency']

                trace.append(
                    "Using rates for vehicle type {}".format(form_data['vehicle_type'].name)
                )

            premium = max(rating_values['minimum'], form_data['insured_value'] * (rating_values['rate'] / 100.0))

        return {
            "productCode": "Aman Comprehensive LVV",
            "quoteReference": "",
            "insuredCarValue": form_data['insured_value'],
            "canInsure": True,
            "referralRequired": False,
            "agencyRepair": False,
            "premium": premium,
            "deductible": get_deductible(deal, form_data),
            "rulesTrace": trace
        }

    def get_quotes(self, deal, form_data):
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
        can_quote, why_not = self.can_quote(deal, form_data)
        if not can_quote:
            return [{
                'name': 'Aman Insurance Comprehensive',
                'exception': True,
                'message': why_not
            }]

        comprehensive_quote = self.get_non_agency_quote(deal, form_data)

        can_quote_agency, why_not = self.can_quote_agency_repair(deal, form_data)
        if not can_quote_agency:
            agency_quote_response = {
                'name': 'Aman Insurance Comprehensive (Agency Repair)',
                'exception': True,
                'message': why_not
            }
        else:
            agency_quote_response = self.get_agency_quote(deal, form_data)

        return [
            comprehensive_quote,
            agency_quote_response
        ]


class AmanMotorTakafulHvvRateBook:
    regular_rate_table = {
        'agency': {
            1: 2.30,
            2: 2.30,
            3: 3.00,
        },
        'non-agency': 2.00
    }

    def is_restricted_vehicle(self, deal):
        return deal.car_make.name in ['Alfa Romeo', 'Fiat', 'SEAT', 'MG', 'GAC', 'Changan', 'JAC', 'Geely']

    def can_quote_agency_repair(self, deal, form_data):
        car_age = deal.get_age_of_car_since_registration()
        if car_age > 3:
            return False, 'This plan is not available for vehicles older than 3 years'

        if car_age == 1:
            return True, ''
        elif not form_data['previous_year_agency']:
            return False, 'Agency repair only available when previous year repair condition is agency repair'

        if deal.has_no_claims_history() and deal.claim_certificate_available:
            if car_age == 2:
                return (is_ncd_more_than(deal.years_without_claim, 1),
                        'This plan requires a 1 year no claim letter')
            elif car_age == 3:
                return (is_ncd_more_than(deal.years_without_claim, 1),
                        'This plan requires a 1 year no claim letter')

        return False, 'This plan requires a 1 year no claim letter'

    def can_quote(self, deal, form_data):
        common_checks_passed, reason = passes_common_auto_quoting_checks(deal, form_data)
        if not common_checks_passed:
            return False, reason

        if deal.customer.get_age() > 65:
            return False, 'This plan is only available for drivers between the ages of 25 and 65'
        if deal.customer.get_age() < 25:
            return False, 'This plan is only available for drivers between the ages of 25 and 65'

        # Can't quote a 2 seat saloon for driver younger than 25 years
        if form_data['vehicle_type'] not in [AmanVehicleTypes.Saloon, AmanVehicleTypes.Coupe,
                                             AmanVehicleTypes.FourByFour]:
            return False, 'This plan is not available for this type of vehicle'

        if not (deal.number_of_passengers > 1):
            return False, 'This plan is not available for this type of vehicle'

        if form_data['insured_value'] <= 200000:
            return False, 'This plan is not available for vehicles valued below Dhs 200K or above Dhs 1.5M'
        if form_data['insured_value'] > 1500000:
            return False, 'This plan is not available for vehicles valued below Dhs 200K or above Dhs 1.5M'

        if not deal.car_gcc_spec:
            return False, 'This plan is not available for non-GCC spec vehicles'

        if deal.get_age_of_car_since_registration() > 8:
            return False, 'This plan is not available for vehicles older than 8 years'

        if self.is_restricted_vehicle(deal):
            return False, 'This vehicle must be referred to AMAN for underwriting'

        return True, ''

    def get_agency_quote(self, deal, form_data):
        trace = []

        car_age = deal.get_age_of_car_since_registration()

        trace.append('Using {} year rate for agency repair'.format(car_age))
        rate = self.regular_rate_table['agency'][car_age]

        premium = (rate / 100.0) * form_data['insured_value']

        return {
            "productCode": "Aman Comprehensive HVV",
            "quoteReference": "",
            "insuredCarValue": form_data['insured_value'],
            "canInsure": True,
            "referralRequired": False,
            "agencyRepair": True,
            "premium": premium,
            "deductible": get_deductible(deal, form_data),
            "rulesTrace": trace
        }

    def get_non_agency_quote(self, deal, form_data):
        trace = []

        premium = (self.regular_rate_table['non-agency'] / 100.0) * form_data['insured_value']

        return {
            "productCode": "Aman Comprehensive HVV",
            "quoteReference": "",
            "insuredCarValue": form_data['insured_value'],
            "canInsure": True,
            "referralRequired": False,
            "agencyRepair": False,
            "premium": premium,
            "deductible": get_deductible(deal, form_data),
            "rulesTrace": trace
        }

    def get_quotes(self, deal, form_data):
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
        can_quote, why_not = self.can_quote(deal, form_data)
        if not can_quote:
            return [{
                'name': 'Aman Insurance HVV Comprehensive',
                'exception': True,
                'message': why_not
            }]

        comprehensive_quote = self.get_non_agency_quote(deal, form_data)

        can_quote_agency, why_not = self.can_quote_agency_repair(deal, form_data)
        if not can_quote_agency:
            agency_quote_response = {
                'name': 'Aman Insurance HVV Comprehensive (Agency Repair)',
                'exception': True,
                'message': why_not
            }
        else:
            agency_quote_response = self.get_agency_quote(deal, form_data)

        return [
            comprehensive_quote,
            agency_quote_response
        ]


class AmanMotorTakafulDynaTradeRateBook:
    rate_table = {
        AmanVehicleTypes.Saloon: {
            'rate': 3.0,
            'minimum': 1600
        },
        AmanVehicleTypes.FourByFour: {
            'rate': 2.6,
            'minimum': 2300
        },
        AmanVehicleTypes.Coupe: {
            'rate': 4.0,
            'minimum': 3500
        },
    }

    def is_restricted_vehicle(self, deal):
        return deal.car_make.name in ['Alfa Romeo', 'Fiat', 'SEAT', 'MG', 'GAC', 'Changan', 'JAC', 'Geely']

    def can_quote(self, deal, form_data):
        common_checks_passed, reason = passes_common_auto_quoting_checks(deal, form_data)
        if not common_checks_passed:
            return False, reason

        if not deal.car_gcc_spec:
            return False, 'This plan is not available for non-GCC spec vehicles'

        if form_data['vehicle_type'] not in self.rate_table:
            return False, 'This plan is not available for this type of vehicle'

        if deal.get_age_of_car_since_registration() > 6:
            return False, 'This plan is not available for vehicles older than 6 years'

        if not (40000 <= form_data['insured_value'] <= 500000):
            return False, 'This plan is not available for vehicles valued below Dhs 40K or above Dhs 500K'

        if deal.customer.get_age() < 25:
            return False, 'This plan is only available for drivers between the ages of 25 and 65'
        if deal.customer.get_age() > 65:
            return False, 'This plan is only available for drivers between the ages of 25 and 65'

        if self.is_restricted_vehicle(deal):
            return False, 'This vehicle must be referred to AMAN for underwriting'

        return True, ''

    def get_quotes(self, deal, form_data):
        can_quote, reason = self.can_quote(deal, form_data)
        if not can_quote:
            return [{
                'name': 'Aman Insurance Motor Plus Plan Dynatrade (Non-Agency)',
                'exception': True,
                'message': reason
            }]

        trace = []

        trace.append('Using rate for vehicle type {}'.format(form_data['vehicle_type'].name))
        rating_data = self.rate_table[form_data['vehicle_type']]

        premium = (rating_data['rate'] / 100.0) * form_data['insured_value']
        premium = max(premium, rating_data['minimum'])

        return [{
            "productCode": "Aman Comprehensive Dyna Trade",
            "quoteReference": "",
            "insuredCarValue": form_data['insured_value'],
            "canInsure": True,
            "referralRequired": False,
            "agencyRepair": False,
            "premium": premium,
            "deductible": get_deductible(deal, form_data),
            "rulesTrace": trace
        }]


class AmanAutoQuoter(AutoQuoterBase):
    def setup_for_company(self, company):
        logger.debug('AmanAutoQuoter: Setting up self for company %s', company.name)
        self.company = company
        try:
            self.config = AutoQuoterConfig.objects.get(company=company, insurer='aman').get_options_dict()
        except AutoQuoterConfig.DoesNotExist:
            raise AutoQuoterException('The Aman auto quoter is not configured')

    def get_deal_missing_data_fields(self, deal: Deal):
        missing_field_names = []

        if deal.date_of_first_registration is None:
            missing_field_names.append('deal.date_of_first_registration')

        if deal.customer.dob is None:
            missing_field_names.append('customer.dob')

        if not deal.number_of_passengers:
            missing_field_names.append('deal.number_of_passengers')

        return missing_field_names

    def get_quote_for_insurer_with_deal(self, insurer, deal, form_data):
        self.setup_for_company(deal.company)

        basic_rate_book = AmanMotorTakafulLvvRateBook
        if form_data['insured_value'] > 200000:
            basic_rate_book = AmanMotorTakafulHvvRateBook

        rates = basic_rate_book().get_quotes(deal, form_data)
        rates.extend(AmanMotorTakafulDynaTradeRateBook().get_quotes(deal, form_data))

        final_quotes = []
        for rate in rates:
            if not rate.get('exception'):
                if rate['productCode'] in self.config['mapping']:
                    rate['productCode'] = self.config['mapping'][rate['productCode']]
                    rate['premium'] *= 1.05  # VAT
                    final_quotes.append(rate)
                else:
                    logger.warning('AmanAutoQuoter: Product code %s not mapped to anything in our products DB',
                                   rate['productCode'])
            else:
                final_quotes.append(rate)

        return rates


class AmanApiAutoQuoter(AutoQuoterBase):
    class PolicyClass(Enum):
        TPL = 2
        Comprehensive = 3

    class UsedVehicle(Enum):
        New = 0
        Renewal = 1
        TransferToDifferentEmirate = 2
        TransferWithinSameEmirate = 3

    class TypeCar(Enum):
        Used = 1
        New = 2

    class AgencyRepair(Enum):
        NonAgencyRepair = 0
        AgencyRepair = 1

    class VehicleUsage(Enum):
        Private = 1
        Commercial = 2
        Transportation = 3
        General = 4
        Public = 5
        TAXI = 6
        DiplomaticAuthority = 7
        ConseltAuthority = 8

    class AAA(Enum):
        No = 0
        Yes = 1

    class PABD(Enum):
        No = 0
        Yes = 1

    class PABP(Enum):
        No = 0
        Yes = 1

    class OffRoad(Enum):
        No = 0
        Yes = 1

    class OmanCover(Enum):
        No = 0
        Yes = 1

    class Cities(Enum):
        Dubai = 1
        Sharjah = 2
        AbuDhabi = 3
        AlAin = 4
        RasAlKhaimah = 5
        UmmAlQuwain = 6
        Ajman = 7
        Fujairah = 8
        Khorfakan = 9
        Other = 99
        GCCCountriesLicHolder = 10
        JabelAli = 11

    base_url = settings.AUTO_QUOTERS['aman']['api_url']

    def __init__(self):
        super().__init__()

        self.session = None

    def setup_for_company(self, company):
        self.config = AutoQuoterConfig.objects.get(company=company, insurer=AMAN_API).get_options_dict()

        self.session = requests.session()
        self.session.headers['Authentication'] = self.config['token']
        self.session.verify = False

    def get_base_params(self):
        return {
            "Broker_UserName": self.config['username'],
            "Broker_Password": self.config['password'],
            "Broker_ID": self.config['broker_id'],
            "Broker_Hash": self.config['broker_hash']
        }

    def get_vehicle_details(self, chassis_number):
        url = self.base_url + '/vehicledetails/'
        params = self.get_base_params()
        params.update({
            "Chassis_No": chassis_number,
            "Pol_Class": '3',
            "Requestee": "Broker"
        })

        response = self.session.post(url, data=params)
        if not response.ok:
            logger.error("AmanApiAutoQuoter: Not OK response from AMAN vehicle details API. Response: %s",
                         response.content)
            raise AutoQuoterException("Not OK response from AMAN API.")

        return response.json()['VehicleDetailsResponse']['Data']

    def get_discounts(self):
        url = self.base_url + '/discounts/'
        response = self.session.get(url)
        if not response.ok:
            logger.error("AmanApiAutoQuoter: Not OK response from AMAN discounts API. Response: %s",
                         response.content)
            raise AutoQuoterException("Not OK response from AMAN API.")

        response_data = response.json()
        if not response_data['BodyColorsResponse']['Result']['ResponseStatus'] == 'success':
            response_message = response_data['BodyColorsResponse']['Result']['ResponseMessage']
            logger.error("AmanApiAutoQuoter: Not OK response from AMAN discounts API. Response message: %s",
                         response_message)
            raise AutoQuoterException(response_message)

        available_discounts = response_data['BodyColorsResponse']['Data']
        discounts = [
            (0, f'No discount'),
        ]

        for discount_data in available_discounts:
            description = discount_data['Discounts']['DISC_DESC']
            percentage = discount_data['Discounts']['DISC_PER']

            discounts.append(
                (percentage, f'{description} - {percentage}%')
            )

        return discounts

    def get_premium(self, deal: Deal, policy_class: PolicyClass, sum_insured: int, dob: datetime.date,
                    used_car: UsedVehicle, agency_repair: AgencyRepair, vehicle_use: VehicleUsage,
                    vehicle_code: str, body_code: str, year_manufacture: str, aaa: AAA, pabd: PABD,
                    pabp: PABP, off_road: OffRoad, oman_cover: OmanCover, license_city: Cities,
                    license_registration_date: datetime.date, emirate_of_registration: Cities,
                    first_registration_date: datetime.date, last_registration_date: datetime.date,
                    seats: int, weight: float, cylinders: int, discount_percentage: str):
        url = self.base_url + '/calcpremium/'

        if used_car == AmanApiAutoQuoter.UsedVehicle.New:
            type_car = AmanApiAutoQuoter.TypeCar.New
        else:
            type_car = AmanApiAutoQuoter.TypeCar.Used

        params = {
            "BROKER_CODE": self.config['broker_id'],
            "POL_CLASS": policy_class.value,
            "SUM_INSURED": sum_insured,
            "DATE_OF_BIRTH": dob.strftime("%d/%m/%Y"),
            "USED_CAR": used_car.value,
            "TYPE_CAR": type_car.value,
            "AG_REP": agency_repair.value,
            "VEHICLE_USE": vehicle_use.value,
            "VEH_CODE": vehicle_code,
            "BODY_CODE": body_code,
            "YEAR_MANUFAC": year_manufacture,
            "AAA": aaa.value,
            "PABD": pabd.value,
            "PABP": pabp.value,
            "OFF_ROAD": off_road.value,
            "OMAN_COVER": oman_cover.value,
            "LICENSE_CITY": license_city.value,
            "LICENSE_REG_DATE": license_registration_date.strftime("%d/%m/%Y"),
            "EMIRATES_REG": emirate_of_registration.value,
            "FIRST_REG_DATE": first_registration_date.strftime("%d/%m/%Y"),
            "LAST_REG_DATE": last_registration_date.strftime("%d/%m/%Y"),
            "SEATS": seats,
            "WEIGHT": weight,
            "CYLINDERS": cylinders
        }

        log = InsurerApiTransactionLog(company=deal.company, insurer=AMAN_API, deal=deal,
                                       request_content=json.dumps(params))

        response = self.session.get(url, params=params)

        log.response_content = response.content
        log.save()

        if not response.ok:
            logger.error("AmanApiAutoQuoter: Not OK response from AMAN calculate premium API. Response: %s",
                         response.content)
            return AutoQuoterResponse(False, "Not OK response from AMAN API.")

        response_data = response.json()
        calc_premium_response = response_data['CalcPremiumResponse']
        if calc_premium_response['Result']['ResponseStatus'] == 'error':
            logger.warning("AmanApiAutoQuoter: Error response from the API. Error message: %s",
                           calc_premium_response['Result']['ResponseMessage'])
            return AutoQuoterResponse(False, calc_premium_response['Result']['ResponseMessage'],
                                      extra=calc_premium_response)
        else:
            pd = calc_premium_response['Data']

            pre_discount_premium = pd['OD_Premium'] + pd['TPL_Premium']
            discount_percentage = int(discount_percentage) / 100.0
            discounted_premium = pre_discount_premium - (pre_discount_premium * discount_percentage)
            final_premium = discounted_premium + (
                    pd['ADD_PREMIUM'] + pd['ADD_PABD_AMNT'] + pd['ADD_PABP_AMNT'] + pd['ADD_REP_AMNT'] +
                    pd['ADD_LEGL_AMNT'] + pd['ADD_OFF_ROAD_AMNT'] + pd['ADD_OmanC_AMNT']
            )

            return AutoQuoterResponse(
                True, "", self.add_vat(final_premium), pd['EXCESS_AMOUNT'],
                extra=calc_premium_response
            )

    def add_vat(self, premium):
        return premium * 1.05

    def get_deal_missing_data_fields(self, deal):
        missing_field_names = []

        if deal.customer.dob is None:
            missing_field_names.append('customer.dob')

        return missing_field_names

    def str_value_to_enum_member(self, enum_klass, value):
        for member in enum_klass:
            if str(member.value) == value:
                return member

        raise ValueError("Unable to find %s in %s" % (value, enum_klass))

    def get_quote_for_insurer_with_deal(self, insurer, deal, form_data):
        self.setup_for_company(deal.company)

        agency_repair = self.str_value_to_enum_member(
            AmanApiAutoQuoter.AgencyRepair, form_data['agency_repair']
        )
        policy_class = self.str_value_to_enum_member(
            AmanApiAutoQuoter.PolicyClass, form_data['policy_class']
        )

        response = self.get_premium(
            deal,

            policy_class,
            form_data['sum_insured'],
            deal.customer.dob,
            self.str_value_to_enum_member(
                AmanApiAutoQuoter.UsedVehicle, form_data['used_vehicle']
            ),
            agency_repair,
            self.str_value_to_enum_member(
                AmanApiAutoQuoter.VehicleUsage, form_data['vehicle_usage']
            ),
            form_data['vehicle_code'],
            form_data['body_code'],
            form_data['year_manufactured'],
            self.str_value_to_enum_member(
                AmanApiAutoQuoter.AAA, form_data['aaa']
            ),
            self.str_value_to_enum_member(
                AmanApiAutoQuoter.PABD, form_data['pabd']
            ),
            self.str_value_to_enum_member(
                AmanApiAutoQuoter.PABP, form_data['pabp']
            ),
            self.str_value_to_enum_member(
                AmanApiAutoQuoter.OffRoad, form_data['off_road']
            ),
            self.str_value_to_enum_member(
                AmanApiAutoQuoter.OmanCover, form_data['oman_cover']
            ),
            self.str_value_to_enum_member(
                AmanApiAutoQuoter.Cities, form_data['license_city']
            ),
            form_data['license_registration_date'],
            self.str_value_to_enum_member(
                AmanApiAutoQuoter.Cities, form_data['emirate_of_registration']
            ),
            form_data['first_registration_date'],
            form_data['last_registration_date'],
            form_data['seats'],
            form_data['weight'],
            form_data['cylinders'],
            form_data['discount_percentage'],
        )

        if response.ok:
            if policy_class == AmanApiAutoQuoter.PolicyClass.Comprehensive:
                if agency_repair == AmanApiAutoQuoter.AgencyRepair.AgencyRepair:
                    auto_quoter_product_code = "Aman Api Agency Repair"
                else:
                    auto_quoter_product_code = "Aman Api Non-Agency Repair"
            else:
                auto_quoter_product_code = "Aman Api TPL"

            try:
                mapped_product_code = self.config["mapping"][auto_quoter_product_code]
            except KeyError:
                logger.warning("AmanApiAutoQuoter: Unable to map generic product code %s to a DB product code",
                               auto_quoter_product_code)
                return []

            return [{
                "productCode": mapped_product_code,
                "quoteReference": "",
                "insuredCarValue": form_data['sum_insured'],
                "canInsure": True,
                "referralRequired": False,
                "agencyRepair": agency_repair == AmanApiAutoQuoter.AgencyRepair.AgencyRepair,
                "premium": response.premium,
                "deductible": response.deductible,
                "rulesTrace": []
            }]
        else:
            logger.warning(
                "AmanApiAutoQuoter: Error in response from API when trying to quote for deal id %s. Response: %s",
                deal.pk, response.extra
            )

            return [{
                "name": "Aman Api",
                "exception": True,
                "message": response.message
            }]
