from urllib.parse import urljoin
import logging

import requests
from django.conf import settings
from auto_quoter import constants

from auto_quoter.custom_ratebooks_base import CustomRateBooksBase
from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.utils import passes_common_auto_quoting_checks
from motorinsurance_shared.models import CarTrim

logger = logging.getLogger('auto_quote.watania')

EXCLUDED_VEHICLES_FILTERS = {
    'Alfa Romeo': [],
    'Bentley': [],
    'Chrysler': [],
    'Citroën': [],
    'Fiat': [],
    'Hummer': [],
    'Lotus': [],
    'Maserati': [],
    'MINI': [],
    'Opel': [],
    'Saab': [],
    'Skoda': [],
    'Subaru': [],

    "BMW": [
        {"model__name__startswith": "M"},
        {"algo_driven_data__body__iexact": "Coupe"},
    ],
    "Dodge": [
        {"model__name": "Charger"},
        {"algo_driven_data__body__iexact": 'Coupe'},
    ],

    "Audi": [
        {"algo_driven_data__body__iexact": 'Coupe'},
        {"model__name__startswith": 'RS'},
        {"algo_driven_data__variant__icontains": "Luxury"},
    ],

    "Cadillac": [
        {"algo_driven_data__body__iexact": "Coupe"},
        {"algo_driven_data__body__iexact": "SUV", "algo_driven_data__variant__icontains": "Luxury"},
    ],

    "Chevrolet": [
        {"algo_driven_data__body__iexact": "Coupe"},
    ],

    "Ford": [
        {"algo_driven_data__body__iexact": "Coupe"},
        {"algo_driven_data__body__iexact": "Double Cab Utility", "algo_driven_data__variant__icontains": "Luxury"},
    ],

    "Honda": [
        {"algo_driven_data__body__iexact": "Coupe"},
    ],

    "Jaguar": [
        {"algo_driven_data__body__iexact": "Coupe"},
    ],

    "Jeep": [
        {"model__name": "Wrangler"},
        {"model__name": "Grand Cherokee", "algo_driven_data__variant__startswith": "SRT"},
        {"algo_driven_data__variant__icontains": "Sahara"},
    ],

    "Lexus": [
        {"algo_driven_data__body__iexact": "Coupe"},
    ],

    "Mazda": [
        {"algo_driven_data__body__iexact": "Coupe"},
    ],

    "Mercedes-AMG": [
        {"algo_driven_data__body__iexact": "Coupe"},
    ],
    "Mercedes-Benz": [
        {"algo_driven_data__body__iexact": "Coupe"},
    ],

    "Mitsubishi": [
        {"algo_driven_data__body__iexact": "Coupe"},
        {"algo_driven_data__body__iexact": "Double Cab Utility"},
        {"algo_driven_data__body__iexact": "Single Cab Utility"},
        {"algo_driven_data__variant__icontains": "Single Evolution Utility"},
    ],

    "Nissan": [
        {"algo_driven_data__body__iexact": "Coupe"},
        {"algo_driven_data__body__iexact": "Double Cab Utility"},
        {"algo_driven_data__body__iexact": "Single Cab Utility"},
        {"algo_driven_data__variant__icontains": "Single Evolution Utility"},
        {"algo_driven_data__variant__icontains": "Van"},
        {"model__name": "Patrol", "algo_driven_data__variant__icontains": "Safari"},
    ],

    "Peugeot": [
        {"algo_driven_data__body__iexact": "Coupe"},
        {"algo_driven_data__body__iexact": "Convertible"},
    ],

    "Porsche": [
        {"algo_driven_data__body__iexact": "Coupe"},
    ],

    "Land Rover": [
        {"algo_driven_id__in": ["AELRRAN12ACAA", "AELRRRS12AFAA"]},
    ],

    "Renault": [
        {"algo_driven_data__body__iexact": "Coupe"},
    ],

    "Toyota": [
        {"algo_driven_data__body__iexact": "Coupe"},
    ],

    "Volkswagen": [
        {"algo_driven_data__body__iexact": "Coupe"},
        {"model__name": "Golf", "algo_driven_data__variant__startswith": "GTI"},
        {"model__name": "Golf", "algo_driven_data__variant": "R"},
    ],

    "Volvo": [
        {"algo_driven_data__body__iexact": "Coupe"},
        {"algo_driven_data__variant": "Polestar"},
    ],
}

WATANIA_4_ALLOWED_VEHICLES = {
    'Lexus': [
        {"algo_driven_data__body__iexact": "Sedan"},
        {"algo_driven_data__body__iexact": "Hatchback"},
    ],
    'Toyota': [
        {"algo_driven_data__body__iexact": "Sedan"},
        {"algo_driven_data__body__iexact": "Hatchback"},
    ],
    'Nissan': [
        {"algo_driven_data__body__iexact": "Sedan"},
        {"algo_driven_data__body__iexact": "Hatchback"},
    ],
    'Infiniti': [
        {"algo_driven_data__body__iexact": "Sedan"},
        {"algo_driven_data__body__iexact": "Hatchback"},
    ]
}

WATANIA_EDGE_ALLOWED_VEHICLES = {
    'Lexus': [],
    'Toyota': [],
    'Nissan': [],
    'Infiniti': [
        {"model__name": "QX56"},
        {"model__name": "QX80"},
    ],
    'Mitsubishi': [
        {"model__name": "Pajero"}
    ]
}


class WataniaAutoQuoter(CustomRateBooksBase):
    api_url = settings.AUTO_QUOTERS['watania']['api_url']
    product_code_format_str = 'Watania Insurance ({})'
    insurer = constants.WATANIA
    insurer_ratebook_name = 'watania'

    def get_quote_for_insurer_with_deal(self, insurer, deal, form_data):
        self.setup_for_company(deal.company)

        common_checks_passed, reason = passes_common_auto_quoting_checks(deal, form_data)
        if not common_checks_passed:
            return [{
                'name': 'Watania Insurance (Agency & Non-Agency)',
                'exception': True,
                'message': reason
            }]

        if form_data["vehicle_type"] == "COUPE":
            return [{
                'name': 'Watania Insurance (Agency & Non-Agency)',
                'exception': True,
                'message': "This vehicle must be referred to the insurer for underwriting."
            }]

        if deal.car_make.name in EXCLUDED_VEHICLES_FILTERS and deal.car_trim:
            vehicle_excluded = False

            excluded_check_filters = EXCLUDED_VEHICLES_FILTERS[deal.car_make.name]
            if excluded_check_filters == []:
                vehicle_excluded = True
            else:
                for qs_filters in excluded_check_filters:
                    if deal.car_trim in CarTrim.objects.filter(**qs_filters, model__make=deal.car_make):
                        vehicle_excluded = True
                        break

            if vehicle_excluded:
                return [{
                    'name': 'Watania Insurance (Agency & Non-Agency)',
                    'exception': True,
                    'message': "This vehicle must be referred to the insurer for underwriting."
                }]

        formatted_quotes = []

        request_data = self.prepare_request_data(deal, form_data)

        request_data['deal']['vehicle_allowed'] = True
        request_data['deal']['vehicle_origin'] = 'JAPAN' if deal.car_make.name in [
            'Toyota', 'Lexus','Nissan', 'Honda', 'Suzuki', 'Mazda', 'Daihatsu', 'Subaru', 'Mitsubishi',
        ] else 'NOT JAPAN'

        watania_4_allowed = False
        if deal.car_make.name in WATANIA_4_ALLOWED_VEHICLES:
            included_vehicle_filters = WATANIA_4_ALLOWED_VEHICLES[deal.car_make.name]

            if included_vehicle_filters:
                for qs_filters in included_vehicle_filters:
                    if deal.car_trim in CarTrim.objects.filter(**qs_filters, model__make=deal.car_make):
                        watania_4_allowed = True
                        break

        watania_edge_allowed = False
        if form_data['vehicle_type'] == '4WD' and deal.car_make.name in WATANIA_EDGE_ALLOWED_VEHICLES:
            included_vehicle_filters = WATANIA_EDGE_ALLOWED_VEHICLES[deal.car_make.name]

            if included_vehicle_filters:
                for qs_filters in included_vehicle_filters:
                    if deal.car_trim in CarTrim.objects.filter(**qs_filters, model__make=deal.car_make):
                        watania_edge_allowed = True
                        break
            else:
                watania_edge_allowed = True

        request_data['vehicle_data'] = {'iv_allowed': watania_4_allowed, 'edge_allowed': watania_edge_allowed}

        try:
            quotes_response = requests.post(urljoin(self.api_url, '/rates'), json=request_data, timeout=30)
        except requests.Timeout:
            logger.error('WataniaAutoQuoter: Request to Watania Auto Quoter timed out')
            raise AutoQuoterException('The API failed to respond. Please try later')

        try:
            quotes_response.raise_for_status()
        except requests.HTTPError as e:
            logger.error('WataniaAutoQuoter: Error while trying to use Watania Auto Quoter. Status Code: %s Error: %s',
                         quotes_response.status_code, str(e))
            raise AutoQuoterException('API exception. Please check with Felix support.')

        self.add_record_to_insurance_logs(deal, request_data, quotes_response)

        quotes = quotes_response.json()
        for quote in quotes:
            agency = quote['type'] == 'agency'

            readable_product_type = self.api_product_type_to_readable(quote["type"])
            generic_product_code = self.api_product_to_generic_product_code(quote)

            if not quote.get('canInsure', True):
                formatted_quotes.append({
                    'name': generic_product_code,
                    'exception': True,
                    'message': quote['trace']
                })
                continue

            if generic_product_code not in self.config['mapping']:
                logger.warning('WataniaAutoQuoter: Mapping not configured for product code %s', generic_product_code)
                continue

            product_code = self.config['mapping'][generic_product_code]

            premium_with_vat = quote['premium'] * 1.05

            formatted_quotes.append({
                'productCode': product_code,
                'quoteReference': '',
                'insuredCarValue': form_data['insured_value'],
                'canInsure': True,
                'referralRequired': False,
                'agencyRepair': agency,
                'premium': premium_with_vat,
                'deductible': quote['deductable'],
                'rulesTrace': quote['trace']
            })

        return formatted_quotes

    def api_product_type_to_readable(self, product_type):
        return {
            'agency': 'Agency',
            'nonagency': 'Non-Agency',
            'dynatrade': 'DynaTrade',
            'premier': 'Premier Garage',
        }[product_type]

    def api_product_to_generic_product_code(self, quote):
        # Comes from the PHP API. Can be one of: Comprehensive, Hvv, Iv, Edge
        product_name = quote["product_name"]
        # Comes from the PHP API. Can be one of: Agency, NonAgency, Dynatrade, Premier
        product_type = quote["type"]

        readable_product_name = {
            'COMPREHENSIVE': 'Comprehensive',
            'HVV': 'HVV',
            'IV': 'IV',
            'EDGE': 'Edge'
        }[product_name]
        readable_type_name = self.api_product_type_to_readable(product_type)

        return f'{readable_product_name} ({readable_type_name})'
