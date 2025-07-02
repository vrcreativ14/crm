"""Views that serve data and pages for the motor insurance dashboard"""
import datetime
import dateutil.relativedelta
from dateutil.rrule import MONTHLY, rrule
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse
from django.views.generic import View
from mortgage.models import Deal, Order, Bank
from datetime import date, timedelta
from itertools import groupby
from mortgage.constants import *
from django.db.models import Q
from django.utils.dateparse import parse_datetime


today = date.today()


def get_last_12_month_dates():
    """Returns a list of month starting date objects for the last 12 months"""
    start_date = datetime.date.today().replace(
        day=1
    ) + dateutil.relativedelta.relativedelta(years=-1, months=1)
    month_dates = list(rrule(MONTHLY, start_date, count=13))

    return month_dates


def get_month_pairs_for_last_12_months():
    """Returns a list of 11 pairs that make up the monthly intervals for the last year"""
    month_dates = get_last_12_month_dates()
    month_ranges = [month_dates[i: i + 2] for i in range(12)]

    return month_ranges


class BaseChartDataView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "auth.company_dashboard"

    def dispatch(self, request, *args, **kwargs):
        self.params = self.request.GET.dict()
        if self.params.get('start_date'):
            if parse_datetime(self.params.get('start_date')):
                self.params['start_date'] = parse_datetime(self.params.get('start_date')).date()
        if self.params.get('end_date'):
            if parse_datetime(self.params.get('end_date')):
                self.params['end_date'] = parse_datetime(self.params.get('end_date')).date()
        return super().dispatch(request, *args, **kwargs)

    def get_user_filter(self):
        user = self.params.get("user")
        try:
            user = User.objects.get(pk=user)
        except User.DoesNotExist:
            user = None

        return user

    def get_chart_data(self, querytype=None):

        if not querytype:
            return

        if querytype == "mortgagedeals":
            self.deals = Deal.objects.all()
            if self.params.get('filtertype') == 'date':
                start_date = today - timedelta(weeks=52)
                self.deals = self.deals.filter(created_date__range=[self.params.get('start_date'), self.params.get('end_date')]).order_by('created_date')
            else:
                start_date = today - timedelta(weeks=52)
                self.deals = self.deals.filter(created_date__range=[start_date, today]).order_by('created_date')

            if self.params.get('user'):
                self.deals = self.deals.filter(
                    Q(user_id=self.get_user_filter()) | Q(referrer_id=self.get_user_filter())
                )

        elif querytype == "wonbank":
            self.deals = Order.objects.filter(deal__stage=STAGE_ClosedWON)
            if self.params.get('filtertype') == 'date':
                self.deals = self.deals.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')]).order_by('created_on')

            elif self.params.get('filtertype') == 'month':
                start_date = today - timedelta(weeks=52)
                self.deals = self.deals.filter(created_on__range=[start_date, today]).order_by('created_on')

            if self.params.get('user'):
                self.deals = self.deals.filter(
                    Q(deal__user_id=self.get_user_filter()) | Q(deal__referrer_id=self.get_user_filter())
                )
        elif querytype == "lostdeals":
            self.deals = Deal.objects.filter(stage=STAGE_ClosedLOST).order_by('created_date')

        elif querytype == "totaldeals":
            self.deals = Deal.objects.filter(status=STATUS_ACTIVE).order_by('created_date')
            if self.params.get('user'):
                self.deals = self.deals.filter(
                    Q(user_id=self.get_user_filter()) | Q(referrer_id=self.get_user_filter())
                )
            elif self.params.get('filtertype') == 'month':
                start_date = today - timedelta(weeks=52)
                self.deals = self.deals.filter(created_date__range=[start_date, today]).order_by('created_date')

            elif self.params.get('filtertype') == 'date':
                self.deals = self.deals.filter(created_date__range=[self.params.get('start_date'), self.params.get('end_date')]).order_by('created_date')
            
        elif querytype == "total-won-deals":
            self.deals = Deal.objects.filter(status=STATUS_ACTIVE, stage=STAGE_ClosedWON).order_by('created_date')
            if self.params.get('user'):
                self.deals = self.deals.filter(
                    Q(user_id=self.get_user_filter()) | Q(referrer_id=self.get_user_filter())
                )
        elif querytype == "won_deals":
            self.deals = Deal.objects.filter(status=STATUS_ACTIVE, stage=STAGE_ClosedWON).order_by('created_date')
            if self.params.get('user'):
                self.deals = self.deals.filter(
                    Q(user_id=self.get_user_filter()) | Q(referrer_id=self.get_user_filter())
                )


    def get_active_deals(self):
        return Deal.objects.filter(status='active')

    def get_lost_deals(self):
        lost_deal = self.request.GET.get("STAGE_ClosedLOST")

        try:
            lost_deal = Deal.objects.get(pk=lost_deal, DEAL_STAGES='Closed Lost')
        except Deal.DoesNotExist:
            lost_deal = None
        return lost_deal

class DealsFilter():
    def __init__(self, queryset, params):
        self.params = params
        self.deals=queryset
        chart_data = []
        date_holder =[]
        today_date = date.today()
        if self.params.get('filtertype') == "date":
            grouping_function = lambda deal: deal.created_date
            for x, y in groupby(self.deals, grouping_function):
                    chart_data.append((x,len(list(y))))
                    date_holder.append(x)
            start_date = self.params.get('start_date')
            while start_date <= self.params.get('end_date'):
                    if start_date not in date_holder:
                        chart_data.append((start_date,0))
                    start_date = start_date + timedelta(days=1)
            chart_data.sort(key= lambda x:x[0])
            self.final_result = [ (x.strftime('%b, %d'),y) for x,y  in chart_data ]

        else:
            grouping_function = lambda deal: deal.created_date.month
            
            for x, y in groupby(self.deals, grouping_function):
                temp_date = today_date.replace(month=x, day=1)
                chart_data.append((temp_date,len(list(y))))
                date_holder.append(temp_date)
            for x in [v.date() for v in get_last_12_month_dates()]:
                if x not in date_holder:
                    chart_data.append((x,0))
            chart_data.sort(key= lambda x:x[0])
            self.final_result =  [ (x.strftime('%b, %y'),y) for x,y  in chart_data ]

    def get_result(self):
        return self.final_result


class MortgageDealsCreatedCountView(BaseChartDataView):
    def get(self, request):
        self.get_chart_data(querytype='mortgagedeals')
        deals_filter = DealsFilter(self.deals, self.params)
        return JsonResponse(deals_filter.get_result(), safe=False)


class BankActiveDealsView(BaseChartDataView):
    def get(self, request):
        self.get_chart_data(querytype='wonbank')
        chart_data = []
        date_holder =[]
        today_date = date.today()
        if self.params.get('filtertype') == "date":
            grouping_function = lambda deal: deal.bank
            for x, y in groupby(self.deals, grouping_function):
                    chart_data.append((x.name,len(list(y))))
                    date_holder.append(x)
            for x in Bank.objects.all():
                if x not in date_holder:
                    chart_data.append((x.name,0))
            chart_data.sort(key= lambda x:x[0])
            final_result = chart_data

        else:
            grouping_function = lambda deal: deal.bank
            for x, y in groupby(self.deals, grouping_function):
                chart_data.append((x.name,len(list(y))))
                date_holder.append(x.name)

            for x in Bank.objects.all():
                if x not in date_holder:
                    chart_data.append((x.name,0))
            chart_data.sort(key= lambda x:x[0])
            final_result = chart_data
        return JsonResponse(final_result, safe=False)



class BankLostDealsView(BaseChartDataView):
    def get(self, request):
        self.get_chart_data(querytype='lostdeals')
        deals_filter = DealsFilter(self.deals, self.params)
        return JsonResponse(deals_filter.get_result(), safe=False)


class TotalDealsView(BaseChartDataView):
    def get(self, request):
        self.get_chart_data(querytype='totaldeals')
        deals_filter = DealsFilter(self.deals, self.params)
        return JsonResponse(deals_filter.get_result(), safe=False)

class DealsWonView(BaseChartDataView):
    def get(self, request):
        self.get_chart_data(querytype='won_deals')
        deals_filter = DealsFilter(self.deals, self.params)
        return JsonResponse(deals_filter.get_result(), safe=False)


class TotalWonView(BaseChartDataView):
    def get(self, request):
        self.get_chart_data(querytype='total-won-deals')
        x_axis = []
        chart_data = []
        if self.params.get('filtertype') == "date":
            grouping_function = lambda deal: deal.created_date
            loan = 0
            for x,y in groupby(self.deals, grouping_function):
                for deal in y:
                    loan += deal.loan_amount
                chart_data.append((deal.created_date,loan ))
                x_axis.append(deal.created_date)
            start_date = self.params.get('start_date')
            while start_date <= self.params.get('end_date'):
                    if start_date not in x_axis:
                        chart_data.append((start_date,0))
                    start_date = start_date + timedelta(days=1)
            chart_data.sort(key= lambda x:x[0])
            self.final_result =  [ (x.strftime('%b, %d'),y/10) for x,y  in chart_data ]

        else:
            grouping_function = lambda deal: deal.created_date.month
            loan = 0
            for x,y in groupby(self.deals, grouping_function):
                for deal in y:
                    loan += deal.loan_amount
                chart_data.append((deal.created_date.replace(day=1),loan ))
                x_axis.append(deal.created_date.replace(day=1))
            for x in [v.date() for v in get_last_12_month_dates()]:
                if x not in x_axis:
                    chart_data.append((x,0))
            chart_data.sort(key= lambda x:x[0])
            self.final_result =  [ (x.strftime('%b, %y'),y) for x,y  in chart_data ]

        return JsonResponse(self.final_result, safe=False)