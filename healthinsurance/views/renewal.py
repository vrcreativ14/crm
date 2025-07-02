import logging
import datetime
from urllib import response

from django.conf import settings
from django.http.response import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, View
from django.db.models import Q

from core.algolia import Algolia
from core.utils import log_user_activity
from core.amplitude import Amplitude
from accounts.roles import Producer

from healthinsurance.views.policy import PolicyBaseView
from motorinsurance.forms.policy import RenewalsSearchAndOrderingForm
from healthinsurance.models.deal import *
from healthinsurance.models.policy import *
from healthinsurance.serializers import PolicySerializer
from healthinsurance.constants import DEAL_TYPE_RENEWAL
from felix.exporter import ExportService
import math

api_logger = logging.getLogger("api.amplitude")


class RenewalView(PolicyBaseView,TemplateView):
    template_name = "healthinsurance/renewal/renewal_list.djhtml"
    permission_required = ('auth.list_health_policies', 'auth.create_health_deals', )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['policies'] = self.get_queryset()
        ctx['search_form'] = self.get_search_and_ordering_form()
        ctx['page'] = self.request.GET.get('page') or 1
        ctx['sort_by'] = self.request.GET.get('sort_by') or 'policy_expiry_date_asc'
        ctx['to_date'] = self.request.GET.get('to_date') or ''
        ctx['from_date'] = self.request.GET.get('from_date') or ''
        ctx['current_timestamp'] = datetime.datetime.today()
        ctx['entity'] = 'health'
        self.request.session['selected_product_line'] = 'health-insurance'
        log_user_activity(self.request.user, self.request.path)
        return ctx


class RenewalCountView(PolicyBaseView, View):
    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        today = datetime.date.today()
        expiry_date = today + datetime.timedelta(days=60)

        qs = qs.filter(
            expiry_date__gte=today, expiry_date__lte=expiry_date)

        return JsonResponse({'count': qs.count()}, safe=False)
        
class RenewalListFilter(PolicyBaseView, View):
    def get(self, request, *args, **kwargs):
        data = []
        qs = self.get_queryset()
        today = datetime.date.today()
        range = request.GET.get('range')
        filter = request.GET.get('filter')
        expiry_date = ''
        start = request.GET.get('start', '0')
        length = request.GET.get('length', '10')
        if start and length:
            start = int(start)
            length = int(length)
            page = math.ceil(start / length) + 1
            per_page = length
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
                qs = qs.filter(
                expiry_date__gte = start_date, expiry_date__lte=end_date)
            elif range == 'next month':
                next_month = today.replace(day=28) + datetime.timedelta(days=4)
                start_date = today.replace(day=1,month=next_month.month)                
                end_date = next_month - datetime.timedelta(days=next_month.day)
                qs = qs.filter(
                expiry_date__gte = start_date, expiry_date__lte=end_date)
            elif range == 'next 12 months':
                next_year = today.replace(month=12) + datetime.timedelta(days=31)               
                end_date = next_year.replace(month = today.month)
                qs = qs.filter(
                expiry_date__gte = today, expiry_date__lte=end_date)
        if filter and filter == 'hide_renewal':
            qs = qs.exclude(deal__deal_type = DEAL_TYPE_RENEWAL)
        if expiry_date:
            qs = qs.filter(
                expiry_date__gte=today, expiry_date__lte=expiry_date)
        policies = []
        recordsTotal= qs.count()
        checkbox = '''<td class="link"><label class="felix-checkbox">
            <input class="select-record" type="checkbox" data-id="{}" value="{}" />
            <span class="checkmark"></span>
        </label>
    </td>'''
        deal_link = ''
        for policy in qs:
            if policy.deal and policy.deal.deal_type == 'renewal':
                deal_url = reverse('health-insurance:deal-details', kwargs=dict(pk=policy.deal.pk))
                deal_link = f'''<a href="{deal_url}" class="link limit-text">{policy.deal.customer.name}</a>
                <span class="policy-renewal-badge badge badge-default badge-font-light 
                badge-{policy.deal.status_badge}">{policy.deal.deal_stage_text}</span>'''
            if policy.customer:
                customer_link = f'''<a class="link"
                href={reverse('customers:edit', kwargs=dict(pk=policy.customer.pk))}>{policy.customer.name}</a>'''
            p = {
                'id' : policy.pk,
                'checkbox' : checkbox.format(policy.pk, policy.pk),
                'status' : policy.status,
                'policy_number' : policy.policy_number,
                'deal' : deal_link,
                'customer': customer_link,
                'referrer':policy.referrer.get_full_name() if policy.referrer else '',
                'expiring_insurer':policy.deal.selected_plan.insurer.name if policy.deal and policy.deal.selected_plan else '',
                'total_premium':policy.total_premium_vat_inc,
                'expiry_date':policy.expiry_date.strftime('%b. %d %Y'),                
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
        # for policy in qs:
        #     response = {}
        #     response['status'] = policy.status
        #     response['policy_number'] = policy.policy_number
        #     response['deal'] = policy.deal.primary_member.name if policy.deal else '-'
        #     response['customer'] = policy.customer.name if policy.customer else '-'
        #     response['owner'] = policy.user.username if policy.user else '-'
        #     response['insurer'] = policy.deal.selected_plan.insurer.name if policy.deal and policy.deal.selected_plan else '-'
        #     response['premium'] = policy.total_premium_vat_inc
        #     response['expiry_date'] = policy.expiry_date.strftime('%b. %d %Y')
        #     response['tr_id'] = policy.pk
        #     policies.append(response)

        # policy_serializer = PolicySerializer(qs, many = True)
        # return JsonResponse({'qs': policies}, safe=False)


class CreateRenewalDealView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('auth.create_health_deals',)

    def get(self, request):
        try:
            policy_ids = request.GET['pids']
            if policy_ids:
                response = []
                errors = []
                policies = HealthPolicy.objects.filter(id__in=policy_ids.split(','), company=request.company)
                for policy in policies:
                    error_occurred = False
                    primary_member = PrimaryMember.objects.create(
                            name = policy.customer.name,
                            email = policy.customer.email,
                            phone = policy.customer.phone,
                            dob = policy.customer.dob,
                            marital_status = policy.customer.marital_status,
                            nationality = policy.customer.nationality,
                        )
                    if getattr(policy, 'deal', None):
                        deal = policy.deal
                        deal.pk = None
                        # These are the fields need to be resetted in order to
                        # create a new deal from an existing one.
                        
                        deal.stage = STAGE_NEW
                        #deal.renewal_for_policy = policy
                        deal.quote_sent = False
                        deal.is_deleted = False
                        deal.deal_type = DEAL_TYPE_RENEWAL
                        deal.primary_member = primary_member
                        deal.save(user=self.request.user)
                    else:
                        
                        deal = Deal(                            
                            customer=policy.customer,                            
                            deal_type=DEAL_TYPE_RENEWAL,                       
                            primary_member=primary_member,
                        )
                        deal.save(user=self.request.user)
                        policy.deal = deal
                        policy.save()

                    if not error_occurred:
                        response.append({
                            'new_deal_id': deal.pk,
                            'policy_number': policy.policy_number,
                            'expiring_insurer': deal.selected_plan.insurer.name if deal.selected_plan else '',
                            'expiring_plan': deal.selected_plan.name if deal.selected_plan else ''
                        })
                return JsonResponse({'success': True, 'new_deals_data': response, 'errors': errors})

        except Exception as e:
            api_logger.error('Error while creating "health renewal deal" Source: %s, Error: %s',
                                         'renewal', e)
            errors.append('Unable to create renewal deal for policy [{}]. Contact support'.format(
                                      policy.reference_number))
            return JsonResponse({'success': False, 'message': 'Please select one or more policy records'})

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
        
    if param == 'hide_renewals':
        # if policies and policies.count() > 0:
        #         qs = policies.exclude(deal__deal_type = DEAL_TYPE_RENEWAL)
        # else:
            qs = HealthPolicy.objects.exclude(deal__deal_type = DEAL_TYPE_RENEWAL)

    return qs


def RenewalPolicyJsonView(request):
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
        checkbox = '''<td class="link"><label class="felix-checkbox">
            <input class="select-record" type="checkbox" data-id="{}" value="{}" />
            <span class="checkmark"></span>
        </label>
    </td>'''
        deal_link = ''
        for policy in policies:
            if policy.deal and policy.deal.deal_type == 'renewal':
                deal_url = reverse('health-insurance:deal-details', kwargs=dict(pk=policy.deal.pk))
                deal_link = f'''<a href="{deal_url}" class="link limit-text">{policy.deal.customer.name}</a>
                <span class="policy-renewal-badge badge badge-default badge-font-light 
                badge-{policy.deal.status_badge}">{policy.deal.deal_stage_text}</span>'''
            if policy.customer:
                customer_link = f'''<a class="link"
                href={reverse('customers:edit', kwargs=dict(pk=policy.customer.pk))}>{policy.customer.name}</a>'''
            p = {
                'id' : policy.pk,
                'checkbox' : checkbox.format(policy.pk, policy.pk),
                'status' : policy.status,
                'policy_number' : policy.policy_number,
                'deal' : deal_link,
                'customer': customer_link,
                'referrer':policy.referrer.get_full_name() if policy.referrer else '',
                'expiring_insurer':policy.deal.selected_plan.insurer.name if policy.deal and policy.deal.selected_plan else '',
                'total_premium':policy.total_premium_vat_inc,
                'expiry_date':policy.expiry_date.strftime('%b. %d %Y'),
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