import logging
from django.utils import timezone

from django.db.models import F
from django.http.response import JsonResponse
from django.views.generic import View
from motorinsurance.helpers import CarTreeHelper

from core.algodriven import AlgoDriven

from accounts.models import AlgoDrivenUsage
from motorinsurance_shared.models import CarTrim

from felix.constants import ALGODRIVEN_FREE_EVALUATIONS

api_logger = logging.getLogger("api.algodriven")


class CarTreePartsView(View):
    def get(self, request):
        year, make = request.GET["year"], request.GET.get("make")
        if make:
            return JsonResponse(data={"models": CarTreeHelper.get_models_and_trims_for_year_and_make(year, make)})
        else:
            return JsonResponse(data={"makes": CarTreeHelper.get_makes_for_year(year)})


class CarValuationGuideView(View):
    def get(self, request):
        trim = request.GET.get("trim")

        if not self._is_allowed():
            return JsonResponse({
                'success': False,
                'error': 'Your organisation has already used up your monthly quota of {} vehicle valuation checks.\
                          To enable more checks please reach out to us via live chat. \
                          At the beginning of next month you will automatically get another {} \
                          free valuation checks.'.format(
                              self.request.company.workspacemotorsettings.algodriven_credits,
                              ALGODRIVEN_FREE_EVALUATIONS)
            })

        if trim:
            algo_obj = AlgoDriven()

            try:
                car_trim = CarTrim.objects.get(pk=trim)

                if car_trim.algo_driven_id:
                    pricing = algo_obj.get_pricing(car_trim.algo_driven_id)

                    if pricing.status_code == 200:

                        self._record_usage()

                        if type(pricing) == 'list' and 'error' in pricing[0]:
                            api_logger.error('AlgoDriven raised error: {}'.format(pricing[0]['error']))

                            return JsonResponse({
                                'success': False,
                                'error': 'The pricing functionality is currently facing some issues and will be back online shortly.'
                            })
                        else:
                            return JsonResponse({
                                'success': True,
                                'low_retail': '{:,}'.format(pricing.json()['lowRetail']),
                                'high_retail': '{:,}'.format(pricing.json()['highRetail']),
                            })

            except CarTrim.DoesNotExist:
                pass

        return JsonResponse({'success': False, 'error': 'No pricing available for this vehicle.'})

    def _is_allowed(self):
        credits = self.request.company.workspacemotorsettings.algodriven_credits
        credits_used = self.request.company.get_algodrive_usage_for_current_month()

        return credits_used < credits

    def _record_usage(self):
        year, month = timezone.now().year, timezone.now().month
        record, created = AlgoDrivenUsage.objects.get_or_create(
            company=self.request.company,
            year=year,
            month=month
        )

        record.count = F('count') + 1
        record.save()
