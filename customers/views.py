import json
import time
import datetime

from django.conf import settings
from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render
from django.http import Http404
from django.http.response import JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView, UpdateView, FormView, View, DetailView
from django.utils.html import strip_tags, escape

from core.mixins import AjaxListViewMixin, AdminAllowedMixin
from core.forms import NoteForm, AttachmentForm
from core.models import Attachment
from core.utils import log_user_activity, normalize_phone_number, is_valid_number, clean_and_validate_email_addresses
from core.views import AddNoteView, DeleteNoteView, AddAttachmentView, DeleteAttachmentView
from customers.forms import CustomerForm, CustomerSearchAndOrderingForm, CustomerMergeForm
from customers.models import Customer
from customers.tasks import add_note_to_customer

from felix.exporter import ExportService
from felix.constants import ITEMS_PER_PAGE

from motorinsurance.forms import DealForm
from motorinsurance.models import CustomerProfile, Deal, Policy

from core.algolia import Algolia
from core.timeline import Timeline


class CustomerBaseView(LoginRequiredMixin, PermissionRequiredMixin):
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

        index_name = f'{settings.ALGOLIA["ENV"]}_customers_{self.request.company.pk}{sort_by}'
        index = Algolia().get_index(index_name)

        if so_form.is_valid():
            cd = so_form.cleaned_data

            if cd['status'] == 'deleted':
                status = 'deleted'

            facet_filters.append(f'status:{status}')

            if cd['created_on_after']:
                numeric_filters.append('created_on >= {}'.format(time.mktime(cd['created_on_after'].timetuple())))
            if cd['created_on_before']:
                numeric_filters.append('created_on <= {}'.format(time.mktime(cd['created_on_before'].timetuple())))

            if cd['search_term']:
                query = cd['search_term']

        params = {
            'query': query,
            'filters': filters,
            'facets': facets,
            'facetFilters': facet_filters,
            'numericFilters': numeric_filters,
            'attributesToHighlight': [],
            'attributesToSnippet': [],
        }

        return index.browse_all(params)

    def get_search_and_ordering_form(self):
        return CustomerSearchAndOrderingForm(data=self.request.GET)


class CustomersSearchView(CustomerBaseView, AjaxListViewMixin, View):
    permission_required = 'auth.search_customers'
    default_sort_by = ''

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()

        return JsonResponse(self.serialize_object_list(qs), safe=False)

    def serialize_object_list(self, customers):
        res = []
        producer_customers = []

        if self.request.user.userprofile.has_producer_role():
            producer_deals = Deal.objects.filter(producer=self.request.user).distinct('customer')
            producer_customers = [str(deal.customer.id) for deal in producer_deals]

        for record in customers:
            if len(producer_customers) and record['objectID'] not in producer_customers:
                continue

            res.append({
                'id': record['objectID'],
                'label': record['name'],
                'desc': 'E: {} | T: {}'.format(
                    record['email'] or '-',
                    record['phone'] or '-',
                )
            })

        return res


class CustomerExportView(CustomerBaseView, AdminAllowedMixin, AjaxListViewMixin, View):
    permission_required = 'auth.export_customers'
    default_sort_by = ''

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = list()
        column_labels = [
            '#', 'Customer', 'Phone', 'Email', 'Nationality', 'Created On', 'Updated On']

        counter = 1
        for customer in qs:
            data.append([
                counter,
                customer['name'], customer['phone'], customer['email'], customer['nationality'],
                customer['created_on_display'], customer['updated_on_display']
            ])
            counter += 1

        exporter = ExportService()

        return exporter.to_csv(column_labels, data, filename='customers-{}.csv'.format(datetime.datetime.today()))


class CustomersView(CustomerBaseView, AjaxListViewMixin, TemplateView):
    template_name = "customers/list.djhtml"
    permission_required = 'auth.list_customers'
    default_sort_by = ''

    def get_context_data(self, **kwargs):
        ctx = super(CustomersView, self).get_context_data(**kwargs)

        ctx['search_form'] = self.get_search_and_ordering_form()
        ctx['customer_form'] = CustomerForm()
        ctx['customer_merge_form'] = CustomerMergeForm()
        ctx['page'] = self.request.GET.get('page') or 1
        ctx['default_sort_by'] = self.request.GET.get('sort_by') or 'created_on_desc'

        log_user_activity(self.request.user, self.request.path)

        return ctx


class CustomersDeleteView(LoginRequiredMixin, AdminAllowedMixin, PermissionRequiredMixin, View):
    permission_required = 'auth.delete_customers'

    def get(self, *args, **kwargs):
        try:
            customer = Customer.objects.get(company=self.request.company, pk=self.kwargs['pk'])
            customer.status = Customer.STATUS_DELETED
            customer.save(user=self.request.user)

            response = {'success': True}

        except ObjectDoesNotExist:
            response = {'success': False}

        return JsonResponse(response, safe=False)


class CustomersAddView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = 'auth.create_customers'
    form_class = CustomerForm

    def form_valid(self, form, **kwargs):
        customer = form.save(commit=False)
        customer.company = self.request.company

        if customer.name == customer.name.upper():
            customer.name = customer.name.title()

        if customer.phone:
            if(is_valid_number(customer.phone)):
                customer.phone = normalize_phone_number(customer.phone)
            else:
                return JsonResponse({'success': False, 'errors': {'phone': 'Invalid phone number'}})

        customer.save(user=self.request.user)

        log_user_activity(self.request.user, self.request.path, 'C', customer)

        return JsonResponse({
            'success': True,
            'redirect_url': reverse('customers:edit', kwargs=dict(pk=customer.pk)),
            'message': 'Customer created.'
        })

    def form_invalid(self, form, **kwargs):
        return JsonResponse({'success': False, 'errors': form.errors})


class CustomersEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = "customers/customer_detail.djhtml"
    permission_required = 'auth.update_customers'
    form_class = CustomerForm

    def get_object(self, **kwargs):
        try:
            return Customer.objects.get(
                pk=self.kwargs['pk'], company=self.request.company)
        except Customer.DoesNotExist:
            raise Http404()

    def get_context_data(self, **kwargs):
        ctx = super(CustomersEditView, self).get_context_data(**kwargs)
        customer = self.get_object()

        log_user_activity(self.request.user, self.request.path, 'R', self.get_object())

        ctx['form'] = CustomerForm(instance=customer)
        ctx['customer'] = customer

        ctx['deal_form'] = DealForm(
            initial={'customer': customer},
            company=self.request.company,
            user=self.request.user
        )

        note_form = NoteForm()
        ctx['note_form'] = note_form
        ctx['note_form_action'] = reverse('customers:add-note', kwargs=dict(pk=customer.pk))

        attachment_form = AttachmentForm()
        attachment_form.helper.form_action = reverse('customers:add-attachment', kwargs=dict(pk=customer.pk))
        ctx['attachment_form'] = attachment_form

        ctx['back_url'] = self.request.GET.get('filters') or reverse('customers:customers')
        ctx['deleted'] = customer.status == Customer.STATUS_DELETED

        customer_motor_deals = customer.get_non_deleted_deals()
        customer_motor_open_deals = customer.get_open_deals()
        customer_motor_policies = customer.get_policies()
        customer_motor_active_policies = customer.get_active_policies()

        if self.request.user.userprofile.has_producer_role():
            customer_motor_deals = customer_motor_deals.filter(producer=self.request.user)
            customer_motor_open_deals = customer_motor_open_deals.filter(producer=self.request.user)
            customer_motor_policies = customer_motor_policies.filter(deal__producer=self.request.user)
            customer_motor_active_policies = customer_motor_active_policies.filter(deal__producer=self.request.user)

        ctx['motor_deals'] = customer_motor_deals
        ctx['motor_open_deals'] = customer_motor_open_deals
        ctx['motor_policies'] = customer_motor_policies
        ctx['motor_active_policies'] = customer_motor_active_policies

        ctx['attachments'] = json.dumps([{
            'id': attachment.id,
            'label': attachment.label,
            'url': attachment.get_file_url(),
            'can_preview': attachment.can_preview_in_frontend(),
            'extension': attachment.get_file_extension(),
            'added_by': attachment.added_by.get_full_name() if attachment.added_by else '',
            'created_on': attachment.created_on.strftime('%Y-%m-%d'),
        } for attachment in customer.get_attachments()])

        return ctx

    def form_valid(self, form, **kwargs):
        customer = form.save(commit=False)
        customer.save(user=self.request.user)  # We use a custom save so we can pass in the User for history tracking

        log_user_activity(self.request.user, self.request.path, 'U', self.get_object())

        return JsonResponse({'success': True})

    def form_invalid(self, form, **kwargs):
        return JsonResponse({'success': False, 'errors': form.errors})


class CustomerHistoryView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.update_customers'
    template_name = 'core/_history.djhtml'
    model = Customer

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['history'] = Timeline.get_formatted_object_history(self.get_object())

        return ctx


class CustomersFieldUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'auth.update_customers'

    def get_object(self, **kwargs):
        try:
            return Customer.objects.get(
                pk=self.kwargs['pk'], company=self.request.company)
        except Customer.DoesNotExist:
            raise Http404()

    def check_for_outdated_quotes(self):
        customer = self.get_object()
        deals = Deal.objects.filter(customer=customer, stage=Deal.STAGE_QUOTE)

        for deal in deals:
            if deal.quote:
                quote = deal.quote
                quote.outdated = True
                quote.save()

    def post(self, request, *args, **kwargs):
        customer = self.get_object()
        field_name = request.POST['name']
        field_value = strip_tags(request.POST['value'])

        quote_outdated = False

        excluded_fields = ['company', 'company_id', 'customer', 'customer_id', 'created_on', 'updated_on']
        fields_to_outdate_quote = ['nationality', 'gender', 'dob']

        if field_name in fields_to_outdate_quote or kwargs['model'] == 'motorprofile':
            self.check_for_outdated_quotes()

            quote_outdated = True

        success = True
        status_code = 200
        message = 'Updated successfully'
        data = {}

        if (customer.pk != int(request.POST['pk'])) or field_name in excluded_fields:
            return JsonResponse({'success': False, 'message': 'Not allowed'}, status=401)

        if kwargs['model'] == 'customer':
            model = customer
        elif kwargs['model'] == 'motorprofile':
            if not hasattr(customer, 'motorinsurancecustomerprofile'):
                CustomerProfile.objects.create(customer=customer)

            model = customer.motorinsurancecustomerprofile

        field_type = request.GET.get('type')

        if field_name == 'name' and field_value == field_value.upper():
            field_value = field_value.title()

        return_value = field_value

        if field_type == 'email' and field_value:
            valid_email_addresses = clean_and_validate_email_addresses(field_value)

            if valid_email_addresses:
                field_value = valid_email_addresses
                return_value = valid_email_addresses
            else:
                success = False
                status_code = 400
                message = 'Invalid format'

        elif field_type and field_type == 'date':
            try:
                if field_value:
                    field_value = datetime.datetime.strptime(field_value, "%d-%m-%Y")
                    return_value = field_value.strftime('%b %d, %Y')
                else:
                    field_value = None
            except ValueError:
                success = False
                status_code = 400
                message = 'Invalid format'

        elif field_name == 'phone' and field_value:
            if is_valid_number(field_value):
                field_value = normalize_phone_number(field_value)
                return_value = field_value
            else:
                success = False
                status_code = 400
                message = 'Invalid phone number'

        if success:
            setattr(model, field_name, field_value)
            model.save(user=self.request.user)

            log_user_activity(self.request.user, self.request.path, 'U', model)

        data = {'name': field_value, 'value': return_value}

        return JsonResponse({
            'success': success, 'message': message, 'data': data, 'quote_outdated': quote_outdated},
            status=status_code)


class CustomerJsonListView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            customers = Customer.objects.filter(company=self.request.company, status=Customer.STATUS_ACTIVE)
            response = [
                (customer.id, '{} - {}'.format(customer.name, customer.email))
                for customer in customers
            ]

        except ObjectDoesNotExist:
            response = None

        return JsonResponse(response, safe=False)


class CustomerProfileMotorView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            customer = Customer.objects.get(pk=kwargs['pk'], company=self.request.company)
            profile = customer.motorinsurancecustomerprofile
            profileset = {
                "first_license_age": profile.first_license_age,
                "uae_license_age": profile.uae_license_age,
                "first_license_country": profile.first_license_country,
                "first_license_issue_date": profile.first_license_issue_date,
                "uae_license_issue_date": profile.uae_license_issue_date
            }
            response = {'success': True, 'profile': profileset}
        except ObjectDoesNotExist:
            response = {'success': False}

        return JsonResponse(response)


class CustomerAddNoteView(AddNoteView):
    permission_required = ('auth.update_customers',)
    model = Customer

    def get_success_url(self):
        return reverse('customers:edit', kwargs={
            'pk': self.kwargs['pk']
        })


class CustomerDeleteNoteView(DeleteNoteView):
    permission_required = ('auth.update_customers',)
    attached_model = Customer

    def get_success_url(self, attached_obj):
        return reverse('customers:edit', kwargs={
            'pk': attached_obj.pk
        })


class CustomerAttachmentsView(LoginRequiredMixin, DetailView):
    permission_required = 'auth.update_customers'
    model = Customer

    def get(self, request, *args, **kwargs):
        customer = self.get_object()
        documents = self.serialize_attachments(customer.get_attachments())
        related_documents = self.get_related_attachments()

        return JsonResponse({
            'title': 'Customer',
            'documents': documents,
            'related_documents': related_documents
        })

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

    def get_related_attachments(self):
        attachments = []
        customer = self.get_object()

        deals = Deal.objects.filter(customer=customer)

        for deal in deals:
            attachments = attachments + self.serialize_attachments(
                deal.get_attachments(),
                deal.get_car_title(),
                reverse('motorinsurance:deal-edit', kwargs=dict(pk=deal.pk)))

        return attachments


class CustomerAddAttachmentView(AddAttachmentView):
    permission_required = ('auth.update_customers',)
    model = Customer

    def get_success_url(self):
        if 'next' in self.request.GET:
            return self.request.GET['next']

        return "{}#tab_documents".format(
            reverse('customers:edit', kwargs={'pk': self.kwargs['pk']})
        )


class CustomerDeleteAttachmentView(DeleteAttachmentView):
    permission_required = ('auth.update_customers',)
    attached_model = Customer

    def get_success_url(self, attached_obj):
        if 'next' in self.request.GET:
            return self.request.GET['next']

        return "{}#tab_documents".format(
            reverse('customers:edit', kwargs={'pk': attached_obj.pk})
        )


class CustomerCopyAttachmentView(LoginRequiredMixin, DetailView):
    permission_required = ('auth.update_customers',)
    model = Customer

    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        try:
            attachment = Attachment.objects.get(pk=kwargs['attachment_id'])
            content_type_id = ContentType.objects.get(app_label='customers', model='customer').id

            attachment.pk = None
            attachment.content_type_id = content_type_id
            attachment.object_id = obj.pk

            attachment.save()
        except Attachment.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Attachment does not exist.'})

        return JsonResponse({'success': True})


class CustomersMergeView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = 'auth.create_customers'
    form_class = CustomerMergeForm
    template_name = 'customers/components/customer_merge_form.djhtml'

    def get_suggested_initial_data(self, primary, secondary):
        try:
            pcmp = primary.motorinsurancecustomerprofile
        except CustomerProfile.DoesNotExist:
            pcmp = CustomerProfile.objects.create(customer=primary)

        try:
            scmp = secondary.motorinsurancecustomerprofile
        except CustomerProfile.DoesNotExist:
            scmp = CustomerProfile.objects.create(customer=secondary)

        first_license_issue_date = pcmp.first_license_issue_date or scmp.first_license_issue_date
        if first_license_issue_date:
            first_license_issue_date = first_license_issue_date.strftime('%d-%m-%Y')

        uae_license_issue_date = pcmp.uae_license_issue_date or scmp.uae_license_issue_date
        if uae_license_issue_date:
            uae_license_issue_date = uae_license_issue_date.strftime('%d-%m-%Y')

        return {
            'name': primary.name or secondary.name,
            'email': primary.email or secondary.email,
            'phone': primary.phone or secondary.phone,
            'gender': primary.gender or secondary.gender,
            'nationality': primary.nationality or secondary.nationality,

            'first_license_age': pcmp.first_license_age or scmp.first_license_age,
            'uae_license_age': pcmp.uae_license_age or scmp.uae_license_age,
            'first_license_country': pcmp.first_license_country or scmp.first_license_country,
            'first_license_issue_date': first_license_issue_date,
            'uae_license_issue_date': uae_license_issue_date,
        }

    def get_customers(self):
        customer_1 = Customer.objects.get(pk=self.kwargs['pk1'])
        customer_2 = Customer.objects.get(pk=self.kwargs['pk2'])

        primary = customer_1 if customer_1.created_on < customer_2.created_on else customer_2
        secondary = customer_1 if customer_1.created_on > customer_2.created_on else customer_2

        return primary, secondary

    def get(self, request, *args, **kwargs):
        primary, secondary = self.get_customers()

        ctx = {
            'customer_merge_form': CustomerMergeForm(initial=self.get_suggested_initial_data(primary, secondary)),
            'primary': primary,
            'secondary': secondary
        }

        return render(request, self.template_name, ctx)

    def form_valid(self, form, **kwargs):
        primary, secondary = self.get_customers()

        # Updating primary customer's profile
        primary.name = form.cleaned_data['name']
        primary.email = form.cleaned_data['email']
        primary.phone = form.cleaned_data['phone']
        primary.gender = form.cleaned_data['gender']
        primary.nationality = form.cleaned_data['nationality']
        primary.save(user=self.request.user)

        # Updating primary customer's motor profile
        primary.motorinsurancecustomerprofile.first_license_age = form.cleaned_data['first_license_age']
        primary.motorinsurancecustomerprofile.uae_license_age = form.cleaned_data['uae_license_age']
        primary.motorinsurancecustomerprofile.first_license_country = form.cleaned_data['first_license_country']
        primary.motorinsurancecustomerprofile.first_license_issue_date = form.cleaned_data['first_license_issue_date']
        primary.motorinsurancecustomerprofile.uae_license_issue_date = form.cleaned_data['uae_license_issue_date']
        primary.motorinsurancecustomerprofile.save(user=self.request.user)

        Deal.objects.filter(customer=secondary).update(customer=primary)
        Policy.objects.filter(customer=secondary).update(customer=primary)

        secondary.notes.all().update(object_id=primary.pk)
        secondary.attachments.all().update(object_id=primary.pk)

        secondary.status = Customer.STATUS_DELETED
        secondary.save(user=self.request.user)

        today = datetime.datetime.today().strftime('%d-%m-%Y')

        note_content = (
            f'Customer {secondary.name} was merged '
            f'on {today} '
            f'by {self.request.user}'
        )

        add_note_to_customer(primary, note_content)

        return JsonResponse({
            'success': True,
            'redirect_url': reverse('customers:edit', kwargs={'pk': primary.pk})
        })

    def form_invalid(self, form, **kwargs):
        return JsonResponse({'success': False, 'errors': form.errors})
