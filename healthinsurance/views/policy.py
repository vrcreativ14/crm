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
from healthinsurance.forms.policy import PolicySearchAndOrderingForm
from healthinsurance.forms.deal import HealthPolicyForm, CustomerForm
from healthinsurance.models.deal import Deal
from healthinsurance.models.quote import Quote, QuotedPlan, Order
from healthinsurance.models.policy import HealthPolicy, PolicyFiles
from django.contrib.auth.models import User
from healthinsurance.constants import DEAL_TYPE_RENEWAL
from django.urls import reverse
import math


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
            qs = qs.filter(user=self.request.user)

        return qs

    def get_search_and_ordering_form(self):
        return PolicySearchAndOrderingForm(data=self.request.GET, company=self.request.company)


class PolicyListView(PolicyBaseView, TemplateView):
    template_name = "healthinsurance/policies_list.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super(PolicyListView, self).get_context_data(**kwargs)
        self.request.session['selected_product_line'] = 'health-insurance'
        policies = self.get_queryset()
        
        ctx['policies'] = policies
        ctx['search_form'] = self.get_search_and_ordering_form()
        #ctx['policy_form'] = NewPolicyForm(company=self.request.company)
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


class PolicyAddView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'auth.create_health_policies'
    
    def post(self, request):
        updated_request = request.POST.copy()
        reference_number = ''
        updated_request.update({'company':self.request.company,        
        'user':self.request.user,
        })
        customer_id = request.POST.get('customer')
        customer_name = request.POST.get('name')
        policy_num = request.POST.get('policy_number')
        policy = HealthPolicy.objects.filter(policy_number = policy_num)
        if policy.exists():
            return JsonResponse({
                    "success": False, 
                    "errors": 'Policy with this policy number already exists'
                })

        if customer_id:
            customer = Customer.objects.filter(pk = customer_id)
            if customer.exists():
                customer = customer[0]
        else:
            customer_form = CustomerForm(updated_request)
            if customer_form.is_valid():
                customer = customer_form.save()
            else:
                return JsonResponse({
                    "success": False, "errors": customer_form.errors
                })
        
        start_date = request.POST.get('start_date', None)
        start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y") if start_date else None
        expiry_date = request.POST.get('expiry_date',None)
        expiry_date = datetime.datetime.strptime(expiry_date, "%d/%m/%Y") if expiry_date else None
        updated_request.update({
        'customer':customer,
        'start_date':start_date,
        'expiry_date':expiry_date
        })
        
        policy_form = HealthPolicyForm(updated_request)
        if policy_form.is_valid():
            policy = policy_form.save()
            for file in request.FILES:
                PolicyFiles.objects.create(file = request.FILES[file], type=file, policy = policy)
        else:
            print(policy_form.errors)
            return JsonResponse({
                    "success": False, "errors": policy_form.errors
                })
        
        return JsonResponse({
            'success':True            
        })

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
    required_permission = 'list_health_policies'
    model = HealthPolicy

    def get(self, request, *args, **kwargs):
        policy = self.get_object()
        deal = policy.deal
        order = None
        if deal:
            order = Order.objects.filter(deal = deal)
            order = order[0] if order else None
        if order:
            logo_url = order.selected_plan.plan.get_logo() if order else '' #policy.product.get_logo()
        else:
            logo_url = ''
        selected_plan = deal.selected_plan.name if deal and deal.selected_plan else None
        policy_files = PolicyFiles.objects.filter(policy = policy)
        files_type = ['receipt_of_payment','tax_invoice','certificate_of_insurance','medical_card','confirmation_of_cover']
        
        response = {
            'source_deal_id': deal.pk if deal else '',
            'source_deal_title': f'{deal}' if deal else '',
            'insurer': deal.selected_plan.insurer.name if deal and deal.selected_plan else None,
            'selected_plan': selected_plan,
            'deal_members_count': deal.primary_member.additional_members.all().count() + 1 if deal else '',
            'consultant': policy.referrer.get_full_name() if policy.referrer else '',
            'policy_number': policy.policy_number,
            'policy_start_date': policy.start_date,
            'policy_expiry_date': policy.expiry_date,
            'policy_status': policy.get_policy_expiry_status(),
            'customer': policy.customer.name,
            'primary_member_name': deal.primary_member.name if deal else '',            
            'currency': deal.selected_plan.currency if deal and deal.selected_plan else request.company.companysettings.get_currency_display(),
            'premium': '{:,}'.format(policy.total_premium_vat_inc) if policy.total_premium_vat_inc else '',            
            'commission': '{:,}'.format(policy.commission) if policy.commission else '',
            'product_logo_url': logo_url,
            'policy_created_on': localtime(policy.created_on).strftime("%d %b, %Y"),
            'policy_updated_on': localtime(policy.updated_on).strftime("%d %b, %Y"),            
        }

        for type in files_type:
            file = policy_files.filter(type = type)
            response[type] = file[0].file.url if file.exists() else ''

        
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

def GetPolicyQueryset(param, **kwargs):
    today = datetime.date.today()
    range = kwargs.get('range')
    policies = kwargs.get('policies')
    expiry_date = ''
    if param == 'range_expiry':
        if range:
            range = range.lower()
            if range == 'today':
                expiry_date = today
            elif range == 'tomorrow':
                expiry_date = today + datetime.timedelta(days=1)
            elif range == 'next 7 days':
                expiry_date = today + datetime.timedelta(days=7)
            elif range == 'next 30 days':
                expiry_date = today + datetime.timedelta(days=30)
            elif range == 'next 60 days':
                expiry_date = today + datetime.timedelta(days=60)
            elif range == 'this month':
                start_date = today.replace(day=1)
                next_month = today.replace(day=28) + datetime.timedelta(days=4)
                end_date = next_month - datetime.timedelta(days=next_month.day)
                if policies and policies.count() > 0:
                    qs = policies.filter(
                expiry_date__gte = start_date, expiry_date__lte=end_date)
                else:
                    qs = HealthPolicy.objects.filter(
                    expiry_date__gte = start_date, expiry_date__lte=end_date)
            elif range == 'next month':
                next_month = today.replace(day=28) + datetime.timedelta(days=4)
                start_date = today.replace(day=1,month=next_month.month)                
                end_date = next_month - datetime.timedelta(days=next_month.day)
                if policies and policies.count() > 0:
                    qs = policies.filter(
                expiry_date__gte = start_date, expiry_date__lte=end_date)
                else:
                    qs = HealthPolicy.objects.filter(
                    expiry_date__gte = start_date, expiry_date__lte=end_date)
            elif range == 'next 12 months':
                next_year = today.replace(month=12) + datetime.timedelta(days=31)               
                end_date = next_year.replace(month = today.month)
                qs = HealthPolicy.objects.filter(
                expiry_date__gte = today, expiry_date__lte=end_date)
        if filter and filter == 'hide_renewal':
            qs = qs.exclude(deal__deal_type = DEAL_TYPE_RENEWAL)
        if expiry_date:
            qs = HealthPolicy.objects.filter(
                expiry_date__gte=today, expiry_date__lte=expiry_date)

    return qs

def PolicyJsonView(request):
        data = []
        start = request.GET.get('start')
        length = request.GET.get('length')
        if start and length:
            start = int(start)
            length = int(length)
            page = math.ceil(start / length) + 1
            per_page = length
        search_term = request.GET.get('search[value]')
        range_expiry = request.GET.get('range_expiry')
        hide_renewals = request.GET.get('hide_renewals')
        policies = None
        if(search_term):
            policies = HealthPolicy.objects.filter(Q(policy_number__icontains = search_term) | Q(customer__name__icontains = search_term))
            recordsTotal= policies.count()
            policies = policies[start:start + length]
        elif range_expiry:
            policies = GetPolicyQueryset('range_expiry', range = range_expiry, policies = policies)
            recordsTotal= policies.count()
            policies = policies[start:start + length]
        elif hide_renewals == 'true':
            policies = GetPolicyQueryset('hide_renewals', range = range_expiry, policies = policies)
            recordsTotal= policies.count()
            policies = policies[start:start + length]
        else:
            policies = HealthPolicy.objects.order_by()[start:start + length]
            recordsTotal= HealthPolicy.objects.all().count()
        
        for policy in policies:
            status = f'''<td><span class="stage-icon status-{policy.get_policy_expiry_status()}">
                </span>{policy.get_policy_expiry_status()}</td>'''
                #deal_url = reverse('health-insurance:deal-details', kwargs=dict(pk=policy.deal.pk))
            if policy.customer:
                # customer_link = f'''<a class="link"
                # href={reverse('customers:edit', kwargs=dict(pk=policy.customer.pk))}>{policy.customer.name}</a>'''
                p = {
                    'id' : policy.pk,
                    'status' : status,
                    'policy_number' : policy.policy_number,
                    'deal' : policy.deal.customer.name if policy.deal else '',
                    'customer': policy.customer.name,
                    'referrer': policy.referrer.get_full_name() if policy.referrer else '',
                    'selected_plan': policy.deal.selected_plan.name if policy.deal and policy.deal.selected_plan else '',
                    'total_premium': policy.total_premium_vat_inc,
                    'start_date': policy.start_date.strftime('%b. %d %Y'),
                    'expiry_date': policy.expiry_date.strftime('%b. %d %Y'),
                }
                data.append(p)
        
        resp = {
            'data' : data,
            'page': page,
            'per_page' : per_page,
            'recordsTotal':recordsTotal,
            'recordsFiltered': recordsTotal,
        }
        return JsonResponse(resp, safe=False)
