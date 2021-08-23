import datetime
import json

from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import modelformset_factory
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import Http404
from django.http.response import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic import DetailView, TemplateView, View, FormView

from core.utils import log_user_activity
from motorinsurance.forms import MotorInsuranceQuoteForm, MotorInsuranceQuotedProductForm
from motorinsurance.forms.quote import OrderForm, Quote, QuoteSearchAndOrderingForm
from motorinsurance.models import Deal
from motorinsurance.models import PaymentRecord
from motorinsurance.models import Quote, QuotedProduct
from motorinsurance.resources import QuoteResource
from motorinsurance_shared.models import Product

from felix.constants import ITEMS_PER_PAGE

from core.email import Emailer

from motorinsurance.tasks import perform_successful_product_selection
from motorinsurance.tasks import removed_selected_product_and_add_a_note


class UploadDocumentView(DetailView):
    template_name = "motorinsurance/order/documents.djhtml"
    model = Quote

    slug_field = "reference_number"
    slug_url_kwarg = "reference_number"
    query_pk_and_slug = True

    def get_object(self):
        obj = super().get_object()

        if obj.status != Quote.STATUS_PUBLISHED:
            raise Http404()

        return obj

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        quote = self.get_object()
        selected_product_details = self.object.selected_product_details

        try:
            ctx['product'] = quote.get_all_quoted_products().get(
                pk=selected_product_details.get('quoted_product_id', None))
        except Exception:
            raise Http404()

        ctx['quote'] = quote
        ctx['user_data'] = self.get_user_data()

        ctx['selected_product_details'] = selected_product_details
        ctx['selected_addons'] = self.get_cleaned_add_ons(selected_product_details['addons'])
        ctx['expired'] = False if selected_product_details else not self.object.is_active()

        ctx['drafted_product'] = None
        ctx['identify_user'] = False
        ctx['note'] = self.object.note

        return ctx

    def get_cleaned_add_ons(self, addons):
        if addons:
            return [addon.replace('_', ' ') for addon in addons]

        return addons

    def get_user_data(self):
        customer = self.object.deal.customer
        customer_age = None

        if customer.dob:
            difference = relativedelta(datetime.datetime.now(), customer.dob)
            customer_age = "{} years".format(difference.years)

        return {
            'quote_pk': self.object.pk,
            'ref_number': self.object.reference_number,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'age': customer_age,
            'uae_license_age': customer.motorinsurancecustomerprofile.uae_license_age,
            'nationality': customer.get_nationality_display(),
            'vehicle': self.object.deal.car_trim.get_full_title(),
            'insured_value': float(self.object.insured_car_value),
        }
