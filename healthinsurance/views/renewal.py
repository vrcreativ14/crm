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

api_logger = logging.getLogger("api.amplitude")


class RenewalView(PolicyBaseView,TemplateView):
    template_name = "healthinsurance/renewal/renewal_list.djhtml"
    permission_required = ('auth.list_health_policies', 'auth.create_health_deals', )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['policies'] = self.get_queryset()
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
        qs = self.get_queryset()
        today = datetime.date.today()
        range = request.GET.get('range')
        filter = request.GET.get('filter')
        expiry_date = ''
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
        for policy in qs:
            response = {}
            response['status'] = policy.status
            response['policy_number'] = policy.policy_number
            response['deal'] = policy.deal.primary_member.name if policy.deal else '-'
            response['customer'] = policy.customer.name if policy.customer else '-'
            response['owner'] = policy.user.username if policy.user else '-'
            response['insurer'] = policy.deal.selected_plan.insurer.name if policy.deal and policy.deal.selected_plan else '-'
            response['premium'] = policy.total_premium_vat_inc
            response['expiry_date'] = policy.expiry_date.strftime('%b. %d %Y')
            response['tr_id'] = policy.pk
            policies.append(response)

        policy_serializer = PolicySerializer(qs, many = True)
        return JsonResponse({'qs': policies}, safe=False)


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
                        deal.renewal_for_policy = policy
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
            errors.append('Unable to create renewal deal for policy [{}]. Contact support'.format(
                                      policy.reference_number))
            return JsonResponse({'success': False, 'message': 'Please select one or more policy records'})
