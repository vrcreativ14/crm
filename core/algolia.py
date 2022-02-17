"""Algolia Search"""
from django.conf import settings
from algoliasearch import algoliasearch
from django.utils.timezone import localtime


class Algolia:
    def __init__(self):
        self.client = algoliasearch.Client(
            settings.ALGOLIA['APPLICATION_ID'], settings.ALGOLIA['API_KEY'])

    def get_secured_search_api_key(self, indices='', filters=''):
        return self.client.generateSecuredApiKey(
            settings.ALGOLIA['SEARCH_API_KEY'],
            {
                'filters': filters
            }
        )

    def get_index(self, index_name):
        return self.client.init_index(index_name)

    def set_index_settings(self, index_name, settings):
        self.get_index(index_name).set_settings(settings)

    def upsert_motor_deal_record(self, deal):
        index = self.get_index(self.get_index_name('motor_deals', deal.company.pk))

        premium = 0
        renewal_policy = ''
        renewal_policy_id = 0
        order = deal.get_order()

        if deal.quote:
            lqp = deal.quote.get_least_quoted_product()
            if lqp:
                premium = lqp.get_sale_price()

        if order:
            premium = order.payment_amount

        if deal.renewal_for_policy:
            renewal_policy = deal.renewal_for_policy
            renewal_policy_id = deal.renewal_for_policy.pk

        index.add_object({
            'objectID': deal.pk,
            'company_id': deal.company.id,
            'company_name': deal.company.name,

            'deal_type': deal.deal_type,
            'deal_type_display': deal.get_deal_type_display(),

            'customer_id': deal.customer.id,
            'customer_name': deal.customer.name,
            'customer_email': deal.customer.email,
            'customer_phone': deal.customer.phone,
            'customer_nationality': deal.customer.get_nationality_display(),
            'customer_dob': deal.customer.dob.strftime('%b %d, %Y') if deal.customer.dob else '',

            'stage': deal.stage,
            'car_year': deal.car_year,
            'car_make': deal.car_make.name if deal.car_make else '',
            'custom_car_name': deal.custom_car_name,
            'cached_car_name': deal.cached_car_name,
            'vehicle_insured_value': deal.vehicle_insured_value,
            'premium': premium,

            'assigned_to_id': deal.assigned_to.pk if deal.assigned_to else 0,
            'assigned_to_name': deal.assigned_to.get_full_name() if deal.assigned_to else 'Unassigned',

            'producer_id': deal.producer.pk if deal.producer else 0,
            'producer_name': deal.producer.get_full_name() if deal.producer else 'Unassigned',

            'created_on': localtime(deal.created_on),
            'updated_on': localtime(deal.updated_on),

            'tags': deal.get_tags(),

            'renewal_for_policy_id': renewal_policy_id,
            'renewal_for_policy': renewal_policy,

            'status': 'deleted' if deal.is_deleted else 'active',

            'created_on_display': localtime(deal.created_on).strftime('%b %d, %Y'),
            'updated_on_display': localtime(deal.updated_on).strftime('%b %d, %Y'),
        })

        if hasattr(deal, 'policy'):
            self.upsert_motor_policy_record(deal.policy)

        if renewal_policy:
            self.upsert_motor_policy_record(renewal_policy)

    def upsert_motor_policy_record(self, policy):
        index = self.get_index(self.get_index_name('motor_policies', policy.company.pk))
        deal = policy.deal

        renewal_deal = ''
        renewal_deal_id = ''
        renewal_deal_stage = ''
        renewal_deal_status = ''

        renewal_deal_obj = policy.get_renewal_deal()

        if renewal_deal_obj and not renewal_deal_obj.is_deleted:
            renewal_deal = renewal_deal_obj
            renewal_deal_id = renewal_deal.pk
            renewal_deal_stage = renewal_deal.stage
            renewal_deal_status = renewal_deal.get_tags()

        index.add_object({
            'objectID': policy.pk,
            'company_id': policy.company.id,
            'company_name': policy.company.name,

            'deal_id': deal.pk if deal else '',
            'deal_title': deal.get_car_title() if deal else '',

            'owner_id': policy.owner_id,
            'owner_name': policy.owner.get_full_name() if policy.owner else '',

            'customer_id': policy.customer.id,
            'customer_name': policy.customer.name,
            'customer_email': policy.customer.email,
            'customer_phone': policy.customer.phone,
            'customer_nationality': policy.customer.get_nationality_display(),
            'customer_dob': policy.customer.dob.strftime('%b %d, %Y') if policy.customer.dob else '',

            'car_year': policy.car_year if policy.car_year else '',
            'car_make': policy.car_make.name if policy.car_make else '',
            'car_trim': policy.car_trim if policy.car_trim else '',
            'custom_car_name': policy.custom_car_name,

            'policy_title': policy.get_title(),
            'reference_number': policy.reference_number,
            'invoice_number': policy.invoice_number,
            'insurance_type': policy.get_insurance_type_display(),
            'agency_repair': policy.agency_repair,
            'ncd_required': policy.ncd_required,
            'premium': policy.premium,
            'deductible': policy.deductible,
            'deductible_extras': policy.deductible_extras,
            'car_value': policy.insured_car_value,
            'mortgage_by': policy.mortgage_by,
            'default_add_ons': policy.default_add_ons,
            'paid_add_ons': policy.paid_add_ons,
            'status': policy.status,

            'product_id': policy.product.pk if policy.product else '',
            'product_name': policy.product.name if policy.product else '',
            'custom_product_name': policy.custom_product_name,
            'insurer_id': policy.product.insurer.pk if policy.product else '',
            'insurer_name': policy.product.insurer.name if policy.product else '',

            'renewal_deal': renewal_deal,
            'renewal_deal_id': renewal_deal_id,
            'renewal_deal_stage': renewal_deal_stage,
            'renewal_deal_status': renewal_deal_status,
            'has_renewal_deal': bool(renewal_deal),

            'policy_start_date': int(policy.policy_start_date.strftime('%s')),
            'policy_expiry_date': int(policy.policy_expiry_date.strftime('%s')),
            'policy_start_date_display': policy.policy_start_date.strftime('%b %d, %Y'),
            'policy_expiry_date_display': policy.policy_expiry_date.strftime('%b %d, %Y'),

            'created_on': localtime(policy.created_on),
            'updated_on': localtime(policy.updated_on),
            'created_on_display': localtime(policy.created_on).strftime('%b %d, %Y'),
            'updated_on_display': localtime(policy.updated_on).strftime('%b %d, %Y'),
        })

    def upsert_customer_record(self, customer):
        index = self.get_index(self.get_index_name('customers', customer.company.pk))

        index.add_object({
            'objectID': customer.pk,
            'company_id': customer.company.name,
            'company_name': customer.company.name,

            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'nationality': customer.get_nationality_display(),
            'phone_number_suffixes': self.get_possible_suffixes(customer.phone),

            'status': customer.status,
            'entity': customer.entity,
            'created_on': localtime(customer.created_on),
            'updated_on': localtime(customer.updated_on),

            'created_on_display': localtime(customer.created_on).strftime('%b %d, %Y'),
            'updated_on_display': localtime(customer.updated_on).strftime('%b %d, %Y'),
        })

        if not customer.entity == "Mortgage":
            for deal in customer.get_motor_deals():
                self.upsert_motor_deal_record(deal)

    def get_possible_suffixes(self, string):
        suffixes = list()
        if string:
            suffixes = [string[i:] for i in range(0, len(string))]

        return suffixes

    def get_index_name(self, name, company_id):
        return '{}_{}_{}'.format(settings.ALGOLIA['ENV'], name, company_id)
