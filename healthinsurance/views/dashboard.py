"""Views that serve data and pages for the health insurance dashboard"""
import datetime as dt
import dateutil.relativedelta
from dateutil.rrule import MONTHLY, rrule
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse
from django.views.generic import View

from datetime import date, timedelta, datetime
from itertools import groupby
from healthinsurance.constants import *
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from healthinsurance.models.deal import Deal
from healthinsurance.models.quote import QuotedPlan,Order
from healthinsurance_shared.models import Insurer
from healthinsurance_shared.models import Plan



today = date.today()


def get_last_12_month_dates():
    """Returns a list of month starting date objects for the last 12 months"""
    start_date = dt.date.today().replace(
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
            if parse_datetime(self.request.GET.get('start_date')):
                self.params['start_date'] = parse_datetime(self.request.GET.get('start_date')).date()
        if self.params.get('end_date'):
            if parse_datetime(self.request.GET.get('end_date')):
                self.params['end_date'] = parse_datetime(self.request.GET.get('end_date')).date()
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
        if querytype == "healthdeals":
            self.deals = Deal.objects.all()
            if  self.params.get('user'):
                self.deals = self.deals.filter(user = self.params.get('user'))
                            
            if self.params.get('filtertype') == 'date':
                start_date = today - timedelta(weeks=52)
                # import pdb
                # pdb.set_trace()
                self.deals = self.deals.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')]).order_by('created_on')


            else:
                start_date = today - timedelta(weeks=52)
                self.deals = self.deals.filter(created_on__range=[start_date, timezone.now()]).order_by('created_on')

            # if self.params.get('user'):
            #     self.deals = self.deals.filter(
            #         Q(user_id=self.get_user_filter()) | Q(referrer_id=self.get_user_filter())
            #     )
        
        elif querytype == "won_deals":
            self.deals = Deal.objects.filter(stage='won').order_by('created_on')
            if self.params.get('user'):
                self.deals = self.deals.filter(
                    Q(user_id=self.get_user_filter()) | Q(referrer_id=self.get_user_filter())
                )
            if self.params.get('filtertype') == 'date': 
                start_date = today - timedelta(weeks=52)
                self.deals = self.deals.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')]).order_by('created_on')

          

        elif querytype == "lostdeals":
            Order
            self.deals = Deal.objects.filter(stage='lost').order_by('created_on')
            if  self.params.get('user'):
                self.deals = self.deals.filter(user = self.params.get('user'))

            if self.params.get('filtertype') == 'date': 
                start_date = today - timedelta(weeks=52)
                self.deals = self.deals.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')]).order_by('created_on')


        elif querytype == "by_insurer":
            # import pdb
            # pdb.set_trace()
            self.deals = Order.objects.filter(deal__stage = STAGE_WON).order_by('created_on')
            if self.params.get('user'):
                self.deals = Order.objects.filter(deal__stage = STAGE_WON,deal__user = self.params.get('user'))
                self.chart_data = []
                deal_deatil = {}
                deafult_count = 0
                """
                    for insurer in self.deals:
                            quotedproducts = QuotedProduct.objects.filter(product__insurer_id = insurer.pk)
                            print("quotedproducts",quotedproducts)
                            for qp in quotedproducts:
                                order = Order.objects.filter(selected_plan = qp)
                                print("order",order)
                                if order.exists():
                                    deal_count+=1 
                            self.chart_data.append((insurer.name, deal_count))
                """
        
                for i in self.deals:
                    insurer = i.selected_plan.plan.insurer
                    deal_deatil[insurer.id] = deafult_count+1

                # for i in deal_deatil:
                #     self.chart_data.append((Insurer.objects.get(id=i).name, deal_deatil[i]))

            if self.params.get('insurer') and self.params.get('filtertype') == 'date':
                self.deals = self.deals.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')],selected_plan__plan__insurer=self.params.get('insurer'))
                
                
            
            elif  (self.params.get('filtertype') == 'date'):

                self.deals = self.deals.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')]).order_by('created_on')

                


            # elif  self.params.get('insurer'):
            #     self.deals = self.deals.filter(selected_plan__plan__insurer=self.params.get('insurer'))
            #     chart_data()
            
            # else:
            #     chart_data()



    
    
    # def get_active_deals(self):
    #     if self.params.get('filtertype') == 'date': 
    #             start_date = today - timedelta(weeks=52)
    #             self.deals = self.deals.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')]).order_by('created_on')

    #     return Deal.objects.filter(status='active')

    # def get_lost_deals(self):
    #     lost_deal = self.request.GET.get("STAGE_ClosedLOST")

    #     try:
    #         lost_deal = Deal.objects.get(pk=lost_deal, DEAL_STAGES='Closed Lost')
    #     except Deal.DoesNotExist:
    #         lost_deal = None
    #     return lost_deal

class DealsFilter():
    def __init__(self, queryset, params):
        self.params = params
        self.deals=queryset
        chart_data = []
        date_holder =[]
        today_date = date.today()
        if self.params.get('filtertype') == "date":
            grouping_function = lambda deal: deal.created_on.date()
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
            
            grouping_function = lambda deal: deal.created_on.month
            
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


class HealthDealsCreatedCountView(BaseChartDataView):
    def get(self, request):
        self.get_chart_data(querytype='healthdeals')
        deals_filter = DealsFilter(self.deals, self.params)
        return JsonResponse(deals_filter.get_result(), safe=False)


class HealthLostDealsView(BaseChartDataView):
    def get(self, request):
        self.get_chart_data(querytype='lostdeals')
        deals_filter = DealsFilter(self.deals, self.params)
        return JsonResponse(deals_filter.get_result(), safe=False)

class DealsWonView(BaseChartDataView):
    def get(self, request):
        self.get_chart_data(querytype='won_deals')
        deals_filter = DealsFilter(self.deals, self.params)
        return JsonResponse(deals_filter.get_result(), safe=False)

class HealthSalesConversionRateView(BaseChartDataView):
    def get(self, request):
        user = self.get_user_filter()
        month_ranges = get_month_pairs_for_last_12_months()

        if self.params.get('insurer') and self.params.get('filtertype') == 'date':
            insurer_id =  self.params.get('insurer')
            deal_qs = Deal.objects.filter()
            if self.params.get('user'):
                user_id = self.params.get('user')
                deals_won = Order.objects.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')],deal__user = user_id,selected_plan__plan__insurer = insurer_id)
            else:
                deals_won = Order.objects.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')],selected_plan__plan__insurer = insurer_id)

        elif self.params.get('insurer'):
            # import pdb
            # pdb.set_trace()
            deal_qs = Deal.objects.filter()
            insurer_id =  self.params.get('insurer')
            if self.params.get('user'):
                user_id = self.params.get('user')
                deals_won = Order.objects.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')],deal__user = user_id,selected_plan__plan__insurer = insurer_id)
            else:
                deals_won = Order.objects.filter(selected_plan__plan__insurer = insurer_id)

        
        elif self.params.get('filtertype') == 'date': 
            # import pdb
            # pdb.set_trace()
            if self.params.get('user'):
                user_id = self.params.get('user')
                deal_qs =  Deal.objects.filter(user = user_id,created_on__range=[self.params.get('start_date'), self.params.get('end_date')]).order_by('created_on')
            else:
                deal_qs =  Deal.objects.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')]).order_by('created_on')
        
        
        elif self.params.get('user'):
            user_id = self.params.get('user')
            deal_qs = Deal.objects.filter(user = user_id)
        else:
            deal_qs = Deal.objects.filter()

        # if user:
        #     deal_qs = deal_qs.filter(assigned_to=user)


        chart_data = list()
        for sd, ed in month_ranges:
            month_label = sd.strftime('%b, %y')

            deals = deal_qs.filter(created_on__range=(sd, ed))
            
            if self.params.get('insurer'): # If insurer filtering out won deal from "Order" model.
                deals_won_qs = deals_won.filter(created_on__range=(sd, ed))
            else:
                deals_won_qs = deals.filter(Q(stage = 'closed') )

            
            # for closedD in deals_won_qs:
            #     pass

            number_of_deals_won = deals_won_qs.count()
            number_of_deals = deals.count()

            if number_of_deals > 0:
                conversion_rate = number_of_deals_won / float(number_of_deals)
            else:
                conversion_rate = 0.0

            chart_data.append((
                month_label, '{:0.2f}'.format(conversion_rate * 100.0)
            ))
        return JsonResponse(chart_data, safe=False)

class HealthOrdersTotalPremiumView(BaseChartDataView):

    def get(self, request):
        base_qs = Order.objects.filter()
        if  self.params.get('insurer') and self.params.get('filtertype') == 'date':
            ins = Insurer.objects.filter(id=self.params.get('insurer'))
            base_qs = QuotedPlan.objects.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')],product = Plan.objects.filter(insurer=ins.first().id).first().id).order_by('created_on')

        elif self.params.get('filtertype') == 'date': 
                base_qs = base_qs.filter(created_on__range=[self.params.get('start_date'), self.params.get('end_date')]).order_by('created_on')

        elif self.params.get('insurer'):
            ins = Insurer.objects.filter(id=self.params.get('insurer'))
            base_qs = QuotedPlan.objects.filter(product = Plan.objects.filter(insurer=ins.first().id).first().id)

        user = self.get_user_filter()
        month_ranges = get_month_pairs_for_last_12_months()
       
        if user and not self.params.get('insurer'):
            try :
                base_qs = base_qs.filter(deal__assigned_to=user)
            except:
                pass

        chart_data = list()
        for sd, ed in month_ranges:
            month_label = sd.strftime('%b, %y')
            if self.params.get('insurer'):
                total_premium = (
                base_qs
                .filter(created_on__range=(sd, ed))
                .aggregate(total_premium=Sum('premium'))
                )['total_premium'] or 0.0
            else:
                total_premium = (
                    base_qs
                    .filter(created_on__range=(sd, ed))
                    .aggregate(total_premium=Sum('selected_plan__total_premium'))
                )['total_premium'] or 0.0
            chart_data.append((
                month_label,
                total_premium
            ))
        
        return JsonResponse(chart_data, safe=False)


class HealthDealByInsurer(BaseChartDataView):
     def get(self, request):
        self.get_chart_data(querytype='by_insurer')
        chart_data = []
        holder =[]
        month_ranges = get_month_pairs_for_last_12_months()
        # for sd, ed in month_ranges:
        #     month_label = sd.strftime('%b, %y')
        #     if self.params.get('insurer'):
        #         total_premium = (
        #         self.deal
        #         .filter(created_on__range=(sd, ed))
        #         .aggregate(total_premium=Sum('premium'))
        #         )['total_premium'] or 0.0
        #     else:
        #         total_premium = (
        #             self.deal
        #             .filter(created_on__range=(sd, ed))
        #             .aggregate(total_premium=Sum('selected_plan__total_premium'))
        #         )['total_premium'] or 0.0
        #     chart_data.append((
        #         month_label,
        #         total_premium
        #     ))

        grouping_function = lambda order: order.selected_plan.plan.insurer.name
        for x, y in groupby(self.deals, grouping_function):
                    chart_data.append((x,len(list(y))))
                    holder.append(x)
        for x in Insurer.objects.all():
                if x.name not in holder:
                    chart_data.append((x.name,0))
        #chart_data.sort(key= lambda x:x[0])
        final_result = chart_data
        
        return JsonResponse(chart_data, safe=False)

