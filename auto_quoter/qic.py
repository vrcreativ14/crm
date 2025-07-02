import json
import logging

import pandas
import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.utils.timezone import now as tz_now

from auto_quoter.api_mappings import qic as mappings
from auto_quoter.auto_quoter_base import AutoQuoterBase
from auto_quoter.constants import QIC
from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.models import AutoQuoterConfig, InsurerApiTransactionLog


class QICAutoQuoter(AutoQuoterBase):
    def __init__(self):
        super(QICAutoQuoter, self).__init__()

        self.log = logging.getLogger('auto_quote.qic')

    @classmethod
    def get_deal_missing_data_fields(cls, deal):
        customer = deal.customer

        missing_data_fields = []

        if not customer.name:
            missing_data_fields.append('customer.name')
        if not customer.dob:
            missing_data_fields.append('customer.dob')

        if not deal.date_of_first_registration:
            missing_data_fields.append('deal.date_of_first_registration')
        if not deal.place_of_registration:
            missing_data_fields.append('deal.place_of_registration')

        return missing_data_fields

    @classmethod
    def deal_to_registration_location_code(cls, deal):
        return mappings.emirates_mapping[deal.place_of_registration]

    @classmethod
    def deal_to_car_make_code(cls, deal):
        if deal.car_make.pk in mappings.v_make_mapping:
            return mappings.v_make_mapping[deal.car_make.pk][1]
        else:
            return None

    @classmethod
    def deal_to_car_model_choices(cls, deal):
        make_code = cls.deal_to_car_make_code(deal)

        df = pandas.read_csv(settings.AUTO_QUOTERS['qic']['model_code_mapping_file'], dtype=str)
        model_df = df[df["Make Code"] == make_code]

        if deal.car_trim:
            model = deal.car_trim.model
            matched_models = model_df[model_df["Description"].str.lower().str.contains(model.name.lower())]

            if not matched_models.empty:
                return matched_models[["Model Code", "Description"]].values.tolist()

        return model_df[["Model Code", "Description"]].values.tolist()

    @classmethod
    def deal_to_vehicle_usage_code(cls, deal):
        if deal.private_car:
            return '1001'
        else:
            return '1002'  # Commercial

    @classmethod
    def customer_to_nationality_code(cls, customer):
        if customer.nationality:
            return mappings.country_mapping[customer.nationality]
        else:
            return None

    @classmethod
    def customer_profile_to_driving_experience(cls, customer_profile):
        if not customer_profile.uae_license_age:
            return None

        return {
            "less than 6 months": 0,
            "less than 1 year": 0,
            "less than 2 years": 1,
            "more than 2 years": 2,
        }[customer_profile.uae_license_age]

    @classmethod
    def customer_to_gender_code(cls, customer):
        if customer.gender == 'm':
            return '1'
        elif customer.gender == 'f':
            return '2'
        else:
            return None

    def api_scheme_code_to_product_code(self, scheme_code):
        try:
            return self.config['mapping'][scheme_code]
        except KeyError:
            return None

    def setup_for_company(self, company):
        if self.config is not None:
            self.log.debug('QICAutoQuoter: Already setup for company %s.', company.name)
            return

        self.log.debug('QICAutoQuoter: Setting up self for company %s', company.name)
        self.company = company
        try:
            self.config = AutoQuoterConfig.objects.get(company=company, insurer='qic').get_options_dict()
        except AutoQuoterConfig.DoesNotExist:
            raise AutoQuoterException('The QIC auto quoter is not configured')

    def get_request_data_for_deal(self, deal, form_data):
        """form_data is the cleaned data from a form displayed to the user when they select QIC for auto quoting.
        That form has fields that are required for quoting QIC products."""
        customer = deal.customer
        customer_profile = deal.customer.motorinsurancecustomerprofile

        if self.get_deal_missing_data_fields(deal):
            self.log.error('QICAutoQuoter: Unable to map %s %s to QIC manufacturer', deal.car_year, deal.car_make.name)
            raise AutoQuoterException('Can not auto quote deal due to missing data')

        request_data = {
            'sumInsured': float(form_data['insured_value']),
            'vehicleType': form_data['vehicle_type'],
            'vehicleUsage': self.deal_to_vehicle_usage_code(deal),
            'makeCode': self.deal_to_car_make_code(deal),
            'modelCode': form_data['model'],
            'regnLocation': self.deal_to_registration_location_code(deal),
            'regYear': deal.date_of_first_registration.year,
            'modelYear': deal.car_year,
            'gccSpec': '1' if deal.car_gcc_spec else '0',
            'noOfCylinder': form_data['cylinders'],
            'seatingCapacity': form_data['seating_capacity'],

            'insuredName': customer.name,
            'driverDOB': customer.dob.strftime('%d/%m/%Y'),
            'insuredAge': relativedelta(tz_now().date(), customer.dob).years,
            'previousInsuranceValid': form_data['previous_insurance_valid'],
            'totalLoss': form_data['total_loss']
        }

        nationality = self.customer_to_nationality_code(customer)
        if nationality:
            request_data['nationality'] = nationality

        driving_experience = self.customer_profile_to_driving_experience(customer_profile)
        if driving_experience:
            request_data['driverExp'] = driving_experience

        gender = self.customer_to_gender_code(customer)
        if gender:
            request_data['gender'] = gender

        return request_data

    def add_taxes(self, amount):
        return float(amount) * 1.05

    def get_common_request_params(self):
        return {
            'auth': (self.config['username'], self.config['password']),
            'headers': {
                'Company': self.config['company']
            },
            'timeout': 30
        }

    def get_vehicle_info(self, deal, chassis_number):
        self.log.info(
            'QICAutoQuoter: Requesting vehicle info from QIC for chassis number %s.', chassis_number
        )
        self.setup_for_company(deal.company)

        final_url = settings.AUTO_QUOTERS['qic']['base_url'] + '/admeVehicleInfo'
        request_data = {
            'chassisNo': chassis_number
        }

        raw_response = requests.post(
            final_url,
            json=request_data,
            **self.get_common_request_params()
        )
        if raw_response.status_code != requests.status_codes.codes.ok:
            self.log.error(
                'QICAutoQuoter: Unable to get vehicle info. Response code: %s. Response body: %s.',
                raw_response.status_code, raw_response.text
            )
            raise AutoQuoterException('QICAutoQuoter: Unable to get vehicle info.')

        self.log.debug(
            'QICAutoQuoter: Received response for vehicle info. Chassis number: %s. Response data: %s.',
            chassis_number, raw_response.text
        )

        response_data = raw_response.json()
        return {
            'make': response_data['vehMake'],
            'model': response_data['vehModel'],
            'year': response_data['vehModelYear']
        }

    def get_trims(self, deal, chassis_number, make_code, model_code, year_code):
        self.log.debug(
            'QICAutoQuoter: Requesting trims from QIC API for deal id %s. Chassis number: %s Make: %s Model: %s '
            'Year: %s',
            deal.pk, chassis_number, make_code, model_code, year_code
        )

        self.setup_for_company(deal.company)

        final_url = settings.AUTO_QUOTERS['qic']['base_url'] + '/admeSpecification'
        request_data = {
            'withoutChassisNoFlag': False,
            'chassisNo': chassis_number,
            'vehMake': make_code,
            'vehModel': model_code,
            'vehModelYear': year_code
        }

        raw_response = requests.post(
            final_url, json=request_data, **self.get_common_request_params()
        )

        if raw_response.status_code != requests.status_codes.codes.ok:
            self.log.error(
                'QICAutoQuoter: Unable to get vehicle trims. Response code: %s. Response body: %s.',
                raw_response.status_code, raw_response.text
            )
            raise AutoQuoterException('QICAutoQuoter: Unable to get vehicle trims.')

        self.log.debug(
            'QICAutoQuoter: Received response for vehicle trims. Chassis number: %s. Response data: %s.',
            chassis_number, raw_response.text
        )

        response_data = raw_response.json()

        if response_data.get('errMessage') != 'Success':
            self.log.error('QICAutoQuoter: Error in vehicle trims response: %s', response_data['errMessage'])
            raise AutoQuoterException(response_data['errMessage'])

        return response_data['specification']

    def get_vehicle_details(self, deal, chassis_number, make_code, model_code, year_code, trim_id):
        self.log.debug(
            'QICAutoQuoter: Getting vehicle details for chassis number %s and trim id %s.', chassis_number, trim_id
        )

        self.setup_for_company(deal.company)

        final_url = settings.AUTO_QUOTERS['qic']['base_url'] + '/admeQuoteInfo'
        request_params = {
            'withoutChassisNoFlag': False,
            'chassisNo': chassis_number,
            'vehMake': make_code,
            'vehModel': model_code,
            'vehModelYear': year_code,
            'admeId': trim_id
        }

        raw_response = requests.post(
            final_url, json=request_params, **self.get_common_request_params()
        )

        if raw_response.status_code != requests.status_codes.codes.ok:
            self.log.error(
                'QICAutoQuoter: Unable to get vehicle details. Response code: %s. Response body: %s.',
                raw_response.status_code, raw_response.text
            )
            raise AutoQuoterException('QICAutoQuoter: Unable to get vehicle details.')

        self.log.debug(
            'QICAutoQuoter: Received response for vehicle details. Chassis number: %s. Response data: %s.',
            chassis_number, raw_response.text
        )

        return raw_response.json()

    def get_quote(self, deal, name, make_code, model_code, model_year, sum_insured, vehicle_type_code,
                  vehicle_usage_code, number_cylinders, nationality_code, seating_capacity, first_registration_date,
                  gcc_spec, previous_insurance_valid, is_total_loss, driver_dob, no_claim_years,
                  no_claim_years_self_dec, chassis_number, driver_gcc_experience, trim_code):
        self.log.debug(
            'QICAutoQuoter: Getting quote from QIC API for chassis number %s.', chassis_number
        )

        self.setup_for_company(deal.company)

        final_url = settings.AUTO_QUOTERS['qic']['base_url'] + '/motor/tariff'
        request_data = {
            'insuredName': name,
            'makeCode': make_code,
            'modelCode': model_code,
            'modelYear': model_year,
            'sumInsured': sum_insured,
            'vehicleType': vehicle_type_code,
            'vehicleUsage': vehicle_usage_code,
            'noOfCylinder': number_cylinders,
            'nationality': nationality_code,
            'seatingCapacity': seating_capacity,
            'firstRegDate': first_registration_date.strftime('%d/%m/%Y'),
            'gccSpec': gcc_spec,
            'previousInsuranceValid': previous_insurance_valid,
            'totalLoss': is_total_loss,
            'driverDOB': driver_dob.strftime('%d/%m/%Y'),
            'noClaimYear': no_claim_years,
            'selfDeclarationYear': no_claim_years_self_dec,
            'chassisNo': chassis_number,
            'driverExp': driver_gcc_experience,
            'admeId': trim_code
        }

        api_tx_log = InsurerApiTransactionLog(company=deal.company, insurer=QIC, deal=deal,
                                              request_content=json.dumps(request_data))

        raw_response = requests.post(
            final_url, json=request_data, **self.get_common_request_params()
        )

        self.log.debug(
            'QICAutoQuoter: Received response for quote. Chassis number: %s. Response data: %s.',
            chassis_number, raw_response.text
        )

        try:
            api_tx_log.response_info = raw_response.status_code
            api_tx_log.response_content = raw_response.text
            api_tx_log.save()
        except requests.Timeout:
            api_tx_log.response_info = 'API timeout'
            api_tx_log.save()

            self.log.error('QICAutoQuoter: Request to QIC API timed out')
            raise AutoQuoterException('The API failed to respond. Please try later')

        try:
            raw_response.raise_for_status()
        except requests.HTTPError as e:
            self.log.error('QICAutoQuoter: Error in response from API. Error: %s', str(e))

            try:
                resp_data = raw_response.json()
                if resp_data['errMessage']:
                    raise AutoQuoterException(resp_data['errMessage'])
            except (TypeError, ValueError):
                raise AutoQuoterException('The API returned an invalid response')

        resp_data = raw_response.json()
        if resp_data['errMessage']:
            raise AutoQuoterException(resp_data['errMessage'])

        final_responses = []
        for quote_response in resp_data['schemes']:
            qic_product_code = quote_response['schemeName']
            our_product_code = self.api_scheme_code_to_product_code(qic_product_code)

            if our_product_code is None:
                self.log.warning('Unable to map QIC product code %s to any of ours. Deal id %d',
                                 qic_product_code, deal.pk)
                continue
            else:
                self.log.info('Mapped QIC product code %s to our product code %s. Deal id %d',
                              qic_product_code, our_product_code, deal.pk)

            deductible = 0
            deductible_data_array = quote_response.get('excessCovers', [])
            if len(deductible_data_array) > 0:
                deductible_data = deductible_data_array[0]
                if 'premium' in deductible_data:
                    deductible = deductible_data['premium']

            quote = {
                'productCode': our_product_code,
                'quoteReference': resp_data['quoteNo'],
                'insuredCarValue': sum_insured,
                'canInsure': True,
                'referralRequired': False,
                'agencyRepair': self.is_quote_response_agency_repair(quote_response),
                'premium': self.add_taxes(quote_response['netPremium']),
                'deductible': deductible,
                'rulesTrace': ['Got response from QIC API']
            }

            final_responses.append(quote)

        return final_responses

    @classmethod
    def is_quote_response_agency_repair(cls, resp):
        for cover in resp['inclusiveCovers']:
            if cover['name'] == 'Agency Repairs':
                return True

        for cover in resp['optionalCovers']:
            if cover['name'] == 'Agency Repairs':
                return True

        return False
