import datetime
import decimal
import json
import logging
import requests

from itertools import islice

from django.conf import settings
from dateutil.relativedelta import relativedelta
from django.http import Http404, JsonResponse, HttpResponseRedirect, HttpResponse
from django.views.generic import DetailView, TemplateView

from core.pdf import PDF
from core.models import Attachment
from motorinsurance.models import Quote, Deal
from motorinsurance.models.quote import Order
from motorinsurance.resources import QuoteResource
from motorinsurance.tasks import add_note_to_deal
from motorinsurance.tasks import perform_successful_product_selection

from core.amplitude import Amplitude

api_logger = logging.getLogger("api.amplitude")


class BaseQuoteView(DetailView):
    model = Quote

    slug_field = "reference_number"
    slug_url_kwarg = "reference_number"
    query_pk_and_slug = True

    def get_object(self, queryset=None):
        quote = super().get_object(queryset)

        if quote.status != Quote.STATUS_PUBLISHED or not quote.deal.is_active():
            self.template_name = "motorinsurance/quote_public/quote_not_active.djhtml"

        return quote

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        quote = self.get_object()
        selected_product_details = self.object.selected_product_details

        try:
            selected_quoted_product = quote.get_all_quoted_products().get(
                pk=selected_product_details.get('quoted_product_id', None))
        except Exception:
            raise Http404()

        ctx['quote'] = quote
        ctx['product'] = selected_quoted_product

        selected_add_ons = selected_product_details['add_ons'] or []
        default_add_ons = selected_quoted_product.default_add_ons or []

        all_add_ons = selected_add_ons + default_add_ons

        ctx['user_data'] = self.get_user_data()

        ctx['selected_product_details'] = selected_product_details

        ctx['all_add_ons'] = self.get_cleaned_add_ons(all_add_ons)
        ctx['editable'] = self.is_editable()

        ctx['quote_sent'] = quote.deal.stage == Deal.STAGE_QUOTE
        ctx['product_selected'] = quote.deal.stage == Deal.STAGE_ORDER

        quoted_product = quote.get_quoted_product_by_id(selected_product_details['quoted_product_id'])

        insured_value = quoted_product.insured_car_value or quote.deal.vehicle_insured_value

        ctx['insured_car_value'] = insured_value

        return ctx

    def get_cleaned_add_ons(self, addons):
        if addons:
            return [addon.replace('_', ' ') for addon in addons]

        return addons

    def get_quote_status_and_details(self):
        quote = self.get_object()
        status = True
        error_message = ''

        if not quote.is_active():
            error_message = "Quote has expired."
            status = False

        selected_quoted_product_id = self.request.POST.get("quoted_product_id", None)
        selected_add_ons = self.request.POST.getlist("addons[]")

        if not selected_quoted_product_id and quote.selected_product_details:
            selected_quoted_product_id = quote.selected_product_details['quoted_product_id']
            selected_add_ons = quote.selected_product_details['add_ons']

        quoted_product = quote.get_quoted_product_by_id(
            selected_quoted_product_id
        )

        if quoted_product is None:
            error_message = "This quote does not contain a product with id {}".format(
                selected_quoted_product_id)
            status = False

        product = quoted_product.product

        product_columns = [f.name for f in product._meta.get_fields()]

        for sa in selected_add_ons:
            if sa not in product_columns:
                error_message = "The selected product does not have the add-on you selected ({})".format(
                    sa)
                status = False

        return quote, product, selected_quoted_product_id, selected_add_ons, status, error_message

    def get_user_data(self):
        customer = self.object.deal.customer

        if customer.dob:
            difference = relativedelta(datetime.datetime.now(), customer.dob)
            customer_age = "{} years".format(difference.years)
        else:
            customer_age = '-'

        return {
            'quote_pk': self.object.pk,
            'ref_number': self.object.reference_number,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'age': customer_age,
            'nationality': customer.get_nationality_display(),
            'uae_license_age': customer.motorinsurancecustomerprofile.uae_license_age,
            'vehicle': self.object.deal.get_car_title(),
            'insured_value': float(self.object.insured_car_value),
            'pdf_download_url': self.object.get_download_pdf_url('e-commerce')
        }

    def is_editable(self):
        if not self.object.is_active():  # or not self.object.deal.is_publicly_modifiable():
            return False

        return True


class QuoteComparisonView(BaseQuoteView):
    template_name = "motorinsurance/quote_public/quote_comparison.djhtml"

    def get(self, request, *args, **kwargs):
        response = super(QuoteComparisonView, self).get(request, *args, **kwargs)

        quote = self.object
        if not self.request.user.is_authenticated:
            quote.number_of_views += 1
            quote.save()
            quote.deal.update_in_algolia()

        return response

    def get_context_data(self, *args, **kwargs):
        selected_product_details = self.object.selected_product_details
        products = QuoteResource.generate_frontend_data_from_quote(self.object)

        ctx = dict()
        ctx['quote'] = self.object
        ctx['user_data'] = json.dumps(self.get_user_data())
        ctx['products_data'] = json.dumps(products)
        ctx['payment_captured'] = False
        ctx['selected_product_details'] = selected_product_details
        ctx['expired'] = not self.object.is_active()
        ctx['editable'] = self.is_editable()
        ctx['is_product_selected'] = self.object.deal.stage == Deal.STAGE_ORDER
        ctx['note'] = self.object.note

        return ctx


class QuoteOrderSummaryView(BaseQuoteView):
    template_name = "motorinsurance/quote_public/quote_order_summary.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['amount'] = '{0:.2f}'.format(self.get_payment_amount())
        ctx['order_terms'] = self.request.company.companysettings.get_order_terms_as_list()

        return ctx

    def get(self, request, reference_number, pk, *args, **kwargs):
        quote = self.get_object()

        return super().get(request, reference_number, pk)

    def get_payment_amount(self):
        quote = self.object

        selected_product_details = quote.selected_product_details
        selected_quoted_product = quote.get_all_quoted_products().get(
            pk=selected_product_details.get('quoted_product_id', None))

        selected_add_ons = selected_product_details.get('add_ons', [])
        premium = selected_quoted_product.get_sale_price()
        product = selected_quoted_product.product

        final_price = QuoteResource.get_price_for_product_with_premium_and_add_ons(quote, product, premium,
                                                                                   selected_add_ons)
        # Needs to be a float to avoid issues with JSON serialization all over the place
        return float(final_price)


class QuoteDocumentsUploadView(BaseQuoteView):
    template_name = "motorinsurance/quote_public/document_upload.djhtml"

    def get(self, request, reference_number, pk):
        quote = self.get_object()

        # if not quote.deal.is_publicly_modifiable():
        # return HttpResponseRedirect(reverse('motorinsurance:quote-upload-documents-success'))

        return super().get(request, reference_number, pk)

    def post(self, request, reference_number, pk):
        quote = self.get_object()
        deal = quote.deal
        customer = deal.customer

        if not len(request.FILES):
            return JsonResponse({})

        attachment = Attachment(company=request.company, attached_to=deal)
        file = list(request.FILES.values())[0]
        attachment.label = f'Customer Uploaded: {file.name}'
        attachment.file = file
        attachment.save()

        return JsonResponse({
            'success': True,
            'url': attachment.get_file_url()
        })


class SelectProductView(BaseQuoteView):
    def post(self, request, reference_number, pk):
        quote, product, qp_id, add_ons, status, error_message = self.get_quote_status_and_details()

        if status:
            perform_successful_product_selection(quote, product, qp_id, add_ons)

        return JsonResponse({'status': status, 'error_message': error_message})


class QuoteProductSelectionAndDocumentUploadView(BaseQuoteView):
    def post(self, request, reference_number, pk):
        response = {}
        quote, product, qp_id, add_ons, status, error_message = self.get_quote_status_and_details()

        if request.POST.get('policy_start_date'):
            policy_start_date_str = request.POST['policy_start_date']
            policy_start_date = datetime.datetime.strptime(policy_start_date_str, "%d-%m-%Y")
        else:
            policy_start_date = datetime.datetime.now()
            policy_start_date_str = policy_start_date.strftime('%d-%m-%Y')

        bank_finance = request.POST.get('bank_finance', None)
        promo_code = request.POST.get('promo_code', None)

        deal = quote.deal
        order = deal.get_order()

        if request.GET['st'] == 'ps':  # product_selected
            formatted_add_ons = ''
            for add_on in add_ons:
                formatted_add_ons += f'<span class="badge badge-info">{add_on}</span> '

            if formatted_add_ons:
                formatted_add_ons = f' with Add Ons {formatted_add_ons} '

            formatted_bank_finance = f'<span class="badge badge-info">{bank_finance}</span>' if bank_finance \
                else 'n/a'
            formatted_policy_start_date = f'<span class="badge badge-info">{policy_start_date_str}</span>' if \
                policy_start_date else 'n/a'

            order = Order(
                deal=deal,
                selected_product_id=qp_id,
                selected_add_ons=add_ons,
                policy_start_date=policy_start_date,
                mortgage_by=bank_finance,
                created_by_agent=False,
                payment_amount=QuoteResource.get_price_for_quoted_product_with_add_ons(
                    quote, quote.products.get(pk=qp_id), add_ons
                )
            )

            order.save()

            deal.stage = Deal.STAGE_ORDER
            deal.save()

            perform_successful_product_selection(quote, product, qp_id, add_ons, policy_start_date_str, bank_finance,
                                                 send_email=True, send_sms=True)

            note_content = (
                f'Customer selected a product <span class="badge badge-primary">{product}</span>'
                f'{formatted_add_ons}, Bank Finance: {formatted_bank_finance}, Policy Start Date: '
                f'{formatted_policy_start_date}'
            )

            if promo_code:
                note_content = f'{note_content} <br>with a promo code <span class="badge badge-warning">{promo_code}</span>'

            car_model = ''
            car_body_type = ''

            if deal.car_trim:
                car_model = deal.car_trim.model.name
                car_body_type = deal.car_trim.algo_driven_data.get('body', '')

            response = {
                'deal_id': deal.pk,
                'deal_created_date': deal.created_on.isoformat(),

                'product': order.selected_product.product.name,
                'insurer': order.selected_product.product.insurer.name,
                'cover': 'TPL' if order.selected_product.product.is_tpl_product else 'comprehensive',
                'premium': '{}'.format(order.payment_amount),
                'discounted_premium': 'yes' if order.selected_product.premium != order.selected_product.sale_price else 'no',
                'repair_type': 'agency' if order.selected_product.agency_repair else 'non-agency',
                'views': quote.number_of_views if quote else 0,

                'vehicle_model_year': deal.car_year,
                'vehicle_make': deal.car_make.name,
                "vehicle_model": car_model,
                "vehicle_body_type": car_body_type,
                'vehicle_sum_insured': '{}'.format(
                    float(order.selected_product.insured_car_value) or deal.vehicle_insured_value),

                'client_email': deal.customer.email,
                'client_email_hash': deal.customer.get_email_hash(),
                'client_nationality': deal.customer.get_nationality_display(),
                'client_gender': deal.customer.get_gender_display(),
                'client_age': deal.customer.get_age(),

                'status': True,
                'error_message': error_message
            }
        elif request.GET['st'] == 'dc':  # documents_collected
            note_content = 'Customer has submitted the documents'
            response = {'status': status, 'error_message': error_message}

        add_note_to_deal(quote.deal, note_content)

        return JsonResponse(response)


class QuoteDocumentsUploadSuccessView(TemplateView):
    template_name = "motorinsurance/quote_public/document_upload_thankyou.djhtml"


class QuoteTermsAndConditionsView(TemplateView):
    template_name = "motorinsurance/quote_public/terms_and_conditions.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        term_url = self.request.company.companysettings.terms_and_conditions_url

        if not term_url:
            raise Http404()

        ctx['terms_url'] = term_url

        return ctx


class QuotePDFView(DetailView):
    model = Quote

    slug_field = "reference_number"
    slug_url_kwarg = "reference_number"
    query_pk_and_slug = True

    template_name = "motorinsurance/quote_public/quote_pdf.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        quote = self.get_object()
        deal = quote.deal

        ctx['deal'] = deal

        products_data = QuoteResource.generate_frontend_data_from_quote(quote)

        for product in products_data:
            for attribute in product['tier_1_attributes']:
                attribute['default'] = attribute['type'] == 'addon' and attribute['code'] in product['default_addons']
            for attribute in product['tier_2_attributes']:
                attribute['default'] = attribute['type'] == 'addon' and attribute['code'] in product['default_addons']

        product_sets = list(self.get_chunks(products_data, 3))
        formatted_products_data = list()

        for product_set in product_sets:
            formatted_products_data.append({
                'products': product_set,
                'tier_1_attributes': zip(*map(lambda x: x['tier_1_attributes'], product_set)),
                'tier_2_attributes': zip(*map(lambda x: x['tier_2_attributes'], product_set)),
            })

        ctx['product_sets'] = formatted_products_data
        ctx['currency'] = deal.company.companysettings.get_currency_display() or 'Dhs'

        if deal.customer.dob:
            difference = relativedelta(datetime.datetime.now(), deal.customer.dob)
            ctx['customer_dob'] = "{} years".format(difference.years)
        else:
            ctx['customer_dob'] = '-'

        return ctx

    def get_chunks(self, data, size):
        data = iter(data)
        return iter(lambda: tuple(islice(data, size)), ())


class QuotePDFDownloadView(DetailView):
    model = Quote

    slug_field = "reference_number"
    slug_url_kwarg = "reference_number"
    query_pk_and_slug = True

    template_name = None

    def get(self, request, *args, **kwargs):
        quote = self.get_object()

        file_name = '{} Quote Reference {}.pdf'.format(
            self.request.company.name,
            quote.reference_number
        )

        source = quote.get_pdf_url()

        response = PDF().convert(source, filename=file_name)

        try:
            Amplitude(self.request).log_event(Amplitude.EVENTS['pdf_quote_downloaded'], {
                'source': request.GET.get('source'),
                'deal_id': quote.deal.pk
            })
        except Exception as e:
            api_logger.error('Amplitude error while logging "pdf quote downloaded" Source: %s, Error: %s', source, e)

        return response
