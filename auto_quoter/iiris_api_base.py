"""Iiris is a product by Assure Tech that insurance companies use to power their APIs.

For now, we have two insurers using this product; Tokio Marine and DAT. This is the base class we can use to build the
integration.

P.S: We have limited data to judge how much common items there are in the integrations. This common class is being made
as an experiment to see how much we can abstract the API."""
import logging
import json

import zeep.client
from django.core.exceptions import ImproperlyConfigured

from auto_quoter.auto_quoter_base import AutoQuoterBase
from auto_quoter.constants import TOKIO_MARINE_API
from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.models import AutoQuoterConfig


class IirisApiBase(AutoQuoterBase):
    name = None
    wsdl_url = None

    def __init__(self):
        if self.name is None or self.wsdl_url is None:
            raise ImproperlyConfigured('Name or WSDL URL must be set')

        super(IirisApiBase, self).__init__()

        """
            When logging in this class, use it similar to:
                
                `self.log.error(f'{self.name}: Your message here. Information on the error: %s', error_info)`
                
            The reason we use the `{self.name}` as part of the F-String is so that in Sentry, errors from each instance
            of IirisApiBase are logged separately.
            
            We still use the placeholders (%s) so that the same error does not get logged as a unique error type if the
            only difference is the details of the error info.
        """
        self.log = logging.getLogger('auto_quote.iiris')

        self.client = zeep.client.Client(self.wsdl_url)

        self.username = None
        self.password = None
        self._auth_token = None

    def ensure_login(self):
        assert self._auth_token is not None, "Login token not set"

    def login(self):
        self.log.debug(f'{self.name}: Logging in with username %s', self.username)

        login_response = self.client.service.ValidateLogin(self.username, self.password)
        try:
            login_response = json.loads(login_response)
        except (ValueError, TypeError) as e:
            self.log.error(f'{self.name}: Unable to login to API. Exception: %s', e)
            raise AutoQuoterException(f'{self.name}: Unable to login')

        if 'Data' not in login_response or len(login_response['Data']) != 1:
            self.log.error(f'{self.name}: Unable to find token in response data. Data: %s', login_response)
            raise AutoQuoterException(f'{self.name}: Unable to login')

        token_data = login_response['Data'][0]
        if 'Token' not in token_data:
            self.log.error(f'{self.name}: Unable to find token in response data. Data: %s', login_response)
            raise AutoQuoterException(f'{self.name}: Unable to login')

        self._auth_token = token_data['Token']

        return token_data['Token']

    def setup_for_company(self, company):
        self.company = company
        try:
            self.config = AutoQuoterConfig.objects.get(company=company, insurer=TOKIO_MARINE_API).get_options_dict()
        except AutoQuoterConfig.DoesNotExist:
            raise AutoQuoterException(f'The {self.name} auto quoter is not configured')

        self.username = self.config['username']
        self.password = self.config['password']

    def map_auto_quoter_product_to_db_product_code(self, product_code):
        return self.config['mapping'].get(product_code)

    def get_quote_for_insurer_with_deal(self, insurer, deal, form_data):
        """Return an array of quotes. Formats are given below.

        Valid quote:
        {
            'productCode': our_product_code,
            'quoteReference': response_data['quoteRefNo'],
            'insuredCarValue': form_data['insured_value'],
            'canInsure': True,
            'referralRequired': False,
            'agencyRepair': plan['repairCondition'] == 'Dealer Workshop',
            'premium': self.add_taxes(plan['premium']),
            'deductible': plan.get('standardExcess', 0),
            'rulesTrace': ['Got response from Oman API']
        }

        Invalid quote:
        {
            'name': 'New India Agency',
            'exception': True,
            'message': reason
        }
        """
        raise NotImplemented('Subclasses of IirisApiBase must implement this method')
