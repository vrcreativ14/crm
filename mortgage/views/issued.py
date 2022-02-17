from datetime import datetime
from django.forms.fields import DateField
from django.http.response import Http404
from django.views.generic import FormView
from django.http import JsonResponse, request
from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import View
from mortgage.forms import NewIssuedForm, FilterIssuedForm
from mortgage.models import Bank, Deal, Order, Quote, IssuedDeal
from mortgage.constants import STATUS_ACTIVE, STATUS_DELETED, STAGE_ClosedWON
from customers.models import Customer
from core.forms import TaskForm, AttachmentForm
from felix.exporter import ExportService
import datetime
from mortgage.serializers import DealSerializer
 
class IssuedView(View):
    template_name = "mortgage/issued/mortgage_issued_list.html"
    permission_required = "auth.list_motor_deals"

    def get(self, *args, **kwargs):
        issued_lists = Deal.objects.filter(stage='won').order_by('-updated_on').all()
        bank_lists = Bank.objects.all()
        issued_form = NewIssuedForm()
        search_form = FilterIssuedForm()
        context = {
            "entity": "mortgage",
            "issued_lists": issued_lists,
            "issued_form": issued_form,
            "bank_lists": bank_lists,
            "search_form":search_form,
        }

        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        issued_data = self.request.POST
        # issued_form = NewIssuedForm(issued_data)
        # if issued_form.is_valid():
        customer_id = issued_data['customer']

        if customer_id == '':
            return JsonResponse({"errors": 'This customer was not registered.'})
        else:
            property_price = issued_data['property_price'].replace(',', '')
            bank_id = issued_data['bank']
            referrer_id = issued_data['referrer']
            status = issued_data['status']
            issue_date = issued_data['issue_date']
            issued_date = datetime.strptime(issue_date, '%d-%m-%Y')

            deal = Deal.objects.create(stage='won', property_price=int(property_price), status=status,
                                       referrer_id=referrer_id, created_date=issue_date, updated_on=issue_date)

            quote = Quote.objects.create(deals_id=deal.deal_id)

            return HttpResponseRedirect(reverse("mortgage:issued"))


class FilterIssuedDeals(View):

    def get(self, *args, **kwargs):
        created_on_before = self.request.GET.get('created_on_before')
        created_on_after = self.request.GET.get('created_on_after')
        sort_by = self.request.GET.get('sort_by')
        
        
        if created_on_before and created_on_after:
                created_on_before = datetime.datetime.strptime(created_on_before,"%d-%m-%Y").date()            
                created_on_after = datetime.datetime.strptime(created_on_after,"%d-%m-%Y").date()                
                if sort_by == 'desc':
                    issued_lists = Deal.objects.filter(stage='won', created_date__gte=created_on_after, created_date__lte=created_on_before).order_by('-created_date')
                else:
                    issued_lists = Deal.objects.filter(stage='won', created_date__gte=created_on_after, created_date__lte=created_on_before).order_by('created_date')
        elif created_on_before:
                created_on_before = datetime.datetime.strptime(created_on_before,"%d-%m-%Y").date()
                if sort_by == 'desc':
                    issued_lists = Deal.objects.filter(stage='won', created_date__lte=created_on_before).order_by('-created_date')
                else:
                    issued_lists = Deal.objects.filter(stage='won', created_date__lte=created_on_before).order_by('created_date')
        elif created_on_after:
                created_on_after = datetime.datetime.strptime(created_on_after,"%d-%m-%Y").date()
                if sort_by == 'desc':
                    issued_lists = Deal.objects.filter(stage='won', created_date__gte=created_on_after).order_by('-created_date')
                else:
                    issued_lists = Deal.objects.filter(stage='won', created_date__gte=created_on_after).order_by('created_date')

        else:
            if sort_by == 'desc':
                issued_lists = Deal.objects.filter(stage='won').order_by('-created_date').all()
            else:
                issued_lists = Deal.objects.filter(stage='won').order_by('created_date').all()
                
        deal_serializer = DealSerializer(issued_lists, many = True)
        return JsonResponse(deal_serializer.data, safe=False)

class issuedDeaitl(View):
    @staticmethod
    def get(request, *args, **kwargs):
        if kwargs.get("pk"):
            if Deal.objects.filter(pk=kwargs.get("pk")):
                deal = Deal.objects.get(pk=kwargs.get("pk"))
                attachment_form = AttachmentForm()
                request.session["selected_product_line"] = "mortgage"
                attachment_form.helper.form_action = reverse(
                    'mortgage:add-attachment',
                    kwargs=dict(pk=deal.pk, type="postapproval" if deal.stage == "preApproval" else "preapproval"))
                context = {
                    "deal": deal,
                    "entity": "mortgage",
                    "task_form": TaskForm(company=request.company),
                    "attachment_form": attachment_form,
                    "note_form_action": reverse('mortgage:notes', kwargs={"pk": deal.pk}),
                }
                if hasattr(deal, 'mortgage_quote_deals'):
                    quote_instance = deal.mortgage_quote_deals
                    context["quote_instance"] = quote_instance
                    context["quote"] = quote_instance
                template_name = "mortgage/issued/issued_details.djhtml"
                return render(request, template_name, context)
        return HttpResponseRedirect(reverse("mortgage:deals"))

    @staticmethod
    def serialize_attachments(attachments, location_label="", location_url=""):
        data = []
        for attachment in attachments:
            data.append({
                "id": attachment.id,
                "label": attachment.label,
                "url": attachment.get_file_url() if hasattr(attachment, "get_file_url") else '',
                "can_preview": attachment.can_preview_in_frontend(),
                "extension": attachment.get_file_extension().upper(),
                "added_by": attachment.added_by.get_full_name() if attachment.added_by else "",
                "created_on": attachment.created_on.strftime("%Y-%m-%d"),
                "location_label": location_label,
                "location_url": location_url,
                "update_url": reverse("core:update-attachment", kwargs={"pk": attachment.id}),
                "url_for_linking": attachment.get_url_for_linking_in_frontend(),
            })

        return data

    def post(self, request, *args, **kwargs):
        deal = Deal.objects.get(pk=kwargs.get("pk"))
        return JsonResponse(
            {
                "title": "Deal",
                "documents": self.serialize_attachments(deal.get_attachments()),
            }
        )

def GetIssuedDeals(created_on_before, created_on_after, sort_by):                                  
        if created_on_before and created_on_after:
                created_on_before = datetime.datetime.strptime(created_on_before,"%d-%m-%Y").date()            
                created_on_after = datetime.datetime.strptime(created_on_after,"%d-%m-%Y").date()                
                if sort_by == 'desc':
                    issued_lists = Deal.objects.filter(stage='won', created_date__gte=created_on_after, created_date__lte=created_on_before).order_by('-created_date')
                else:
                    issued_lists = Deal.objects.filter(stage='won', created_date__gte=created_on_after, created_date__lte=created_on_before).order_by('created_date')
        elif created_on_before:
                created_on_before = datetime.datetime.strptime(created_on_before,"%d-%m-%Y").date()
                if sort_by == 'desc':
                    issued_lists = Deal.objects.filter(stage='won', created_date__lte=created_on_before).order_by('-created_date')
                else:
                    issued_lists = Deal.objects.filter(stage='won', created_date__lte=created_on_before).order_by('created_date')
        elif created_on_after:
                created_on_after = datetime.datetime.strptime(created_on_after,"%d-%m-%Y").date()
                if sort_by == 'desc':
                    issued_lists = Deal.objects.filter(stage='won', created_date__gte=created_on_after).order_by('-created_date')
                else:
                    issued_lists = Deal.objects.filter(stage='won', created_date__gte=created_on_after).order_by('created_date')

        else:
            if sort_by == 'desc':
                issued_lists = Deal.objects.filter(stage='won').order_by('-created_date').all()
            else:
                issued_lists = Deal.objects.filter(stage='won').order_by('created_date').all()

        return issued_lists

class IssuedDealsExportView(View):
    #permission_required = 'auth.export_motor_deals'
    default_sort_by = ''
    def get_queryset():
        return 

    def get(self, request, *args, **kwargs):
        #qs = self.get_queryset()
        created_on_before = self.request.GET.get('created_on_before')
        created_on_after = self.request.GET.get('created_on_after')   
        sort_by = self.request.GET.get('sort_by')
        qs = GetIssuedDeals(created_on_before, created_on_after, sort_by)
        data = list()
        column_labels = [
            'Status', 'Bank', 'Bank Reference Number', 'Loan Amount', 'Property Price', 'Tenure (Months)', 'LTV (%)',
            'Customer', 'Created On', 'Updated On']

        # deal_ids = [r['objectID'] for r in qs]

        # deals = Deal.objects.filter(pk__in=deal_ids)
        counter = 1
        bank_name = ''
        bank_reference_number = ''
        loan_amount =''
        property_price =''
        tenure =''
        ltv =''
        customer_name =''
        created_on =''
        updated_on = ''
        for issued in qs:            
            status = issued.status
            order = Order.objects.filter(deal = issued)
            issued_deal = IssuedDeal.objects.filter(deal = issued)
            if issued_deal:
                ltv = issued_deal[0].l_tv if issued_deal[0].l_tv else ''
                loan_amount = issued_deal[0].loan_amount
                tenure = issued_deal[0].tenure
                property_price = issued_deal[0].property_price
            if order:
                bank_reference_number = issued.deal_bank.bank_reference_number
                bank_name = issued.deal_bank.bank.name
            if issued.customer:
                customer_name = issued.customer.name
            if issued.created_date:
                created_on = issued.created_date
            if issued.updated_on:
                updated_on = issued.updated_on

            data.append([
                status,
                bank_name,
                bank_reference_number,
                loan_amount,
                property_price,
                tenure,
                ltv,
                customer_name,
                created_on,
                updated_on,                                       
            ])
            counter += 1

        exporter = ExportService()

        return exporter.to_csv(column_labels, data, filename='issued-{}.csv'.format(datetime.datetime.today()))
