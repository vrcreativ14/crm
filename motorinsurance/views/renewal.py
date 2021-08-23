import logging
import datetime

from django.conf import settings
from django.http.response import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, View
from django.db.models import Q

from core.algolia import Algolia
from core.utils import log_user_activity
from core.amplitude import Amplitude
from accounts.roles import Producer

from motorinsurance.views.policy import PolicyBaseView
from motorinsurance.forms.policy import RenewalsSearchAndOrderingForm
from motorinsurance.models import Policy, Deal

from felix.exporter import ExportService

api_logger = logging.getLogger("api.amplitude")


class RenewalView(PolicyBaseView, TemplateView):
    template_name = "motorinsurance/renewal/renewal_list.djhtml"
    permission_required = ('auth.list_motor_policies', 'auth.create_motor_deals', )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        filters = ''
        if self.request.user.userprofile.has_producer_role():
            filters = "owner_id:{user_id}".format(user_id=self.request.user.pk)

        ctx['search_form'] = RenewalsSearchAndOrderingForm(data=self.request.GET)

        ctx['algolia_secured_search_api_key'] = Algolia().get_secured_search_api_key(
            filters=filters
        )

        ctx['page'] = self.request.GET.get('page') or 1
        ctx['sort_by'] = self.request.GET.get('sort_by') or 'policy_expiry_date_asc'
        ctx['to_date'] = self.request.GET.get('to_date') or ''
        ctx['from_date'] = self.request.GET.get('from_date') or ''
        ctx['current_timestamp'] = datetime.datetime.today().strftime('%s')

        log_user_activity(self.request.user, self.request.path)

        return ctx


class RenewalCountView(PolicyBaseView, View):
    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()

        today = datetime.date.today()
        expiry_date = today + datetime.timedelta(days=60)

        qs = qs.filter(
            policy_expiry_date__gte=today, policy_expiry_date__lte=expiry_date)

        return JsonResponse({'count': qs.count()}, safe=False)


class CreateRenewalDealView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('auth.create_motor_deals',)

    def get(self, request):
        policy_ids = request.GET['pids']

        if policy_ids:
            response = []
            errors = []
            policies = Policy.objects.filter(id__in=policy_ids.split(','), company=request.company)

            for policy in policies:
                error_occurred = False

                if getattr(policy, 'deal', None):
                    deal = policy.deal
                    deal.pk = None
                    # These are the fields need to be resetted in order to
                    # create a new deal from an existing one.
                    deal.lead = None
                    deal.stage = Deal.STAGE_NEW
                    deal.renewal_for_policy = policy
                    deal.quote_sent = False
                    deal.is_deleted = False
                    deal.deal_type = Deal.DEAL_TYPE_RENEWAL
                    deal.save(user=self.request.user)
                else:
                    if policy.car_year and policy.car_make:
                        deal = Deal(
                            lead=None,
                            company=policy.company,
                            customer=policy.customer,
                            renewal_for_policy=policy,
                            deal_type=Deal.DEAL_TYPE_RENEWAL,
                            car_year=policy.car_year,
                            car_make=policy.car_make,
                            car_trim=policy.car_trim,
                            vehicle_insured_value=policy.insured_car_value,
                            custom_car_name=policy.custom_car_name,
                        )
                        deal.save(user=self.request.user)
                    else:
                        errors.append('Unable to create renewal deal for policy [{}]. Contact support'.format(
                                      policy.reference_number))
                        error_occurred = True

                if not error_occurred:
                    response.append({
                        'new_deal_id': deal.pk,
                        'policy_number': policy.reference_number,
                        'expiring_insurer': policy.product.insurer.name,
                        'expiring_product': policy.get_title()
                    })

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
                        api_logger.error('Amplitude error while logging "motor deal created" Source: %s, Error: %s',
                                         'renewal', e)

            return JsonResponse({'success': True, 'new_deals_data': response, 'errors': errors})

        return JsonResponse({'success': False, 'message': 'Please select one or more policy records'})


class RenewalExportView(View):
    permission_required = 'auth.export_motor_deals'
    default_order_by = 'policy_expiry_date_asc'

    def get_queryset(self):
        query = ''
        filters = ''
        facets = []
        sort_by = self.default_order_by
        facet_filters = list()
        numeric_filters = list()

        form = self.get_search_and_ordering_form()

        if form.is_valid():
            expiry_from = form.cleaned_data['from_date']
            expiry_till = form.cleaned_data['to_date']
            hide_renewed = form.cleaned_data['hide_renewal_deal']
            search_term = form.cleaned_data['search_term']

            sort_indexes = ['policy_expiry_date_asc',
                            'policy_expiry_date_desc',
                            'policy_start_date_asc',
                            'policy_start_date_desc']

            if self.request.GET.get('sort_by') and self.request.GET.get('sort_by') in sort_indexes:
                sort_by = self.request.GET.get('sort_by')

            facet_filters.append('status:active')

            if hide_renewed:
                facet_filters.append('has_renewal_deal:false')

            if expiry_from:
                numeric_filters.append('policy_expiry_date > {}'.format(expiry_from))

            if expiry_till:
                numeric_filters.append('policy_expiry_date <= {}'.format(expiry_till))

            if search_term:
                query = search_term

        if self.request.user.userprofile.has_producer_role():
            facet_filters.append(f'producer_id:{self.request.user.pk}')

        index_name = f'{settings.ALGOLIA["ENV"]}_motor_policies_{self.request.company.pk}_{sort_by}'
        index = Algolia().get_index(index_name)

        params = {
            'query': query,
            'filters': filters,
            'facets': facets,
            'facetFilters': facet_filters,
            'numericFilters': numeric_filters
        }

        return index.browse_all(params)

    def get_search_and_ordering_form(self):
        return RenewalsSearchAndOrderingForm(data=self.request.GET)

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = list()
        column_labels = [
            'Status',
            'Policy Number',
            'Renewal Deal',
            'Selected Product',
            'Premium',
            'Deductible',
            'Owner',
            'Customer',
            'Phone',
            'Email',
            'Nationality',
            'DOB',
            'Year',
            'Make',
            'Model/Trim',
            'Sum Insured',
            'Policy Start Date',
            'Policy Expiry Date']

        policy_ids = [r['objectID'] for r in qs]
        policies = Policy.objects.filter(pk__in=policy_ids)

        for policy in qs:
            data.append([
                policy['status'].title(),
                policy['reference_number'],

                'Yes' if policy['has_renewal_deal'] else 'No',
                policy['product_name'],

                '{:,}'.format(policy['premium']) if policy['premium'] else '',
                '{:,}'.format(policy['deductible']) if policy['deductible'] else '',

                policy['owner_name'],

                policy['customer_name'],
                policy['customer_phone'],
                policy['customer_email'],
                policy['customer_nationality'],
                policy['customer_dob'],

                policy['car_year'],
                policy['car_make'],
                policy['car_trim'],

                '{:,}'.format(policy['car_value']) if policy['car_value'] else '',

                policy['policy_start_date_display'],
                policy['policy_expiry_date_display']
            ])

        exporter = ExportService()

        return exporter.to_csv(column_labels, data, filename='renewals-{}.csv'.format(datetime.datetime.today()))
