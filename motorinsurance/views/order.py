import datetime

from core.pdf import PDF

from dateutil.relativedelta import relativedelta
from django.views.generic import DetailView

from motorinsurance.models.quote import Order
from motorinsurance.resources import QuoteResource


class OrderPDFView(DetailView):
    model = Order
    template_name = "motorinsurance/order/order_pdf.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        order = self.object
        deal = order.deal
        quote = deal.quote
        selected_quoted_product = order.selected_product

        selected_add_ons = order.selected_add_ons or []
        default_add_ons = selected_quoted_product.default_add_ons or []

        all_add_ons = selected_add_ons + default_add_ons

        if deal.customer.dob:
            difference = relativedelta(datetime.datetime.now(), deal.customer.dob)
            customer_age = "{} years".format(difference.years)
        else:
            customer_age = '-'

        qr = QuoteResource()

        ctx['deal'] = deal
        ctx['order'] = order
        ctx['customer_age'] = customer_age
        ctx['addons'] = ', '.join([addon.replace('_', ' ') for addon in all_add_ons])
        ctx['tier_1_attributes'] = qr.get_tier_1_attributes(quote, selected_quoted_product)
        ctx['tier_2_attributes'] = qr.get_tier_2_attributes(quote, selected_quoted_product)
        ctx['insured_car_value'] = selected_quoted_product.insured_car_value or deal.vehicle_insured_value

        return ctx
