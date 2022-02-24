import datetime
import json
import logging
import time

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.forms import modelformset_factory
from django.http import Http404
from django.http.response import JsonResponse
from django.urls import reverse
from django.utils.html import strip_tags, escape
from django.views.generic import FormView, TemplateView, UpdateView, View, DetailView

from accounts.models import CompanySettings
from core.algolia import Algolia
from core.amplitude import Amplitude
from core.forms import NoteForm, AttachmentForm, TaskForm
from core.mixins import AjaxListViewMixin, CompanyAttributesMixin, AdminAllowedMixin
from core.models import Attachment
from core.timeline import Timeline
from core.utils import clean_and_validate_email_addresses
from core.utils import log_user_activity, serialize_to_json, is_valid_number, normalize_phone_number
from core.views import AddAttachmentView, DeleteAttachmentView
from core.views import AddNoteView, DeleteNoteView, AddEditTaskView
from customers.models import Customer
from felix.constants import DEFAULT_TIMESLOT, EXPIRED_QUOTE_EXTENSION_DAYS
from felix.exporter import ExportService
from motorinsurance.constants import INSURANCE_TYPES, TOP_TIER_INSURERS, LEAD_TYPES, NO_CLAIMS
from motorinsurance.forms import DealForm, PolicyForm
from motorinsurance.forms import MotorInsuranceQuoteForm, MotorInsuranceQuotedProductForm
from motorinsurance.forms.deal import DealSearchAndOrderingForm
from motorinsurance.forms.quote import OrderForm
from motorinsurance.models import CustomerProfile, Deal, Quote, QuotedProduct
from motorinsurance.tasks import add_note_to_deal, perform_successful_product_selection
from motorinsurance.views.task import TaskBaseView

from motorinsurance_shared.models import Product


api_logger = logging.getLogger("api.amplitude")


class DealBaseView(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = None

    def get_queryset(self):
        query = ''
        filters = ''
        status = 'active'
        facets = []
        facet_filters = list()
        numeric_filters = list()
        sort_by = self.default_sort_by

        so_form = self.get_search_and_ordering_form()
        sort_indexes = ['created_on_asc', 'updated_on_asc', 'updated_on_desc']

        if self.request.GET.get('sort_by') and self.request.GET.get('sort_by') in sort_indexes:
            sort_by = f'_{self.request.GET.get("sort_by")}'

        index_name = f'{settings.ALGOLIA["ENV"]}_motor_deals_{self.request.company.pk}{sort_by}'
        index = Algolia().get_index(index_name)

        if so_form.is_valid():
            cd = so_form.cleaned_data

            if cd['deleted']:
                status = 'deleted'
            facet_filters.append(f'status:{status}')

            if cd['stage']:
                facet_filters.append(f'stage:{cd["stage"]}')

            if cd['assigned_to']:
                assigned_to = 0 if cd['assigned_to'] == 'unassigned' else cd['assigned_to']
                facet_filters.append([f'assigned_to_id:{assigned_to}', f'producer_id:{assigned_to}'])

            if cd['created_on_after']:
                numeric_filters.append('created_on >= {}'.format(time.mktime(cd['created_on_after'].timetuple())))
            if cd['created_on_before']:
                numeric_filters.append('created_on <= {}'.format(time.mktime(cd['created_on_before'].timetuple())))

            if cd['search_term']:
                query = cd['search_term']

        if self.request.user.userprofile.has_producer_role():
            facet_filters.append(f'producer_id:{self.request.user.pk}')

        params = {
            'query': query,
            'filters': filters,
            'facets': facets,
            'facetFilters': facet_filters,
            'numericFilters': numeric_filters,
            'attributesToRetrieve': ['objectID', 'customer_name', 'cached_car_name'],
            'attributesToHighlight': [],
            'attributesToSnippet': [],
        }

        return index.browse_all(params)

    def get_search_and_ordering_form(self):
        return DealSearchAndOrderingForm(data=self.request.GET, company=self.request.company)


class DealEditBaseView(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = None

    def get_object(self, **kwargs):
        try:
            filters = {
                'pk': self.kwargs['pk'],
                'company': self.request.company
            }
            deal = Deal.objects.select_related(
                'customer', 'car_make', 'car_trim', 'car_trim__model'
            ).get(**filters)
            if (
                self.request.user.userprofile.has_producer_role() and
                (deal.producer != self.request.user and deal.assigned_to != self.request.user)
            ):
                raise Http404()

            return deal
        except Deal.DoesNotExist:
            raise Http404()

    def serialize_products(self):
        data = dict()

        for product in Product.objects.all().order_by('insurer__name'):
            data[product.id] = {
                'id': product.pk,
                'name': product.name,
                'active': product.is_active,
                'insurer': product.insurer.name,
                'insurer_id': product.insurer_id,
                'code': product.code,
                'allows_agency_repair': product.allows_agency_repair,
                'is_tpl_product': product.is_tpl_product,
                'logo': product.get_logo(),
                'addons': product.get_add_ons(),
            }

        return data

    def get_related_attachments(self):
        deal = self.get_object()
        attachments = self.serialize_attachments(
            deal.customer.get_attachments(),
            deal.customer.name,
            reverse('customers:edit', kwargs=dict(pk=deal.customer.pk))
        )

        deals = Deal.objects.filter(customer=deal.customer).exclude(id=deal.pk)

        for deal in deals:
            attachments = attachments + self.serialize_attachments(
                deal.get_attachments(), deal.get_car_title(),
                reverse('motorinsurance:deal-edit', kwargs=dict(pk=deal.pk)))

        return attachments

    def serialize_attachments(self, attachments, location_label='', location_url=''):
        return [{
            'id': attachment.id,
            'label': attachment.label,
            'url': attachment.get_file_url(),
            'can_preview': attachment.can_preview_in_frontend(),
            'extension': attachment.get_file_extension().upper(),
            'added_by': attachment.added_by.get_full_name() if attachment.added_by else '',
            'created_on': attachment.created_on.strftime('%Y-%m-%d'),
            'location_label': location_label,
            'location_url': location_url,
            'update_url': reverse('core:update-attachment', kwargs={'pk': attachment.id}),
            'url_for_linking': attachment.get_url_for_linking_in_frontend()
        } for attachment in attachments]

    def get_auto_quotable_insurers(self):
        return [{
            'pk': insurer.pk,
            'name': insurer.name
        } for insurer in self.request.company.quotable_motor_insurers.all().order_by('name')]

    # Caching can be added here.
    def get_allowed_insurers(self):
        insurers = dict()

        auto_quotable_insurer_ids = set(
            self.request.company.quotable_motor_insurers.values_list('id', flat=True).all()
        )

        for product in Product.objects.all().order_by('insurer__name'):
            insurer_id = product.insurer_id
            if insurer_id not in insurers:
                insurers[insurer_id] = {
                    'pk': insurer_id,
                    'name': product.insurer.name,
                    'logo': product.insurer.logo.url if product.insurer.logo else '',
                    'auto_quotable': insurer_id in auto_quotable_insurer_ids
                }

        return insurers

    def get_quote(self):
        quote = None
        try:
            quote = self.object.quote
            return self.object.quote
        except Quote.DoesNotExist:
            pass

        return quote


class DealsExportView(DealBaseView, AjaxListViewMixin, View):
    permission_required = 'auth.export_motor_deals'
    default_sort_by = ''

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()

        data = list()
        column_labels = [
            '#',
            'Stage', 'Status', 'Customer', 'Phone', 'Email', 'Nationality', 'DOB', 'First License Country',
            'First License Age', 'UAE License Age', 'First License Issue Date', 'UAE License Issue Date',
            'Year', 'Make', 'Model/Trim', 'Premium', 'Sum Insured', 'Emirate', 'Current Insurance', 'Current Insurer',
            'User', 'Referrer',
            'Created On', 'Updated On']

        deal_ids = [r['objectID'] for r in qs]

        deals = Deal.objects.filter(pk__in=deal_ids)
        counter = 1
        for deal in deals:
            sum_insured = deal.vehicle_insured_value

            customer = deal.customer
            cp = deal.customer.motorinsurancecustomerprofile

            premium = 0
            order = deal.get_order()

            if deal.quote:
                lqp = deal.quote.get_least_quoted_product()
                if lqp:
                    premium = lqp.get_sale_price()

            if order:
                premium = order.payment_amount

            data.append([
                counter,
                deal.get_stage_display(), ', '.join(deal.get_tags()),

                customer.name, customer.phone, customer.email,
                customer.get_nationality_display(), customer.dob,

                cp.get_first_license_country_display(), cp.get_first_license_age_display(),
                cp.get_uae_license_age_display(), cp.first_license_issue_date, cp.uae_license_issue_date,

                deal.car_year, deal.car_make.name, deal.get_car_trim(),
                '{:,}'.format(premium), '{:,}'.format(sum_insured),

                deal.get_place_of_registration_display(), deal.get_current_insurance_type_display(),
                deal.get_current_insurer_display(),
                deal.assigned_to, deal.producer,
                deal.created_on.strftime('%Y-%m-%d'), deal.updated_on.strftime('%Y-%m-%d')
            ])
            counter += 1

        exporter = ExportService()

        return exporter.to_csv(column_labels, data, filename='deals-{}.csv'.format(datetime.datetime.today()))


class DealsView(DealBaseView, AjaxListViewMixin, CompanyAttributesMixin, TemplateView):
    template_name = "motorinsurance/deal/deals_list.djhtml"
    permission_required = 'auth.list_motor_deals'
    default_sort_by = ''

    def get_context_data(self, **kwargs):
        algolia = Algolia()
        filters = ''
        if self.request.user.userprofile.has_producer_role():
            filters = "producer_id:{user_id} OR assigned_to_id:{user_id}".format(user_id=self.request.user.pk)

        ctx = super(DealsView, self).get_context_data(**kwargs)
        self.request.session['selected_product_line'] = 'motorinsurance'

        ctx['algolia_secured_search_api_key'] = Algolia().get_secured_search_api_key(
            filters=filters
        )

        ctx['deal_form'] = DealForm(company=self.request.company, user=self.request.user)

        ctx['search_form'] = self.get_search_and_ordering_form()

        ctx['default_sort_by'] = self.request.GET.get('sort_by') or 'created_on_desc'
        ctx['stage'] = self.request.GET.get('stage', '')
        ctx['page'] = self.request.GET.get('page', 1)

        log_user_activity(self.request.user, self.request.path)

        return ctx


class DealDeleteView(LoginRequiredMixin, AdminAllowedMixin, PermissionRequiredMixin, View):
    permission_required = 'auth.delete_motor_deals'

    def get(self, *args, **kwargs):
        try:
            deal = Deal.objects.get(company=self.request.company, pk=self.kwargs['pk'])
            deal.is_deleted = True
            deal.save(user=self.request.user)

            response = {'success': True}
        except Deal.DoesNotExist:
            response = {'success': False, 'error': 'No record found'}

        return JsonResponse(response, safe=False)


class DealAddView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = 'auth.create_motor_deals'
    form_class = DealForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['user'] = self.request.user
        kwargs['company'] = self.request.company

        return kwargs

    def form_valid(self, form, **kwargs):
        deal = form.save(commit=False)

        deal.car_make_id = form.cleaned_data['car_make']
        deal.car_trim_id = form.cleaned_data['car_trim'] or None
        deal.company = self.request.company
        deal.private_car = form.cleaned_data['private_car'] == 'private'

        if deal.car_trim and deal.car_trim.algo_driven_data:
            number_of_passengers = int(deal.car_trim.algo_driven_data.get('seats')) or 0

            deal.number_of_passengers = number_of_passengers - 1 if number_of_passengers else 0

        if self.request.user.userprofile.has_producer_role():
            deal.producer = self.request.user

        if not form.cleaned_data['customer']:
            customer_name = escape(strip_tags(form.cleaned_data['customer_name']))

            if customer_name == customer_name.upper():
                customer_name = customer_name.title()

            customer = Customer(name=customer_name, company=self.request.company)
            customer.save(user=self.request.user)

            deal.customer = customer

        if not hasattr(deal.customer, 'motorinsurancecustomerprofile'):
            CustomerProfile.objects.create(customer=deal.customer)

        deal.save(user=self.request.user)

        log_user_activity(self.request.user, self.request.path, 'C', deal)

        return JsonResponse({
            'success': True,
            'deal_id': deal.pk,
            'redirect_url': reverse('motorinsurance:deal-edit', kwargs=dict(pk=deal.pk)),
            'message': 'Deal created'
        })

    def form_invalid(self, form, **kwargs):
        return JsonResponse({'success': False, 'errors': form.errors})


class DealEditView(DealEditBaseView, CompanyAttributesMixin, UpdateView):
    template_name = "motorinsurance/deal/deal_detail.djhtml"
    permission_required = 'auth.update_motor_deals'
    form_class = DealForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['company'] = self.request.company
        kwargs['user'] = self.request.user

        return kwargs

    def get(self, *args, **kwargs):
        log_user_activity(self.request.user, self.request.path, 'R', self.get_object())

        return super(DealEditView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(DealEditView, self).get_context_data(**kwargs)

        deal = self.get_object()
        ctx['deal'] = deal

        ctx['deal_form'] = DealForm(instance=deal, company=self.request.company, user=self.request.user)

        note_form = NoteForm()

        ctx['note_form'] = note_form
        ctx['note_form_action'] = reverse('motorinsurance:deal-add-note', kwargs=dict(pk=deal.pk))

        ctx['task_form'] = TaskForm(
            initial={'time': DEFAULT_TIMESLOT},
            company=self.request.company
        )

        attachment_form = AttachmentForm()
        attachment_form.helper.form_action = reverse('motorinsurance:add-attachment', kwargs=dict(pk=deal.pk))
        ctx['attachment_form'] = attachment_form

        ctx['boolean_values_json'] = json.dumps(
            [{'value': '-1', 'text': 'Select an option'}, {'value': 0, 'text': 'No'}, {'value': 1, 'text': 'Yes'}])

        ctx['quote_form'] = MotorInsuranceQuoteForm(company=self.request.company)
        ctx['quoted_product_form'] = MotorInsuranceQuotedProductForm(company=self.request.company)

        ctx['allowed_insurers'] = self.get_allowed_insurers()

        ctx['auto_quotable_insurers'] = self.get_auto_quotable_insurers()

        ctx['back_url'] = self.request.GET.get('filters') or reverse('motorinsurance:deals')

        ctx['helpscout_enabled'] = self.is_helpscount_enabled(self.request.company.pk)

        return ctx

    def is_helpscount_enabled(self, company_id):
        """Helper function that only selects the helpscout enabled flag from the CompanySettings. CS is a huge model
        where a number of email templates are stored as well and loading it adds considerable time to the deal view."""
        cs = CompanySettings.objects.only(
            'helpscout_client_id',
            'helpscout_client_secret',
            'helpscout_mailbox_id',
        ).get(company_id=company_id)

        return cs.helpscout_client_id != '' and cs.helpscout_client_secret != '' and cs.helpscout_mailbox_id != ''

    def get_quoted_product_formset_class(self):
        return modelformset_factory(QuotedProduct,
                                    form=MotorInsuranceQuotedProductForm,
                                    can_delete=True,
                                    extra=0,
                                    min_num=1)

    def get_quoted_product_formset_kwargs(self, **kwargs):
        kwargs.update({
            'queryset': QuotedProduct.objects.none(),
            'form_kwargs': {
                'company': self.request.company
            }
        })

        quote = self.get_quote()
        if quote is not None:
            kwargs.update({
                'queryset': QuotedProduct.objects.filter(quote=quote).exclude(status=QuotedProduct.STATUS_DELETED)
            })

        return kwargs

    def form_valid(self, form, **kwargs):
        form.save()

        # Update or create a customer profile
        customer_profile, created = CustomerProfile.objects.get_or_create(
            customer=form.cleaned_data['customer']
        )

        customer_profile.first_license_age = form.cleaned_data['first_license_age']
        customer_profile.uae_license_age = form.cleaned_data['uae_license_age']
        customer_profile.first_license_country = form.cleaned_data['first_license_country']
        customer_profile.first_license_issue_date = form.cleaned_data['first_license_issue_date']
        customer_profile.uae_license_issue_date = form.cleaned_data['uae_license_issue_date']

        customer_profile.save(user=self.request.user)

        log_user_activity(self.request.user, self.request.path, 'U', self.get_object())

        return JsonResponse({'success': True})

    def form_invalid(self, form, **kwargs):
        return JsonResponse({'success': False, 'errors': form.errors})


class DealGetProductsAjax(DealEditBaseView, CompanyAttributesMixin, View):
    permission_required = 'auth.list_motor_deals'

    def get(self, *args, **kwargs):
        return JsonResponse(self.serialize_products())


class DealJsonAttributesList(DealEditBaseView, CompanyAttributesMixin, View):
    permission_required = 'auth.list_motor_deals'

    def get(self, *args, **kwargs):
        type = self.request.GET.get('type')
        response = {}

        if type == 'insurers':
            response = serialize_to_json(TOP_TIER_INSURERS)
        elif type == 'insurance_types':
            response = serialize_to_json(INSURANCE_TYPES)
        elif type == 'motor_lead_types':
            response = serialize_to_json(LEAD_TYPES)
        elif type == 'motor_years_without_claims':
            response = serialize_to_json(NO_CLAIMS)
        elif type == 'agents':
            response = self.get_company_agents_list()
        elif type == 'producers':
            response = self.get_company_producers_list()

        return JsonResponse(response, safe=False)


class DealHistoryView(DealEditBaseView, CompanyAttributesMixin, TemplateView):
    permission_required = 'auth.update_motor_deals'
    template_name = 'core/_history.djhtml'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['history'] = Timeline.get_formatted_object_history(self.get_object())

        return ctx


class DealSingleView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        today = datetime.datetime.today()

        try:
            deal = Deal.objects.get(pk=kwargs['pk'], company=self.request.company)
            order = deal.get_order()
            quote = deal.quote
            data = {'success': True}
            car_model = ''
            car_body_type = ''

            if deal.car_trim:
                car_model = deal.car_trim.model.name
                car_body_type = deal.car_trim.algo_driven_data.get('body', '')

            data['deal'] = {
                "id": deal.pk,
                "deal_type": deal.deal_type,
                "vehicle": deal.get_car_title(),
                "vehicle_year": deal.car_year,
                "vehicle_make": deal.car_make.name,
                "vehicle_model": car_model,
                "vehicle_body_type": car_body_type,
                "years_without_claim": deal.get_years_without_claim_display(),
                "place_of_registration": deal.get_place_of_registration_display(),
                "claim_certificate_available": 'Yes' if deal.claim_certificate_available else 'No',
                "date_of_first_registration": deal.date_of_first_registration,
                "vehicle_insured_value": f'{self.request.company.companysettings.get_currency_display()} '
                                         f'{deal.vehicle_insured_value}',
                "current_insurance_type": deal.get_current_insurance_type_display(),
                "insured_car_value": deal.vehicle_insured_value,
                "number_of_passengers": deal.number_of_passengers,

                "current_insurer": deal.get_current_insurer_display(),

                "first_license_age": deal.customer.motorinsurancecustomerprofile.first_license_age,
                "uae_license_age": deal.customer.motorinsurancecustomerprofile.uae_license_age,

                "selected_product": '',
                "selected_product_insurer": '',
                "selected_product_premium": '',
                "order_payment_amount": '',
                "selected_product_cover": '',

                "created_on": deal.created_on.isoformat()
            }

            if deal.customer:
                data['customer'] = {
                    "name": deal.customer.name,
                    "email": deal.customer.email,
                    "dob": deal.customer.dob,
                    "age": deal.customer.get_age(),
                    "gender": deal.customer.get_gender_display(),
                    "nationality": deal.customer.get_nationality_display(),
                    "first_license":
                        deal.customer.motorinsurancecustomerprofile.get_first_license_country_display(),
                    "first_license_age": deal.customer.motorinsurancecustomerprofile.first_license_age,
                    "uae_license_age": deal.customer.motorinsurancecustomerprofile.uae_license_age,
                }

            if quote:
                data['quote'] = {
                    'id': quote.pk,
                    'views': deal.quote.number_of_views or 0
                }

            if order:
                selected_product = order.selected_product

                data['order'] = {
                    "product": selected_product.product.name,
                    "product_insurer": selected_product.product.insurer.name,
                    "product_premium": float(selected_product.get_sale_price()),
                    "product_cover": 'TPL' if selected_product.product.is_tpl_product else 'comprehensive',
                    "sum_insured": '{}'.format(float(selected_product.insured_car_value) or deal.vehicle_insured_value),
                    "payment_amount": float(order.payment_amount),
                    "discounted_premium": 'yes' if selected_product.premium != selected_product.sale_price else 'no',
                    "repair_type": 'agency' if selected_product.agency_repair else 'non-agency'
                }

        except Deal.DoesNotExist:
            data = {'success': False}

        return JsonResponse(data)


class DealAddNoteView(AddNoteView):
    permission_required = ('auth.update_motor_deals',)
    model = Deal

    def get_success_url(self):
        return reverse('motorinsurance:deal-edit', kwargs={
            'pk': self.kwargs['pk']
        })


class DealAddEditTaskView(AddEditTaskView):
    permission_required = ('auth.update_motor_deals',)
    attached_model = Deal


class DealTaskListView(TaskBaseView):
    permission_required = 'auth.update_motor_deals'

    def get(self, *args, **kwargs):
        records = self.get_queryset().filter(object_id=self.kwargs['pk'])

        return JsonResponse(self.serialize_object_list(records), safe=False)


class DealDeleteNoteView(DeleteNoteView):
    permission_required = ('auth.update_motor_deals',)
    attached_model = Deal

    def get_success_url(self, attached_obj):
        return reverse('motorinsurance:deal-edit', kwargs=dict(pk=attached_obj.pk))


class DealAssignToMeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'auth.update_motor_deals'

    def get(self, *args, **kwargs):
        try:
            deal = Deal.objects.get(pk=kwargs['pk'], company=self.request.company)
            deal.assigned_to = self.request.user
            deal.save(user=self.request.user)
            response = {'success': True}

            log_user_activity(self.request.user, self.request.path, 'U', deal)
        except Deal.DoesNotExist:
            response = {'success': False, 'error': 'Permission denied'}

        return JsonResponse(response)


class DealUpdateFieldView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'auth.update_motor_deals'

    def get_object(self, **kwargs):
        try:
            return Deal.objects.get(
                pk=self.kwargs['pk'], company=self.request.company)
        except Deal.DoesNotExist:
            raise Http404()

    def post(self, request, *args, **kwargs):
        deal = self.get_object()
        field_name = request.POST['name']
        field_value = strip_tags(request.POST['value'])

        quote_outdated = False

        excluded_fields = [
            'company', 'company_id', 'customer', 'customer_id', 'deal', 'deal_id', 'created_on', 'updated_on']

        fields_to_outdate_quote = [
            'claim_certificate_available', 'years_without_claim', 'vehicle_insured_value',
            'date_of_first_registration', 'place_of_registration']

        if field_name in fields_to_outdate_quote and deal.stage == Deal.STAGE_QUOTE:
            quote = deal.quote
            quote.outdated = True
            quote.save()

            quote_outdated = True

        success = True
        status_code = 200
        message = 'Updated successfully'
        data = {}
        if deal.pk != int(request.POST['pk']) or field_name in excluded_fields:
            return JsonResponse({'success': False, 'message': 'Not allowed.'}, status=401)

        if kwargs['model'] == 'deal':
            model = deal
        elif kwargs['model'] == 'quote':
            model = deal.quote
        elif kwargs['model'] == 'order':
            model = deal.get_order()

        field_type = request.GET.get('type')
        return_value = field_value

        if field_value == '-1':  # To handle the case when user wants to unassign 'assigned_to' and 'producer' fields
            field_value = None
            return_value = 0
        elif field_type == 'email':
            valid_email_addresses = clean_and_validate_email_addresses(field_value)

            if valid_email_addresses is not False:
                field_value = valid_email_addresses
                return_value = valid_email_addresses
            else:
                success = False
                status_code = 400
                message = 'Invalid format for email address(es).'

        elif field_type and field_type == 'date':
            if field_value:
                try:
                    field_value = datetime.datetime.strptime(field_value, "%d-%m-%Y")
                    return_value = field_value.strftime('%b %d, %Y')
                except ValueError:
                    success = False
                    status_code = 400
                    message = 'Invalid format.'
            else:
                field_value = None

        elif field_name == 'phone' and field_value:
            if is_valid_number(field_value):
                field_value = normalize_phone_number(field_value)
                return_value = field_value
            else:
                success = False
                status_code = 400
                message = 'Invalid phone number.'
        elif field_name == 'assigned_to_id' and not field_value:
            success = False
            status_code = 400
            message = 'Please select an option.'

        elif field_name == 'vehicle_insured_value' and not field_value:
            field_value = 0

        data = {'name': field_value, 'value': return_value}

        if success:
            setattr(model, field_name, field_value)
            model.save(user=self.request.user)

            deal.update_in_algolia()

            log_user_activity(self.request.user, self.request.path, 'U', model)

        return JsonResponse({
            'success': success, 'message': message, 'data': data, 'quote_outdated': quote_outdated},
            status=status_code)


class DealUpdateMMTView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'auth.update_motor_deals'

    def get_object(self, **kwargs):
        try:
            return Deal.objects.get(
                pk=self.kwargs['pk'], company=self.request.company)
        except Deal.DoesNotExist:
            raise Http404()

    def post(self, request, *args, **kwargs):
        deal = self.get_object()

        if deal.pk != int(request.POST['pk']):
            raise Http404()

        try:
            deal.car_year = request.POST['car_year']
            deal.car_make_id = request.POST['car_make']
            deal.car_trim_id = request.POST.get('car_trim') or None
            deal.custom_car_name = escape(strip_tags(request.POST['custom_car_name']))

            deal.save(user=self.request.user)

            if deal.stage == Deal.STAGE_QUOTE:
                quote = deal.quote
                quote.outdated = True
                quote.save(user=self.request.user)

            response = {
                'success': True,
                'car': deal.get_car_title()
            }

            if deal.car_trim:
                response['extra_data'] = deal.car_trim.algo_driven_data

                if deal.car_trim.algo_driven_data.get('seats'):
                    no_of_passengers = int(deal.car_trim.algo_driven_data.get('seats')) - 1
                    response['no_of_passengers'] = no_of_passengers
                    deal.number_of_passengers = no_of_passengers
                    deal.save(user=self.request.user)

            log_user_activity(self.request.user, self.request.path, 'U', deal)

        except Deal.DoesNotExist:
            response = {'success': False, 'message': 'You do not have permissions'}

        return JsonResponse(response)


class DealQuoteView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    template_name = "motorinsurance/deal/components/deal_quote_preview.djhtml"
    permission_required = 'auth.list_motor_quotes'
    model = Deal


class DealQuoteExtendView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.update_motor_quotes'
    model = Deal

    def post(self, request, *args, **kwargs):
        deal = self.get_object()
        status = False

        if deal.quote and deal.quote.is_expired():
            quote = deal.quote
            quote.expiry_date = datetime.date.today() + datetime.timedelta(days=EXPIRED_QUOTE_EXTENSION_DAYS)
            quote.save(user=self.request.user)
            status = True

            note_content = 'Quote expiry extended to <span class="badge badge-primary">{}</span> by {}'.format(
                quote.expiry_date.strftime('%d-%m-%Y'),
                self.request.user
            )

            # Adding note to the deal
            add_note_to_deal(deal, note_content)

        return JsonResponse({'success': status}, safe=False)


class DealStagesView(DealEditBaseView, DetailView):
    template_name = "motorinsurance/deal/components/deal_overview.djhtml"
    permission_required = 'auth.list_motor_deals'
    model = Deal

    def get_context_data(self, **kwargs):
        deal = self.object
        ctx = super().get_context_data(**kwargs)
        closed_stages = [Deal.STAGE_LOST, Deal.STAGE_WON, 'closed']

        modification_allowed = deal.stage not in closed_stages

        ctx['modification_allowed'] = modification_allowed
        ctx['allowed_insurers'] = self.get_allowed_insurers()
        ctx['products_data'] = self.serialize_products()

        ctx['extended_expiry_date'] = None

        if deal.quote:
            ctx['extended_expiry_date'] = datetime.date.today() + datetime.timedelta(days=EXPIRED_QUOTE_EXTENSION_DAYS)

        stage = self.request.GET.get('stage') or deal.stage

        if stage == Deal.STAGE_NEW:
            ctx['quote_form'] = MotorInsuranceQuoteForm(company=self.request.company)
            ctx['quoted_product_form'] = MotorInsuranceQuotedProductForm(company=self.request.company)

        if stage == Deal.STAGE_QUOTE:
            has_quote = False
            self.template_name = 'motorinsurance/deal/components/quote_overview.djhtml'

            if deal.quote:
                has_quote = True

                ctx['order_form'] = OrderForm(quoted_products=deal.quote.get_active_quoted_products())
                ctx['quote_form'] = MotorInsuranceQuoteForm(company=self.request.company)
                ctx['quoted_product_form'] = MotorInsuranceQuotedProductForm(company=self.request.company)
                ctx['modification_allowed'] = deal.get_order() is None

                quote_url = deal.quote.get_quote_url()
                absolute_url = self.request.build_absolute_uri(quote_url)
                ctx['absolute_quote_url'] = absolute_url
                ctx['quote_pdf_download_url'] = deal.quote.get_download_pdf_url()

            ctx['has_quote'] = has_quote

        if stage == Deal.STAGE_ORDER:
            has_order = False
            self.template_name = 'motorinsurance/deal/components/order_overview.djhtml'

            order = deal.get_order()
            if order:
                has_order = True
                ctx['order_form'] = OrderForm(
                    instance=order,
                    quoted_products=deal.quote.get_active_quoted_products()
                )

                ctx['policy_form'] = PolicyForm(
                    initial={
                        'product': order.selected_product.product,
                        'policy_start_date': order.policy_start_date,
                        'policy_expiry_date': order.policy_start_date + datetime.timedelta(days=394)
                    },
                    company=self.request.company
                )

                document_url = deal.quote.get_document_upload_url()
                absolute_url = self.request.build_absolute_uri(document_url)
                ctx['absolute_document_upload_url'] = absolute_url
                print(absolute_url)

            ctx['has_order'] = has_order

        if stage == Deal.STAGE_HOUSEKEEPING:
            has_policy = False
            self.template_name = 'motorinsurance/deal/components/housekeeping_overview.djhtml'

            if hasattr(deal, 'policy'):
                has_policy = True
                ctx['policy_form'] = PolicyForm(instance=deal.policy, company=self.request.company)

            ctx['has_policy'] = has_policy

        if stage in closed_stages:
            ctx['has_closed'] = deal.stage in closed_stages
            self.template_name = 'motorinsurance/deal/components/closed_overview.djhtml'

        return ctx


class DealCurrentStageView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.list_motor_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        tags = self.get_object().get_tags()
        if self.get_object().renewal_for_policy:
            tags.insert(0, 'Renewal Deal')

        return JsonResponse({
            'stage': self.get_object().stage,
            'tags': tags
        })


class DealMarkasLostView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.update_motor_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        deal = self.get_object()

        if deal.stage not in [Deal.STAGE_LOST, Deal.STAGE_WON]:
            deal.stage = Deal.STAGE_LOST
            deal.save(user=self.request.user)

            return JsonResponse({'success': True})

        return JsonResponse({'success': False})


class DealReopenView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.update_motor_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        deal = self.get_object()

        if deal.stage in [Deal.STAGE_LOST, Deal.STAGE_WON]:
            if hasattr(deal, 'policy'):
                last_stage = Deal.STAGE_HOUSEKEEPING
            elif hasattr(deal, 'order'):
                last_stage = Deal.STAGE_ORDER
            elif deal.quote:
                last_stage = Deal.STAGE_QUOTE
            else:
                last_stage = Deal.STAGE_NEW

            deal.stage = last_stage
            deal.save(user=self.request.user)

            return JsonResponse({'success': True})

        return JsonResponse({'success': False})


class DealAddEditOrderView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = ('auth.create_motor_orders', 'auth.update_motor_orders')
    model = Deal

    def post(self, request, *args, **kwargs):
        deal = self.get_object()
        existing_order = deal.get_order()
        creating = existing_order is None  # Are we creating a new order?

        form_kwargs = {
            'instance': existing_order,
            'data': request.POST,
            'quoted_products': deal.quote.get_active_quoted_products(),
        }
        form = OrderForm(**form_kwargs)

        if form.is_valid():
            order = form.save(commit=False)
            order.deal = deal
            order.created_by_agent = True
            order.save(user=request.user)
            deal.update_in_algolia()

            quoted_product = form.cleaned_data['selected_product']
            selected_add_ons = form.cleaned_data['selected_add_ons']

            perform_successful_product_selection(
                deal.quote, quoted_product.product, quoted_product.pk, selected_add_ons)

            if creating:  # If we just created a new order, move the deal to the order stage
                deal.stage = Deal.STAGE_HOUSEKEEPING if hasattr(deal, 'policy') else Deal.STAGE_ORDER
                deal.save(user=request.user)

                note_title = 'created a manual order'
            else:
                if order.is_void:  # Did we just void an existing order? If so, move deal back
                    deal.stage = Deal.STAGE_QUOTE
                    deal.save(user=request.user)

                    note_title = 'voided an order'
                else:
                    note_title = 'updated an order'

            agent_name = request.user.get_full_name()
            bank_finance = order.mortgage_by
            policy_start_date = order.policy_start_date.strftime('%d-%m-%Y')

            note_content = (
                f'{agent_name} {note_title} '
                f'for <span class="badge badge-primary">{quoted_product.product.name}</span>, '
                f'Bank Finance: {bank_finance}, '
                f'Policy Start Date: {policy_start_date}'
            )
            add_note_to_deal(deal, note_content)

            return JsonResponse({
                'success': True,
                'creating': creating,
                'note_content': note_content,
                'note_created_on': datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })


class DealMarkClosedView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.update_motor_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        deal = self.get_object()
        mark_type = kwargs['type']

        if mark_type in ['lost', 'won']:
            deal.stage = Deal.STAGE_LOST if mark_type == 'lost' else Deal.STAGE_WON

            deal.save(user=self.request.user)

            return JsonResponse({'success': True})

        return JsonResponse({'success': False, 'errors': 'Invalid request'})


class DealRemoveWarningView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.update_motor_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        deal = self.get_object()

        if deal.quote:
            quote = deal.quote
            quote.outdated = False
            quote.save(user=self.request.user)

            return JsonResponse({'success': True})

        return JsonResponse({'success': False})


class DealQuotedProductsView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = ('auth.create_motor_quotes', 'auth.update_motor_quotes')
    model = Deal

    def get(self, request, *args, **kwargs):
        deal = self.get_object()

        response = []

        if deal.quote:
            for qp in deal.quote.get_editable_quoted_products():
                default_add_ons = qp.default_add_ons
                product_add_ons = qp.product.get_add_ons()
                sale_price = qp.sale_price

                if not sale_price:
                    sale_price = qp.premium

                response.append({
                    'id': qp.pk,
                    'product_id': qp.product.pk,

                    'product_logo': qp.product.logo.url,
                    'product_name': qp.product.name,

                    'is_tpl_product': qp.product.is_tpl_product,
                    'allows_agency_repair': qp.product.allows_agency_repair,

                    'agency_repair': qp.agency_repair,
                    'premium': "{:,}".format(qp.premium),
                    'sale_price': "{:,}".format(sale_price),
                    'deductible': "{:,}".format(qp.deductible),
                    'deductible_extras': qp.deductible_extras,
                    'insured_car_value': "{:,}".format(qp.insured_car_value),
                    'insurer_quote_reference': qp.insurer_quote_reference,
                    'ncd_required': qp.ncd_required,

                    'default_add_ons': default_add_ons,

                    'currency': request.company.companysettings.get_currency_display(),

                    'published': qp.is_published()
                })

        return JsonResponse(response, safe=False)

    def post(self, request, **kwargs):
        deal = self.get_object()
        creating = not bool(deal.quote)
        deleted = False
        request_data = json.load(request)

        if deal.quote is None:
            Quote.objects.create(deal=deal, company=request.company,
                                 insured_car_value=deal.vehicle_insured_value,
                                 status=Quote.STATUS_PUBLISHED)

            deal.stage = Deal.STAGE_QUOTE
            deal.save(user=request.user)

        for request_qp in request_data['products']:
            if request_qp:
                rqp = request_qp  # shortcut

                premium = rqp['premium'].replace(',', '')

                if not rqp['sale_price']:
                    sale_price = premium
                else:
                    sale_price = rqp['sale_price'].replace(',', '')

                if request_qp.get('id'):
                    existing_qp = deal.quote.products.get(pk=request_qp['id'])

                    if rqp.get('deleted'):
                        existing_qp.status = QuotedProduct.STATUS_DELETED
                    elif rqp.get('published'):
                        existing_qp.status = QuotedProduct.STATUS_PUBLISHED
                    elif not rqp.get('published'):
                        existing_qp.status = QuotedProduct.STATUS_UNPUBLISHED

                    existing_qp.product_id = rqp['product_id']
                    existing_qp.agency_repair = rqp['agency_repair']
                    existing_qp.premium = premium
                    existing_qp.sale_price = sale_price
                    existing_qp.deductible = rqp['deductible'].replace(',', '')
                    existing_qp.deductible_extras = rqp['deductible_extras']
                    existing_qp.insurer_quote_reference = rqp['insurer_quote_reference']
                    existing_qp.insured_car_value = rqp['insured_car_value'].replace(',', '')
                    existing_qp.ncd_required = rqp['ncd_required']
                    existing_qp.default_add_ons = rqp['default_add_ons']
                    existing_qp.save(user=request.user)
                else:

                    new_qp = QuotedProduct(quote=deal.quote, product_id=rqp['product_id'],
                                           agency_repair=rqp['agency_repair'],
                                           premium=premium,
                                           sale_price=sale_price,
                                           deductible=rqp['deductible'].replace(',', ''),
                                           deductible_extras=rqp['deductible_extras'],
                                           insured_car_value=rqp['insured_car_value'].replace(',', ''),
                                           insurer_quote_reference=rqp['insurer_quote_reference'],
                                           ncd_required=rqp['ncd_required'],
                                           default_add_ons=rqp['default_add_ons'])
                    if rqp.get('published'):
                        new_qp.status = QuotedProduct.STATUS_PUBLISHED
                    else:
                        new_qp.status = QuotedProduct.STATUS_UNPUBLISHED

                    new_qp.save(user=request.user)

                    car_model = ''
                    car_body_type = ''

                    if deal.car_trim:
                        car_model = deal.car_trim.model.name
                        car_body_type = deal.car_trim.algo_driven_data.get('body', '')

                    try:
                        Amplitude(self.request).log_event(
                            Amplitude.EVENTS['motor_product_quoted'], {
                                'deal_id': deal.pk,
                                'source': 'Quoting Engine' if rqp['auto_quoted'] else 'manual',

                                'insurer': new_qp.product.insurer.name,
                                'product': new_qp.product.name,
                                'premium': new_qp.premium,
                                'sale_price': new_qp.sale_price,
                                'discounted_premium': 'yes' if new_qp.premium != new_qp.sale_price else 'no',
                                'cover': 'TPL' if new_qp.product.is_tpl_product else 'comprehensive',
                                'repair_type': 'agency' if new_qp.agency_repair else 'non-agency',

                                'vehicle_model_year': deal.car_year,
                                'vehicle make': deal.car_make.name,
                                'vehicle_model': car_model,
                                'vehicle_body_type': car_body_type,
                                'vehicle_sum_insured': '{}'.format(
                                    float(new_qp.insured_car_value) or deal.vehicle_insured_value),

                                'client_nationality': deal.customer.get_nationality_display(),
                                'client_gender': deal.customer.get_gender_display(),
                                'client_age': deal.customer.get_age()
                            })

                    except Exception as e:
                        api_logger.error('Amplitude error while logging "motor product quoted", Error: %s', e)

        quote = deal.quote
        quote.outdated = False

        if request_data['quote']['delete'] and not quote.get_editable_quoted_products().count():
            deal.stage = Deal.STAGE_NEW
            deal.save()

            quote.is_deleted = True

            deleted = True
        else:
            quote.status = Quote.STATUS_PUBLISHED if request_data['quote'].get('status') else Quote.STATUS_UNPUBLISHED

        quote.save()

        return JsonResponse({'success': True, 'creating': creating, 'deleted': deleted})


class DealDuplicateView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.create_motor_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        deal = self.get_object()
        deal.pk = None
        # These are the fields need to be resetted in order to
        # create a new deal from an existing one.
        deal.lead = None
        deal.stage = Deal.STAGE_NEW
        deal.quote_sent = False
        deal.is_deleted = False
        deal.renewal_for_policy = None
        deal.deal_type = Deal.DEAL_TYPE_DUPLICATE

        deal.save(user=self.request.user)

        try:
            Amplitude(self.request).log_event(Amplitude.EVENTS['motor_deal_created'], {
                'source': 'manual',
                'deal_id': deal.pk,
                'client_nationality': deal.customer.get_nationality_display(),
                'client_gender': deal.customer.get_gender_display(),
                'client_age': deal.customer.get_age(),
                'vehicle_model_year': deal.car_year,
                'vehicle make': deal.car_make.name,
                'vehicle_sum_insured': '{}'.format(deal.vehicle_insured_value),
                'deal_type': deal.deal_type
            })
        except Exception as e:
            api_logger.error('Amplitude error while logging "motor deal create" Source: %s, Error: %s', 'duplicate', e)

        return JsonResponse({
            'success': True,
            'redirect_url': reverse('motorinsurance:deal-edit', kwargs={'pk': deal.pk})
        })


class DealEmailTemplatesListView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.update_motor_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        deal_id = self.get_object()


class DealAttachmentsView(DealEditBaseView, CompanyAttributesMixin, DetailView):
    permission_required = 'auth.list_motor_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        deal = self.get_object()

        return JsonResponse({
            'title': 'Deal',
            'documents': self.serialize_attachments(deal.get_attachments()),
            'related_documents': self.get_related_attachments()
        })


class DealAddAttachmentView(AddAttachmentView):
    permission_required = ('auth.update_motor_deals',)
    model = Deal

    def get_success_url(self):
        if 'next' in self.request.GET:
            return self.request.GET['next']

        return "{}#tab_documents".format(
            reverse('motorinsurance:deal-edit', kwargs={'pk': self.kwargs['pk']})
        )


class DealDeleteAttachmentView(DeleteAttachmentView):
    permission_required = ('auth.update_motor_deals',)
    attached_model = Deal

    def get_success_url(self, attached_obj):
        if 'next' in self.request.GET:
            return self.request.GET['next']

        return "{}#tab_documents".format(
            reverse('motorinsurance:deal-edit', kwargs={'pk': attached_obj.pk})
        )


class DealCopyAttachmentView(DealEditBaseView, CompanyAttributesMixin, DetailView):
    permission_required = ('auth.update_motor_deals',)
    model = Deal

    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        try:
            attachment = Attachment.objects.get(pk=kwargs['attachment_id'])
            content_type_id = ContentType.objects.get(app_label='motorinsurance', model='deal').id

            attachment.pk = None
            attachment.content_type_id = content_type_id
            attachment.object_id = obj.pk

            attachment.save()
        except Attachment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Attachment does not exist.'})

        return JsonResponse({'success': True})


