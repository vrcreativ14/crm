from django.views.generic import DetailView
from healthinsurance.models.quote import Order
from dateutil.relativedelta import relativedelta
import datetime


class OrderPDFView(DetailView):
    model = Order

    slug_field = "reference_number"
    slug_url_kwarg = "reference_number"
    query_pk_and_slug = True

    template_name = "healthinsurance/order/order_pdf.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order = self.get_object()
        order = self.object
        deal = order.deal
        selected_quoted_product = order.selected_plan
        ctx['deal'] = deal
        ctx['order'] = order
        return ctx