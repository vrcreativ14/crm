"""Views that serve data and pages for the motor insurance dashboard"""
import datetime
import dateutil.relativedelta
from dateutil.rrule import rrule, MONTHLY
from django.db.models import Sum
from django.http import JsonResponse

from django.contrib.auth.models import User

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

from motorinsurance.models import Deal, Order
from felix.exporter import ExportService


def get_last_12_month_dates():
    """Returns a list of month starting date objects for the last 12 months"""
    start_date = datetime.date.today().replace(day=1) + dateutil.relativedelta.relativedelta(years=-1, months=1)
    month_dates = list(rrule(MONTHLY, start_date, count=13))

    return month_dates


def get_month_pairs_for_last_12_months():
    """Returns a list of 11 pairs that make up the monthly intervals for the last year"""
    month_dates = get_last_12_month_dates()
    month_ranges = [month_dates[i:i + 2] for i in range(12)]

    return month_ranges


class BaseChartDataView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'auth.company_dashboard'

    def get_user_filter(self):
        user = self.request.GET.get('user')

        try:
            user = User.objects.get(pk=user, userprofile__company=self.request.company)
        except User.DoesNotExist:
            user = None

        return user


class MotorDealsCreatedCountView(BaseChartDataView):
    def get(self, request):
        user = self.get_user_filter()
        month_ranges = get_month_pairs_for_last_12_months()

        base_qs = Deal.objects.filter(company=request.company, is_deleted=False)

        if user:
            base_qs = base_qs.filter(assigned_to=user)

        chart_data = list()
        for sd, ed in month_ranges:
            month_label = sd.strftime('%b, %y')
            chart_data.append((
                month_label, base_qs.filter(created_on__range=(sd, ed)).count()
            ))

        return JsonResponse(chart_data, safe=False)


class MotorOrdersCreatedCountView(BaseChartDataView):
    def get(self, request):
        user = self.get_user_filter()
        month_ranges = get_month_pairs_for_last_12_months()

        base_qs = Order.objects.filter(deal__company=request.company, deal__is_deleted=False, is_void=False)

        if user:
            base_qs = base_qs.filter(deal__assigned_to=user)

        chart_data = list()
        for sd, ed in month_ranges:
            month_label = sd.strftime('%b, %y')
            chart_data.append((
                month_label, base_qs.filter(created_on__range=(sd, ed)).count()
            ))

        return JsonResponse(chart_data, safe=False)


class MotorOrdersTotalPremiumView(BaseChartDataView):
    def get(self, request):
        user = self.get_user_filter()
        month_ranges = get_month_pairs_for_last_12_months()

        base_qs = Order.objects.filter(deal__company=request.company, deal__is_deleted=False, is_void=False)

        if user:
            base_qs = base_qs.filter(deal__assigned_to=user)

        chart_data = list()
        for sd, ed in month_ranges:
            month_label = sd.strftime('%b, %y')
            total_premium = (
                base_qs
                .filter(created_on__range=(sd, ed))
                .aggregate(total_premium=Sum('payment_amount'))
            )['total_premium'] or 0.0
            chart_data.append((
                month_label,
                total_premium
            ))

        return JsonResponse(chart_data, safe=False)


class MotorSalesConversionRateView(BaseChartDataView):
    def get(self, request):
        user = self.get_user_filter()
        month_ranges = get_month_pairs_for_last_12_months()

        deal_qs = Deal.objects.filter(company=request.company, is_deleted=False)

        if user:
            deal_qs = deal_qs.filter(assigned_to=user)

        chart_data = list()
        for sd, ed in month_ranges:
            month_label = sd.strftime('%b, %y')

            deals = deal_qs.filter(created_on__range=(sd, ed))
            order_qs = Order.objects.filter(is_void=False, deal__in=deals)
            number_of_orders = order_qs.filter(created_on__range=(sd, ed)).count()
            number_of_deals = deals.count()

            if number_of_deals > 0:
                conversion_rate = number_of_orders / float(number_of_deals)
            else:
                conversion_rate = 0.0

            chart_data.append((
                month_label, '{:0.2f}'.format(conversion_rate * 100.0)
            ))

        return JsonResponse(chart_data, safe=False)

class DealReport(View):
    def get_user_filter(self):
        user = self.request.GET.get('user')
        try:
            user = User.objects.get(pk=user, userprofile__company=self.request.company)
        except User.DoesNotExist:
            user = None
        return user

    def get(self, request):
        data = list()
        columns = ['Month','No. of Motor Deals Created', 'No. of Motor Orders Created', 'Total Premium from Orders',
        'Sales Conversion Rate']
        for i in range(1,4):
            start_date = datetime.datetime(2021, i, 1)
            end_date = datetime.datetime(2021, i, 31) if i!=2 else datetime.datetime(2021, i, 28)
            deals = Deal.objects.filter(company=self.request.company, is_deleted=False, created_on__range=(start_date, end_date))
            orders = Order.objects.filter(deal__company=self.request.company, deal__is_deleted=False, is_void=False, created_on__range=(start_date, end_date))
            total_premium = orders.aggregate(total_premium=Sum('payment_amount'))['total_premium'] or 0.0
            number_of_orders = orders.count()
            number_of_deals = deals.count()
            month = ''
            if number_of_deals > 0:
                conversion_rate = number_of_orders / float(number_of_deals)
            else:
                conversion_rate = 0.0
            if i == 1:
                month = 'Jan 2021'
            elif i == 2:
                month = 'Feb 2021'
            elif i == 3:
                month = 'Mar 2021'

            data.append([
                month,
                number_of_deals,
                number_of_orders,
                total_premium,
                conversion_rate,
            ])
            

        exporter = ExportService()
        return exporter.to_csv(columns, data, filename='motor_deals_report{}.csv'.format(datetime.datetime.today()))
