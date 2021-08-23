"""Oman Insurance API v 1.3"""
import json
import logging
import pprint

import requests
from django.core.cache import cache
from django.conf import settings
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib.oauth2_session import OAuth2Session

from auto_quoter.api_mappings import oic as mapping
from auto_quoter.auto_quoter_base import AutoQuoterBase
from auto_quoter.constants import OIC
from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.models import InsurerApiTransactionLog, AutoQuoterConfig
from motorinsurance.constants import INSURANCE_TYPE_TPL
from motorinsurance.helpers import add_two_license_ages


class OICAutoQuoter(AutoQuoterBase):
    def __init__(self):
        super(OICAutoQuoter, self).__init__()

        self.log = logging.getLogger('auto_quote.oic')
        self.base_url = settings.AUTO_QUOTERS['oic']['api_url']
        self.token_url = settings.AUTO_QUOTERS['oic']['login_url']

        self.session = None

    def _setup_cache(self, company):
        self._cache_company = company

    def _get_from_cache(self, key):
        return cache.get(key)

    def _set_in_cache(self, key, value):
        cache.set(key, value, 3600)

    def setup_for_company(self, company):
        self.log.debug(f'OICAutoQuoter: setup_for_company({company.name})')

        try:
            self.config = AutoQuoterConfig.objects.get(company=company, insurer='oic').get_options_dict()
        except AutoQuoterConfig.DoesNotExist:
            raise AutoQuoterException('The Oman auto quoter is not configured')

        self._setup_cache(company)

        client_id = self.config['client_id']
        secret_key = self.config['secret_key']

        client = BackendApplicationClient(client_id=client_id)
        auth = HTTPBasicAuth(client_id, secret_key)
        session = OAuth2Session(client=client)

        token = session.fetch_token(self.token_url, scope='motorapi', auth=auth, timeout=60)
        self.session = session
        return token

    def _ensure_session(self):
        if self.session is None:
            self.log.error('OICAutoQuoter: No session configured before trying to use API')
            raise AutoQuoterException('No oAuth session configured')

    def load_master_data(self):
        cached_master_data = self._get_from_cache('master_data')
        if cached_master_data is not None:
            self.log.info('OICAutoQuoter: Got master data from cache')
            return cached_master_data

        self._ensure_session()

        url = self.base_url + '/Master'
        response = self.session.get(url, timeout=30)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            self.log.error(f'OICAutoQuoter: load_master_data failed with error {str(e)}')
            raise AutoQuoterException(f'Unable to access API. Error: {str(e)}')

        master_data = response.json()

        self._set_in_cache('master_data', master_data)
        return master_data

    def get_master_definitions_for_type(self, master_type):
        for data in self.load_master_data():
            if data['masterType'] == master_type:
                return data['masterDefinitions']

        self.log.error(f'OICAutoQuoter: Unable to load {master_type} list from master data')
        raise LookupError('Unable to find {master_type} data in master data')

    def get_master_list_item_for_description(self, master_list_type, description):
        for item_info in self.get_master_definitions_for_type(master_list_type):
            item_id, item_description = item_info['id'], item_info['description']

            if item_description is None:
                self.log.debug('OICAutoQuoter: None value seen in master list for type %s', master_list_type)
                continue
            else:
                item_description = item_description.strip()

            if item_description == description:
                return item_info

        self.log.error(f'OICAutoQuoter: Unable to find %s in API mapping for %s', description, master_list_type)
        raise LookupError(f'OICAutoQuoter: Unable to find {description} in API mapping for {master_list_type}')

    def country_code_to_country_id(self, country_code):
        oic_country_name = mapping.country_mapping[country_code]
        country_info = self.get_master_list_item_for_description('Countries', oic_country_name)

        country_id, oic_country_name = country_info['id'], country_info['description']
        self.log.debug(
            f'OICAutoQuoter: Mapped country code %s to API country %s',
            country_code, oic_country_name
        )
        return country_id

    def license_age_to_driving_experience_id(self, license_age):
        api_driving_experience_name = mapping.driving_experience[license_age]

        driving_experience_info = self.get_master_list_item_for_description('DrivingExperiences',
                                                                            api_driving_experience_name)
        de_id, de_name = driving_experience_info['id'], driving_experience_info['description']

        self.log.debug(
            f'OICAutoQuoter: Mapped license age %s to API driving experience %s',
            license_age, de_name
        )
        return de_id

    def emirate_to_place_of_registration_id(self, emirate):
        api_emirate_name = mapping.emirates[emirate]

        place_of_registration_info = self.get_master_list_item_for_description('PlaceOfRegistrations',
                                                                               api_emirate_name)
        por_id, por_name = place_of_registration_info['id'], place_of_registration_info['description']

        self.log.debug(
            f'OICAutoQuoter: Mapped Emirate %s to API place of registration %s',
            emirate, por_name
        )
        return por_id

    def year_to_year_id(self, year):
        api_year_name = str(year)

        year_info = self.get_master_list_item_for_description('Years', api_year_name)
        year_id, year_name = year_info['id'], year_info['description']

        self.log.debug(
            f'OICAutoQuoter: Mapped year %s to API year %s',
            year, year_name
        )
        return year_id

    def get_manufacturers_for_year(self, year):
        cache_key = f'manufacturers:{year}'

        cached_manufacturers_list = self._get_from_cache(cache_key)
        if cached_manufacturers_list is not None:
            return cached_manufacturers_list

        self._ensure_session()

        year_id = self.year_to_year_id(year)
        params = {
            'yearId': year_id
        }
        url = self.base_url + '/Master/ManufacturersByYear'

        response = self.session.get(url, params=params, timeout=30)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            self.log.error(f'OICAutoQuoter: get_manufacturers_for_year failed with error {str(e)}')
            raise AutoQuoterException(f'Unable to access API. Error: {str(e)}')

        manufacturers_list = response.json()

        self._set_in_cache(cache_key, manufacturers_list)
        return manufacturers_list

    def get_car_manufacturer_id_for_deal(self, deal):
        car_year = deal.car_year
        car_make = deal.car_make

        try:
            oic_make_name = mapping.car_makes[car_make.name]
        except KeyError:
            self.log.error(f'OICAutoQuoter: Unable to map {car_year} {car_make.name} to OIC manufacturer')
            raise LookupError(f'OICAutoQuoter: Unable to map {car_year} {car_make.name} to OIC manufacturer')

        oic_makes_available = self.get_manufacturers_for_year(car_year)

        for make_info in oic_makes_available:
            make_name = make_info['description']
            if make_name == oic_make_name:
                self.log.debug(f'OICAutoQuoter: Mapped {car_year} {car_make.name} to {make_name}')
                return make_info['id']

        self.log.error(f'OICAutoQuoter: Unable to map {car_year} {car_make.name} to OIC manufacturer')
        raise LookupError(f'OICAutoQuoter: Unable to map {car_year} {car_make.name} to OIC manufacturer')

    def get_car_models_for_deal(self, deal):
        self._ensure_session()

        try:
            make_id = self.get_car_manufacturer_id_for_deal(deal)
        except LookupError as e:
            raise AutoQuoterException(f'OICAutoQuoter: Unable to find car manufacturer for deal id {deal.pk}. Error: '
                                      f'{str(e)}')

        params = {
            'manufacturerId': make_id
        }
        url = self.base_url + '/Master/ModelsByManufacturer'

        response = self.session.get(url, params=params, timeout=30)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            self.log.error(f'OICAutoQuoter: Unable to get car models for deal id {deal.pk}. Error: {str(e)}')
            raise AutoQuoterException(f'OICAutoQuoter: Unable to get car models for deal id {deal.pk}. Error: {str(e)}')

        return response.json()

    def get_car_specs_for_model(self, model_id):
        self._ensure_session()

        params = {
            'modelId': model_id
        }
        url = self.base_url + '/Master/SpecificationsByModel'

        response = self.session.get(url, params=params, timeout=30)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            self.log.error(f'OICAutoQuoter: Unable to get car specs for model id {model_id}. Error: {str(e)}')
            raise AutoQuoterException(
                f'OICAutoQuoter: Unable to get car specs for model id {model_id}. Error: {str(e)}')

        return response.json()

    def get_vehicles_for_spec(self, spec_id):
        self._ensure_session()

        params = {
            'specificationId': spec_id
        }
        url = self.base_url + '/Master/VehiclesBySpecification'

        response = self.session.get(url, params=params, timeout=30)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            self.log.error(f'OICAutoQuoter: Unable to get vehicles for specification id {spec_id}. Error: {str(e)}')
            raise AutoQuoterException(
                f'OICAutoQuoter: Unable to get vehicles for specification id {spec_id}. Error: {str(e)}')
        return response.json()

    @classmethod
    def get_deal_missing_data_fields(cls, deal):
        missing_data_fields = []

        customer = deal.customer

        if not customer.name:
            missing_data_fields.append('customer.name')
        if not customer.dob:
            missing_data_fields.append('customer.dob')
        if not customer.phone:
            missing_data_fields.append('customer.phone')
        if not customer.email:
            missing_data_fields.append('customer.email')

        customer_profile = customer.motorinsurancecustomerprofile

        if not customer_profile.uae_license_age:
            missing_data_fields.append('customer_profile.uae_license_age')

        if not customer_profile.first_license_country:
            missing_data_fields.append('customer_profile.first_license_country')

        if not deal.place_of_registration:
            missing_data_fields.append('deal.place_of_registration')

        return missing_data_fields

    def oic_product_name_to_product_code(self, product_name):
        try:
            return self.config['mapping'][product_name]
        except KeyError:
            return None

    def add_taxes(self, amount):
        return amount * 1.05

    def get_quote_for_insurer_with_deal(self, insurer, deal, form_data):
        if self.get_deal_missing_data_fields(deal):
            self.log.error(f'OICAutoQuoter: Unable to quote deal id {deal.pk} because of missing data')
            raise AutoQuoterException('Can not auto quote deal due to missing data')

        self.log.info(
            'OICAutoQuoter: Requesting quote with deal id {}, and form data {}'.format(
                deal.pk, form_data
            )
        )

        self.setup_for_company(deal.company)

        customer = deal.customer
        customer_profile = customer.motorinsurancecustomerprofile

        is_third_party = 0
        if deal.current_insurance_type == INSURANCE_TYPE_TPL:
            is_third_party = 1

        country_of_first_driving_license = customer_profile.first_license_country
        total_license_age = add_two_license_ages(customer_profile.uae_license_age, customer_profile.first_license_age)

        request_data = {
            'Title': '1',
            'FirstName': customer.name.split(maxsplit=1)[0],
            'LastName': customer.name.split(maxsplit=1)[-1],
            'DateOfBirth': customer.dob.strftime('%d/%m/%Y'),
            'MobileNo': customer.phone,
            'EmailAddress': customer.email,

            'CountryOfFirstDrivingLicense': self.country_code_to_country_id(country_of_first_driving_license),
            'DrivingExperience': self.license_age_to_driving_experience_id(total_license_age),
            'PlaceOfRegistration': self.emirate_to_place_of_registration_id(deal.place_of_registration),

            'VehicleYear': self.year_to_year_id(deal.car_year),
            'VehicleMake': self.get_car_manufacturer_id_for_deal(deal),
            'VehicleModel': form_data['model'],
            'Specification': form_data['specification'],
            'Vehicle': form_data['vehicle'],
            'SumInsured': float(form_data['insured_value']),

            'IsModified': 0 if deal.car_unmodified else 1,
            'IsNonGccVehicle': 0 if deal.car_gcc_spec else 1,
            'IsMortgaged': 1 if form_data['mortgaged'] else 0,
            'IsThirdParty': is_third_party,
            'IsUninsured': 0 if form_data['currently_in_cover'] else 1,
        }

        api_tx_log = InsurerApiTransactionLog(company=deal.company, insurer=OIC, deal=deal,
                                              request_content=json.dumps(request_data))

        url = self.base_url + '/Quote/getQuote'
        try:
            response = self.session.post(url, json=request_data, timeout=30)

            api_tx_log.response_info = response.status_code
            api_tx_log.response_content = response.text
            api_tx_log.save()
        except requests.Timeout:
            api_tx_log.response_info = 'API timeout'
            api_tx_log.save()

            self.log.error('OICAutoQuoter: Request to Oman API timed out')
            raise AutoQuoterException(f'The Oman API call timed out. '
                                      f'Please provide support with this Tx id if the error persists: {api_tx_log.pk}')

        # The API returns a referral required response as a 400 status code with some help text. Detect that here
        if response.status_code == requests.codes['bad_request']:
            if 'We are unable to process your request' in response.text:
                raise AutoQuoterException(response.text)

        try:
            response.raise_for_status()
            response_data = response.json()
        except requests.HTTPError as e:
            self.log.error('OICAutoQuoter: Non-OK response from the API. Error: %s', e)
            raise AutoQuoterException(f'Error encountered while calling the Oman API. '
                                      f'Please provide support with this Tx id if the error persists: {api_tx_log.pk}')

        self.log.debug(f'OICAutoQuoter: Received quotes response for deal id {deal.pk}. Response data: %s',
                       pprint.pformat(response_data))

        plans = response_data['plans']

        quotes = []
        for plan in plans:
            oic_product_code = plan['name']
            our_product_code = self.oic_product_name_to_product_code(oic_product_code)

            if our_product_code is None:
                self.log.warning('Unable to map Oman product code %s to any of ours. Deal id %d',
                                 oic_product_code, deal.pk)
                continue
            else:
                self.log.info('Mapped Oman product code %s to our product code %s. Deal id %d',
                              oic_product_code, our_product_code, deal.pk)

            quotes.append({
                'productCode': our_product_code,
                'quoteReference': response_data['quoteRefNo'],
                'insuredCarValue': form_data['insured_value'],
                'canInsure': True,
                'referralRequired': False,
                'agencyRepair': plan['repairCondition'] == 'Dealer Workshop',
                'premium': self.add_taxes(plan['premium']),
                'deductible': plan.get('standardExcess', 0),
                'rulesTrace': ['Got response from Oman API']
            })

        return quotes
