import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http.response import JsonResponse
from django.utils.timezone import localtime
from django.utils.html import strip_tags, escape
from django.views.generic import TemplateView, View, DetailView, FormView

from rolepermissions.mixins import HasPermissionsMixin
from rolepermissions.roles import get_user_roles

from accounts.roles import Producer
from felix.exporter import ExportService

from core.algolia import Algolia
from core.email import Emailer
from core.mixins import AjaxListViewMixin, AdminAllowedMixin
from core.utils import log_user_activity
from core.views import DeleteAttachmentView

from customers.models import Customer
from healthinsurance.forms.policy import PolicySearchAndOrderingForm, NewPolicyForm
from healthinsurance.models.deal import Deal
from healthinsurance.models.quote import Quote, QuotedPlan
from healthinsurance.models.policy import HealthPolicy
from django.contrib.auth.models import User


class PolicyBaseView(LoginRequiredMixin, PermissionRequiredMixin, AjaxListViewMixin, View):
    permission_required = 'auth.list_health_policies'
    default_order_by = '-updated_on'

    def get_queryset(self):
        qs = HealthPolicy.objects.filter(company=self.request.company).order_by(self.default_order_by)

        so_form = self.get_search_and_ordering_form()

        if so_form.is_valid():

            if so_form.cleaned_data['expiry']:
                if so_form.cleaned_data['expiry'] == 'expired':
                    qs = qs.filter(policy_expiry_date__lte=datetime.date.today())
                if so_form.cleaned_data['expiry'] == 'active':
                    qs = qs.filter(policy_expiry_date__gte=datetime.date.today())

            # if so_form.cleaned_data['products']:
            #     qs = qs.filter(product=so_form.cleaned_data['products'])

            if so_form.cleaned_data['status']:
                qs = qs.filter(status=so_form.cleaned_data['status'])
            else:
                qs = qs.filter(~Q(status=HealthPolicy.STATUS_DELETED))

            if so_form.cleaned_data['created_on_after']:
                qs = qs.filter(created_on__gte=so_form.cleaned_data['created_on_after'])
            if so_form.cleaned_data['created_on_before']:
                qs = qs.filter(created_on__lte=so_form.cleaned_data['created_on_before'] + relativedelta(days=1))

            if so_form.cleaned_data['search_term']:
                st = so_form.cleaned_data['search_term']
                qs = qs.filter(
                    Q(customer__name__icontains=st) |
                    Q(customer__email__icontains=st) |
                    Q(reference_number__icontains=st)
                )

            order_by = so_form.cleaned_data['order_by']

            if order_by:
                if 'product' in order_by:
                    order_by = f'{order_by}__name'
                qs = qs.order_by(order_by)
            else:
                qs = qs.order_by('-start_date')

        roles = get_user_roles(self.request.user)
        if Producer in roles:
            qs = qs.filter(owner=self.request.user)

        return qs

    def get_search_and_ordering_form(self):
        return PolicySearchAndOrderingForm(data=self.request.GET, company=self.request.company)


class PolicyListView(PolicyBaseView, TemplateView):
    template_name = "healthinsurance/policies_list.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super(PolicyListView, self).get_context_data(**kwargs)
        self.request.session['selected_product_line'] = 'health-insurance'
        policies = HealthPolicy.objects.all().order_by('-start_date')
        filters = ''
        if self.request.user.userprofile.has_producer_role():
            filters = "owner_id:{user_id}".format(user_id=self.request.user.pk)

        # ctx['algolia_secured_search_api_key'] = Algolia().get_secured_search_api_key(
        #     filters=filters
        # )
        ctx['policies'] = policies
        ctx['search_form'] = self.get_search_and_ordering_form()
        ctx['policy_form'] = NewPolicyForm(company=self.request.company)
        ctx['expiry'] = self.request.GET.get('expiry') or 'all'

        ctx['page'] = self.request.GET.get('page') or 1
        ctx['sort_by'] = self.request.GET.get('sort_by') or ''
        ctx['expiry'] = self.request.GET.get('expiry') or 'all'
        ctx['referrers'] = User.objects.filter(userprofile__company=self.request.company, is_active=True) \
                                .exclude(pk=self.request.user.id) \
                                .order_by('first_name')
        ctx['entity'] = 'health'
        log_user_activity(self.request.user, self.request.path)

        return ctx


class PolicyAddView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = 'auth.create_health_policies'
    form_class = NewPolicyForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs['company'] = self.request.company

        return kwargs

    def form_valid(self, form, **kwargs):
        policy = form.save(commit=False)

        policy.company = self.request.company

        if not form.cleaned_data['customer']:
            customer_name = escape(strip_tags(form.cleaned_data['customer_name']))

            if customer_name == customer_name.upper():
                customer_name = customer_name.title()

            customer = Customer(name=customer_name, company=self.request.company)
            customer.save(user=self.request.user)

            policy.customer = customer

        

        policy.default_add_ons = []
        policy.paid_add_ons = []

        policy.save(user=self.request.user)

        log_user_activity(self.request.user, self.request.path, 'C', policy)

        return JsonResponse({
            'success': True,
            'message': 'Policy created successfully'
        })

    def form_invalid(self, form, **kwargs):
        return JsonResponse({'success': False, 'errors': form.errors})


class PolicyExportView(PolicyBaseView, AdminAllowedMixin, AjaxListViewMixin, View):
    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = list()
        column_labels = [
            'Status', 'Policy Number','Customer','Phone', 'Email', 'Nationality', 'DOB', 'Premium',
            'User','Referrer','Insurer','Selected Plan', 'Created On', 'Updated On', 
            'Policy Start Date', 'Policy Expiry Date']

        for policy in qs:
            premium = policy.total_premium_vat_inc
            #deductible = policy.deductible            
            selected_plan = policy.plan
            deal = policy.deal

            customer = policy.customer
            user = ''
            referrer = ''

            if deal:
                order = deal.get_order()
                user = deal.user
                referrer = deal.referrer

                if order and not premium:
                    premium = order.payment_amount

                if order and not selected_plan:
                    selected_plan = order.selected_plan.plan

            selected_product_name = selected_plan.name if selected_plan else ''
            insurer_name = selected_plan.insurer.name if selected_plan else ''

            data.append([
                policy.get_policy_expiry_status(), policy.reference_number, customer.name,customer.phone, customer.email,
                customer.get_nationality_display(),customer.dob,'{:,}'.format(premium) if premium else '',                
                user, referrer, insurer_name, selected_product_name, 
                policy.created_on.strftime('%Y-%m-%d'), policy.updated_on.strftime('%Y-%m-%d'),
                policy.start_date.strftime('%Y-%m-%d'), policy.expiry_date.strftime('%Y-%m-%d')
            ])

        exporter = ExportService()

        return exporter.to_csv(column_labels, data, filename='policies-{}.csv'.format(datetime.datetime.today()))


class PolicySingleView(LoginRequiredMixin, HasPermissionsMixin, DetailView):
    required_permission = 'update_health_policies'
    model = HealthPolicy

    def get(self, request, *args, **kwargs):
        policy = self.get_object()

        deal = policy.deal
        order = deal.get_order() if deal else None

        try:
            renewal_deal = policy.deal_policy_renewed_for.first()
        except Deal.DoesNotExist:
            renewal_deal = None
            pass

        if order or policy.product:
            logo_url = order.selected_product.product.get_logo() if order else policy.product.get_logo()
        else:
            logo_url = ''

        response = {
            'source_deal_id': deal.pk if deal else '',
            'source_deal_title': f'{deal}' if deal else '',
            'renewal_deal_id': renewal_deal.pk if renewal_deal else '',
            'renewal_deal_title': f'{renewal_deal}' if renewal_deal else '',
            'policy_title': policy.get_title(),
            'policy_number': policy.reference_number,
            'policy_start_date': policy.policy_start_date,
            'policy_expiry_date': policy.policy_expiry_date,
            'policy_status': policy.get_policy_expiry_status(),
            'insurance_type': policy.get_insurance_type_display(),
            'agency_repair': policy.agency_repair,
            'customer': policy.customer.name,
            'vehicle': policy.get_car_title(),
            'sum_insured': '{:,}'.format(policy.insured_car_value),
            'currency': request.company.companysettings.get_currency_display(),
            'premium': '{:,}'.format(policy.premium),
            'deductible': '{:,}'.format(policy.deductible),
            'deductible_extras': policy.deductible_extras,
            'mortgage': policy.mortgage_by,
            'add_ons': policy.paid_add_ons,
            'default_add_ons': policy.default_add_ons,
            'policy_document_url': policy.get_policy_document_url() if policy.policy_document else '',
            'product_logo_url': logo_url,
            'policy_created_on': localtime(policy.created_on).strftime("%d %b, %Y"),
            'policy_updated_on': localtime(policy.created_on).strftime("%d %b, %Y"),
        }

        return JsonResponse(response, safe=False)


class PolicyDeleteAttachmentView(DeleteAttachmentView):
    permission_required = ('auth.update_health_policies',)
    attached_model = HealthPolicy

    def post(self, request, *args, **kwargs):
        attachment = self.get_object()

        if attachment.content_type != ContentType.objects.get_for_model(self.attached_model):
            return JsonResponse({'success': False}, status=403)

        attached_obj = attachment.attached_to
        if hasattr(attached_obj, 'get_audit_trail'):
            audit_trail = attached_obj.get_audit_trail()
            audit_trail.record_generic_history(
                'remove attachment',
                f'Removed attachment. Label: {attachment.label}. URL: {attachment.get_file_url()}',
                self.request.user
            )
            audit_trail.save()

        attachment.delete()

        return JsonResponse({'success': True})


class PolicyFieldOptionsView(LoginRequiredMixin, View):
    permission_required = ('auth.create_health_policies',)

    def get(self, request):
        field = request.GET.get('field', None)
        value = request.GET.get('val', None)

        qs = None

        if field == 'customer':
            qs = list(
                Deal.objects.filter(customer_id=value, company=self.request.company)
                            .values_list('id', 'cached_car_name')
                            .exclude(is_deleted=True)
            )

        if field == 'deal':
            qs = list(
                Quote.objects.filter(deal_id=value, company=self.request.company)
                             .values_list('id', 'reference_number')
            )

        if field == 'quote':
            qs = list(
                QuotedPlan.objects.filter(quote_id=value)
                                     .values_list('id', 'product__code')
            )

        return JsonResponse(qs, safe=False)


class PolicyImportEmailView(LoginRequiredMixin, View):
    permission_required = ('auth.import_health_policies',)

    def post(self, request):
        if not len(self.request.FILES):
            return JsonResponse({'success': False})
        else:
            file = list(self.request.FILES.values())[0]

        emailer = Emailer(self.request.company)

        emailer.send_general_email(
            to_email='support@felix.insure',
            subject='{} from {} has requested to import policies'.format(
                self.request.user.get_full_name(), self.request.company.name),
            content='{} has uploaded a csv file ({}) to import policies'.format(
                self.request.user.get_full_name(), file.name),
            from_email=settings.DEFAULT_FROM_EMAIL,
            attachments=[(
                file.name,
                file
            )]
        )

        return JsonResponse({'success': True}, safe=False)
