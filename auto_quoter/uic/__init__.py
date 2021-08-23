import logging

from auto_quoter.auto_quoter_base import AutoQuoterBase
from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.models import AutoQuoterConfig
from auto_quoter.uic.rate_book_standard import UICStandardRateBook
from auto_quoter.uic.rate_book_superior import UICSuperiorRateBook
from auto_quoter.uic.nexus_rate_books import NexusSilverRateBook
from auto_quoter.uic.nexus_rate_books import NexusGoldRateBook


class UICAutoQuoter(AutoQuoterBase):
    """Auto quoter for Union Insurance Company"""
    rate_book_classes = [UICStandardRateBook, UICSuperiorRateBook]

    def __init__(self):
        super().__init__()
        self.log = logging.getLogger('auto_quoter.uic')

    def get_deal_missing_data_fields(self, deal):
        missing_fields = []

        customer = deal.customer

        if customer.dob is None:
            missing_fields.append('customer.dob')

        if deal.get_age_of_car_since_registration() is None:
            missing_fields.append('deal.date_of_first_registration')

        customer_profile = customer.motorinsurancecustomerprofile
        if not customer_profile.uae_license_age:
            missing_fields.append('customer_profile.uae_license_age')

        return missing_fields

    def get_product_code_for_scheme_name(self, scheme_name):
        try:
            return self.config['mapping'][scheme_name]
        except KeyError:
            return None

    def get_quote_for_insurer_with_deal(self, insurer, deal, form_data):
        self.log.info('UICAutoQuoter: Generating quote with deal id %d and form data %s', deal.pk, form_data)

        self.setup_for_company(deal.company)

        quotes = []

        for rate_book_class in self.rate_book_classes:
            rate_book = rate_book_class()
            can_quote, reason = rate_book.can_generate_quote(deal, form_data)
            if not can_quote:
                quotes.append({
                    'name': rate_book.generate_name_for_product_we_cant_quote(deal, form_data,
                                                                              ' (Non-Agency and Agency)'),
                    'exception': True,
                    'message': reason
                })
            else:
                this_rate_book_quotes = rate_book.get_quotes(deal, form_data)

                for quote in this_rate_book_quotes:
                    if quote.get('exception'):
                        quotes.append(quote)
                        continue

                    scheme_name = quote['productCode']
                    our_product_code = self.get_product_code_for_scheme_name(scheme_name)

                    if our_product_code is None:
                        self.log.warning('UICAutoQuoter: Unable to map scheme name %s to a product in our DB. '
                                         'Please check auto quoter configuration for UIC and company %s', scheme_name,
                                         deal.company.name)
                        continue

                    self.log.info('UICAutoQuoter: Mapped scheme name %s to our product code %s', scheme_name,
                                  our_product_code)
                    quote['productCode'] = our_product_code

                    quotes.append(quote)

        return quotes

    def setup_for_company(self, company):
        self.log.debug('UICAutoQuoter: Setting up self for company %s', company.name)
        self.company = company
        try:
            self.config = AutoQuoterConfig.objects.get(company=company, insurer='uic').get_options_dict()
        except AutoQuoterConfig.DoesNotExist:
            raise AutoQuoterException('The UIC auto quoter is not configured')

        custom_rate_book = self.config.get('ratebook')
        if custom_rate_book == 'nexus':
            self.rate_book_classes = [NexusSilverRateBook, NexusGoldRateBook]
        elif custom_rate_book == 'eiib':
            self.rate_book_classes = [EIIBSuperiorRateBook, EIIBAutoTrustGarageRepairRateBook]
