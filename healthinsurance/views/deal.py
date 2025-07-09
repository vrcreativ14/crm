
from genericpath import exists
import logging
from re import sub, template
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.views.generic import View, TemplateView
from django.shortcuts import redirect, render
from requests import Request
from healthinsurance.forms.deal import *
from healthinsurance.forms.quote import OrderForm
from healthinsurance.models.deal import *
from healthinsurance.models.policy import *
from healthinsurance.serializers import PlanSerializer
from healthinsurance_shared.models import Plan
import json
from django.utils.timezone import localtime
from rolepermissions.mixins import HasPermissionsMixin
from core.views import AddEditTaskView as CoreAddEditTaskView
from core.views import DeleteTaskView
from core.models import Task
from core.forms import TaskForm, AttachmentForm
from core.views import AddNoteView, DeleteNoteView
from core.mixins import AjaxListViewMixin, CompanyAttributesMixin
from core.amplitude import Amplitude
from django.http import Http404
from django.views.generic import TemplateView, View, DetailView
from healthinsurance_shared.models import Insurer
from django.core import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from collections import OrderedDict
from decimal import Decimal
from felix.settings import DOMAIN
from healthinsurance.utils import *
from mortgage.views import email
from datetime import datetime
from django.utils.html import escape, strip_tags
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404
from django.db.models import Q
from core.views import  DeleteAttachmentView
from rest_framework import status
from core.timeline import Timeline
from core.pdf import PDF
from accounts.roles import Producer
from felix.exporter import ExportService
from healthinsurance.views.email import StageEmailNotification
import io
import zipfile
import math
from healthinsurance.tasks import email_notification
from core.utils import log_user_activity

api_logger = logging.getLogger("api.amplitude")


def get_email_address_for_deal(deal):
    if deal.deal_type != DEAL_TYPE_RENEWAL:
        if deal.primary_member and deal.primary_member.visa == EMIRATE_DUBAI:
            return 'nbind.medical@nexusadvice.com'
        else:
            return 'ind.medical@nexusadvice.com'
    elif (deal.deal_type == DEAL_TYPE_RENEWAL and 
          deal.primary_member and 
          deal.primary_member.visa == EMIRATE_DUBAI):
        return 'rwind.medical@nexusadvice.com'
    else:
        return 'ind.medical@nexusadvice.com'


def GetCountries():
        countries = []
        for country in COUNTRIES:
            countries.append({
                'value': country[0],
                'text': country[1]})

        return countries

def CreateBasicQuote(request, deal):
        quote = Quote.objects.create(deal=deal, company=request.company,                                 
                        status=Quote.STATUS_PUBLISHED)            
        deal.status = STATUS_CLIENT
        deal.stage = STAGE_BASIC
        sub_stage = deal.current_sub_stage
        plan_applicable_visa = get_deal_visa(deal.primary_member.visa)
        plans = Plan.objects.filter(coverage_type = 'basic')
        if not sub_stage:
            substage = SubStage.objects.create(deal = deal, stage = STAGE_BASIC, sub_stage = BASIC_QUOTED)
        else:
            substage.stage = STAGE_BASIC
            substage.sub_stage = BASIC_QUOTED
        '''basic plan premium is being fetched from plan model as a string field
           so it is not saved here in QuotedPlan'''
        for rqp in plans:
            if rqp and rqp.applicable_visa.all().filter(name = plan_applicable_visa).exists():
                new_qp = QuotedPlan(quote=quote, plan_id=rqp.id,
                area_of_cover = rqp.area_of_cover.all().first(),
                consultation_copay = rqp.consultation_copay.all().first(),
                pharmacy_copay = rqp.pharmacy_copay.all().first(),
                diagnostics_copay = rqp.diagnostics_copay.all().first(),
                network = rqp.network.all().first(),
                payment_frequency = rqp.payment_frequency.all().first(),
                annual_limit = rqp.annual_limit.all().first(), 
                physiotherapy = rqp.physiotherapy.all().first(),
                alternative_medicine = rqp.alternative_medicine.all().first(), 
                maternity_benefits = rqp.maternity_benefits.all().first(),
                maternity_waiting_period = rqp.maternity_waiting_period.all().first(), 
                dental_benefits = rqp.dental_benefits.all().first(),
                wellness_benefits = rqp.wellness_benefits.all().first(), 
                optical_benefits = rqp.optical_benefits.all().first(), 
                pre_existing_cover = rqp.pre_existing_cover.all().first(),
                )
                new_qp.save(user=request.user)
                
        quote.save(user = request.user)
        return quote


class DealEditBaseView(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = None

    def get_object(self, **kwargs):
        try:
            filters = {
                "pk": self.kwargs["pk"],
            }
            deal = Deal.objects.select_related().get(**filters)
            if self.request.user.userprofile.has_producer_role() and (
                deal.referrer != self.request.user
            ):
                raise Http404()

            return deal
        except Deal.DoesNotExist:
            raise Http404()

    def serialize_insurers(self):
        data = dict()

        for insurer in Insurer.objects.all().order_by("name"):
            data[insurer.insurer_id] = {
                "insurer_id": insurer.insurer_id,
                "name": insurer.name,
                "logo": insurer.logo,                
            }

        return data

    def get_related_attachments(self):
        deal = self.get_object()
        attachments = self.serialize_attachments(
            deal.customer.get_attachments(),
            deal.customer.name,
            reverse("customers:edit", kwargs=dict(pk=deal.customer.pk)),
        )

        deals = Deal.objects.filter(customer=deal.customer).exclude(id=deal.pk)

        for deal in deals:
            attachments = attachments + self.serialize_attachments(
                deal.get_attachments(),
                reverse("health-insurance:edit-deal", kwargs=dict(pk=deal.pk)),
            )

        return attachments

    def serialize_attachments(self, attachments, location_label="", location_url=""):
        return [
            {
                "id": attachment.id,
                "pk": attachment.id,
                "label": attachment.label,
                "url": attachment.get_file_url(),
                "can_preview": attachment.can_preview_in_frontend(),
                "extension": attachment.get_file_extension().upper(),
                "added_by": attachment.added_by.get_full_name() if attachment.added_by else "",
                "created_on": attachment.created_on.strftime("%Y-%m-%d"),
                "location_label": location_label,
                "location_url": location_url,
                "update_url": reverse(
                    "core:update-attachment", kwargs={"pk": attachment.id}
                ),
                "url_for_linking": attachment.get_url_for_linking_in_frontend(),
            }
            for attachment in attachments
        ]



class DealsList(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "healthinsurance/deals/deals_list.djhtml"
    permission_required = 'auth.list_health_deals'

    def get_search_and_ordering_form(self):
        return DealSearchAndOrderingForm(data=self.request.GET, company=self.request.company)

    def get_context_data(self, **kwargs):
        ctx = super(DealsList, self).get_context_data(**kwargs)
        self.request.session['selected_product_line'] = 'health-insurance'
        deals = Deal.objects.all().exclude(status = STATUS_DELETED).order_by('-created_on')
        if self.request.user.userprofile.has_producer_role():
            deals = deals.filter(Q(user = self.request.user) | Q(referrer = self.request.user))
        
        ctx['deal_form'] = DealForm()
        ctx['deals'] = deals
        ctx['entity'] = 'health'
        ctx['search_form'] = self.get_search_and_ordering_form()
        ctx["users"] = User.objects.all()
        try:
            current_datetime = datetime.now()
        except:
            current_datetime = datetime.datetime.now()
        ctx['current_datetime'] = current_datetime
        ctx['countries'] = COUNTRIES
        return ctx

class PolicyList(LoginRequiredMixin, TemplateView, CompanyAttributesMixin):
    template_name = "healthinsurance/policies_list.djhtml"
    def get_context_data(self, **kwargs):
        ctx = super(PolicyList, self).get_context_data(**kwargs)
        self.request.session['selected_product_line'] = 'health-insurance'
        policies = HealthPolicy.objects.all().order_by('-start_date')        
        ctx['policies'] = policies
        current_datetime = datetime.now()
        ctx['current_datetime'] = current_datetime
        ctx['entity'] = 'health'
        ctx['referrers'] = self.get_company_agents_list()
        print('sd')
        return ctx

class NewHealthDeal(View):
    def post(self, request):
        user = request.user
        if not request.user.is_authenticated:
            referrer = request.POST.get('referrer', None)
            if not referrer:
                return redirect('accounts/login/')
            else:
                user = User.objects.filter(pk = referrer)
                user = user[0] if user.exists() else None

        additional_members = request.POST.get('additional_members')
        if additional_members:
            additional_members = json.loads(additional_members)
        updated_request = request.POST.copy()
        primary_member_dob = request.POST.get('dob', None)
        salary_band = request.POST.get('salary_band', None)
        visa = request.POST.get('visa', None)
        visa = EmirateText(visa)
        updated_request['visa'] = visa
        if not salary_band:
            updated_request['salary_band'] = ''
        updated_request['dob'] = datetime.strptime(primary_member_dob, '%d/%m/%Y') if primary_member_dob else None
        primary_member_form = PrimaryMemberForm(updated_request)
        if primary_member_form.is_valid():
            primary_member = primary_member_form.save()
            updated_request['primary_member'] = primary_member
            for member in additional_members:
                name = member['name']
                relation = member['relation']
                dob = member['dob']
                order = member['order']
                nationality = member['nationality']
                country_of_stay = member['country_of_stay']
                member_dob = datetime.strptime(dob, '%d/%m/%Y')
                member = AdditionalMember.objects.create(name = name, relation = relation, dob=member_dob, nationality = nationality, country_of_stay = country_of_stay, order = order)
                member.save()
                primary_member.additional_members.add(member)
                primary_member.save()
            deal = Deal(primary_member = primary_member, user = user)
            post = request.POST.copy()
            post['primary_member'] = primary_member
            request.POST = post
            customer = request.POST.get('customer')
            if customer:
                customer = Customer.objects.filter(pk = customer)
                if customer.exists():
                    customer = customer[0]
            else:
                updated_request['company'] = self.request.company
                customer_form = CustomerForm(updated_request)
                if customer_form.is_valid():
                    customer = customer_form.save()
                else:
                    return JsonResponse({"success": False, "errors": customer_form.errors})
            updated_request['customer'] = customer
            
            start_date = request.POST.get('start_date', None)
            start_date = start_date.replace('"','')
            level_of_cover = request.POST.get('level_of_cover', None)
            
            additional_benefits = request.POST.get('additional_benefits', None)
            updated_request.pop('additional_benefits')
            additional_benefits = additional_benefits.split(',')
            indicative_budget = request.POST.get('indicative_budget', None)
            indicative_budget = IndicativeBudgetText(indicative_budget)
            updated_request['indicative_budget'] = indicative_budget
            if not level_of_cover:
                updated_request['level_of_cover'] = ''
            if not start_date:
                updated_request['start_date'] = datetime.now().date()
            else:
                try:
                    deal_start_date = datetime.strptime(start_date, "%d/%m/%Y")
                    updated_request['start_date'] = deal_start_date
                except:
                    updated_request['start_date'] = datetime.now().date()
            
            deal_form = DealSaveForm(updated_request,instance=deal)
            if deal_form.is_valid():
                deal_form.save()
                for benefit in additional_benefits:
                    additional_benefit = AdditionalBenefit.objects.filter(benefit__iexact = benefit.replace('_',' '))
                    if additional_benefit.exists():
                        deal.additional_benefits.add(additional_benefit[0])

                if hasattr(self.request.user,'userprofile') and self.request.user.userprofile.has_producer_role():
                    deal.referrer = self.request.user

                deal.save()
                
                response = {
                        "success": True,
                        "deal": deal.pk if deal else "",
                        'redirect_url': reverse('health-insurance:deal-details', kwargs=dict(pk=deal.pk)),
                    }
                
                if not deal.primary_member.visa == EMIRATE_ABU_DHABI and request.POST.get('referrer') and deal.indicative_budget == 'Below 1k':
                    quote = CreateBasicQuote(request, deal)
                    deal.status = STATUS_CLIENT
                    deal.stage = STAGE_BASIC
                    deal.save()
                    if quote:
                        response['quote_reference_number'] = quote.reference_number
                if request.POST.get('referrer') and deal.primary_member.email:
                    cc_email = []
                    bcc_email = []
                    if deal.referrer and deal.referrer.email:
                        cc_email.append(deal.referrer.email)
                    #bcc_email.append('ind.medical@nexusadvice.com')
                    if deal.primary_member and deal.primary_member.visa == EMIRATE_ABU_DHABI:
                        notification_email = 'auhpls.hotline@nexusadvice.com'
                        bcc_email.append(notification_email)
                    else:
                        notification_email = get_email_address_for_deal(deal)
                        bcc_email.append(notification_email)

                    email_notification(deal, 'new deal internal notification', get_email_address_for_deal(deal))
                    if deal.stage == STAGE_BASIC:
                        email_notification(deal, 'basic new deal', deal.primary_member.email, cc_emails = cc_email, bcc_emails = bcc_email)
                    else:
                        email_notification(deal, 'new deal', deal.primary_member.email, cc_emails = cc_email, bcc_emails = bcc_email)
                    
                log_user_activity(user, self.request.path, 'C', deal)
                return JsonResponse(response)
            else:
                return JsonResponse({"success": False, "errors": deal_form.errors})
        else:
            return JsonResponse({"success": False, "errors": primary_member_form.errors})


class EditAdditionalMembers(LoginRequiredMixin, View):
    def post(self, request,pk):
        deal = Deal.objects.filter(pk = pk)
        if deal.exists():
            deal = deal[0]
        primary_member = deal.primary_member
        added_members = []
        for additional_member in deal.primary_member.additional_members.all():
            added_members.append(additional_member.pk)

        additional_members = request.POST.get('additional_members')
        if additional_members:
            additional_members = json.loads(additional_members)            
            for member in additional_members:
                    id = member['id']
                    name = member['name']
                    relation = member['relation']
                    dob = member['dob']
                    order = member['order']
                    nationality = member['nationality']
                    country_of_stay = member['country_of_stay']
                    member_dob = datetime.strptime(dob, '%d/%m/%Y')
                    additional_member = AdditionalMember.objects.filter(pk = id)
                    if additional_member.exists():
                        additional_member = additional_member[0]
                        additional_member.name = name
                        additional_member.dob = member_dob
                        additional_member.nationality = nationality
                        additional_member.country_of_stay = country_of_stay
                        additional_member.save()
                        added_members.remove(int(id))
                    else:
                        additional_member = AdditionalMember.objects.create(name = name, relation = relation, dob=member_dob, nationality = nationality, country_of_stay = country_of_stay, order = order)
                        additional_member.save()
                    primary_member.additional_members.add(additional_member)
                    primary_member.save()
        for member in added_members:
            previous_member = AdditionalMember.objects.filter(pk = int(member))
            if previous_member.exists():
                previous_member.delete()
        return redirect('/health-insurance/deals/{0}'.format(deal.pk))


class EditDeal(LoginRequiredMixin, View):
    def post(self, request,pk):
        deal = Deal.objects.filter(pk = pk)
        if deal.exists():
            deal = deal[0]
        start_date = request.POST.get('start_date', None)
        primary_member_dob = request.POST.get('dob', None)
        if start_date:
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
        if primary_member_dob:
            primary_member_dob = datetime.strptime(primary_member_dob, "%d/%m/%Y").strftime("%Y-%m-%d")
        name = request.POST.get('name')
        primary_email = request.POST.get('email')        
        primary_phone = request.POST.get('phone')
        post = request.POST.copy()
        post['start_date'] = start_date
        post['dob'] = primary_member_dob
        additional_members = request.POST.get('additional_members')
        if additional_members:
            additional_members = json.loads(additional_members)
        request.POST = post
        updated_request = request.POST.copy()
        #customer = Customer.objects.filter(email = primary_email, phone = primary_phone)
        customer = deal.customer
        updated_request['company'] = self.request.company
        if customer:
                customer_form = CustomerForm(updated_request, instance = customer)
        else:
                customer_form = CustomerForm(updated_request)
        if customer_form.is_valid():
            customer = customer_form.save()
        else:
            return JsonResponse({"success": False, "errors": customer_form.errors})
        
        updated_request['customer'] = customer
        updated_request['start_date'] = start_date
        additional_benefits = request.POST.get('additional_benefits', None)
        updated_request.pop('additional_benefits')
        indicative_budget = request.POST.get('indicative_budget', None)
        indicative_budget = IndicativeBudgetText(indicative_budget)
        updated_request['indicative_budget'] = indicative_budget

        primary_member = PrimaryMember.objects.get(pk = deal.primary_member.pk)
        primary_member_form = PrimaryMemberForm(request.POST, instance=primary_member)
        if primary_member_form.is_valid():
            primary_member_form.save()
            for member in additional_members:
                    id = member['id']
                    name = member['name']
                    relation = member['relation']
                    dob = member['dob']
                    order = member['order']
                    nationality = member['nationality']
                    country_of_stay = member['country_of_stay']
                    member_dob = datetime.strptime(dob, "%m/%d/%Y").strftime("%Y-%m-%d")
                    #member = AdditionalMember.objects.create(name = name, relation = relation, dob=member_dob, nationality = nationality, country_of_stay = country_of_stay, order = order)
                    additional_member = AdditionalMember.objects.filter(pk = id)
                    if additional_member.exists():
                        additional_member = additional_member[0]
                        additional_member.name = name
                        additional_member.dob = member_dob
                        additional_member.nationality = nationality
                        additional_member.country_of_stay = country_of_stay
                        additional_member.save()
                    else:
                        additional_member = AdditionalMember.objects.create(name = name, relation = relation, dob=member_dob, nationality = nationality, country_of_stay = country_of_stay, order = order)
                        additional_member.save()
                    primary_member.additional_members.add(additional_member)
                    primary_member.save()
        
        updated_request['primary_member'] = primary_member.pk
        updated_request['referrer'] = deal.referrer
        updated_request['user'] = deal.user
        updated_request['renewal_for_policy'] = deal.renewal_for_policy
        deal_form = DealSaveForm(updated_request,instance=deal)
        is_basic = True if deal.stage == STAGE_BASIC else False
        if deal_form.is_valid():
            deal_form.save()
            if additional_benefits:
                additional_benefits = additional_benefits.split(',')
                for benefit in additional_benefits:
                        additional_benefit = AdditionalBenefit.objects.filter(benefit__iexact = benefit.replace('_',' '))
                        if additional_benefit.exists():
                            deal.additional_benefits.add(additional_benefit[0])
                            deal.save()
            
            if is_basic and request.POST.get('referrer') and deal.stage == STAGE_NEW:
                existing_basic_quote = deal.get_quote()
                if existing_basic_quote:
                    existing_basic_quote.delete()
            
                return JsonResponse({
                    "success": True,
                    'redirect_url': reverse('health-insurance:deal-details', kwargs=dict(pk=deal.pk)),
                    })
        else:
                return JsonResponse({"success": False, "errors": deal_form.errors})
        
        


        return redirect('/health-insurance/deals/{0}'.format(deal.pk))

class DeleteDeals(View):
    def post(self, request, *args, **kwargs):
        deals = Deal.objects.filter(pk__in=request.POST.getlist(('deals[]')))
        for deal in deals:
            deal.status = STATUS_DELETED
            deal.save()

        return JsonResponse({"success":True, "message":"deleted" })

class DeleteDealView(View):
    
    def get(self, request, *args, **kwargs):
        deal = Deal.objects.get(pk=kwargs.get('pk'))
        deal.status = STATUS_DELETED
        deal.save()
        return JsonResponse({
            "success":True
        })

class DealMarkasLostView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.update_health_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        deal = self.get_object()

        if deal.stage not in [STAGE_LOST, STAGE_WON]:
            deal.stage = STAGE_LOST
            deal.save()

            return JsonResponse({'success': True})

        return JsonResponse({'success': False})

class DealReopenView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.update_health_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        deal = self.get_object()

        if deal.stage in [STAGE_LOST, STAGE_WON]:
            substage = SubStage.objects.filter(deal = deal)
            deal.stage = STAGE_NEW
            for deal_stage in substage:
                stage = deal_stage.stage
                if stage == STAGE_WON:
                    deal.stage = STAGE_WON
                elif stage == STAGE_HOUSE_KEEPING:
                    deal.stage = STAGE_HOUSE_KEEPING
                elif stage == STAGE_POLICY_ISSUANCE:
                    deal.stage = STAGE_HOUSE_KEEPING
                elif stage == STAGE_PAYMENT:
                    deal.stage = STAGE_POLICY_ISSUANCE
                elif stage == STAGE_FINAL_QUOTE:
                    deal.stage = STAGE_PAYMENT
                elif stage == STAGE_DOCUMENTS:
                    deal.stage = STAGE_FINAL_QUOTE
                elif stage == STAGE_QUOTE:
                    deal.stage = STAGE_DOCUMENTS
                elif stage == STAGE_NEW:
                    if Quote.objects.filter(deal = deal).exists():
                        deal.stage = STAGE_QUOTE
                    else:
                        deal.stage = STAGE_NEW
            
            deal.save()
            return JsonResponse({'success': True})

        return JsonResponse({'success': False})


class DealDetails(DealEditBaseView, View):
    permission_required = 'auth.update_health_deals'
    def get(self, request,pk):
        deal = Deal.objects.filter(pk = pk)
        insurers = Insurer.objects.all()
        if deal.exists():
            deal = deal[0]
        other_members = ['Spouse','Son', 'Daughter', 'Father', 'Mother']
        added_members = []
        additional_members = []
        counter = {'Son':0,'Spouse':0,'Daughter':0,'Father':0,'Mother':0}
        son, daughter, mother, father, spouse = 0,0,0,0,0
        absolute_quote_url = None
        quote_link = None
        for member in deal.primary_member.additional_members.all():
            added_members.append(member.relation)
            if 'spouse' in member.relation.lower():
                if 'Spouse' in other_members:
                    other_members.remove('Spouse')
                spouse += 1
                counter['Spouse'] = spouse
                
            elif 'son' in member.relation.lower():
                if 'Son' in other_members:
                    other_members.remove('Son')
                
                son += 1
                counter['Son'] = son

            elif 'daughter' in member.relation.lower():
                if 'Daughter' in other_members:
                    other_members.remove('Daughter')
                
                daughter+=1
                counter['Daughter'] = daughter

            elif 'father' in member.relation.lower():
                if 'Father' in other_members:
                    other_members.remove('Father')
                
                father += 1
                counter['Father'] = father

            elif 'mother' in member.relation.lower():
                if 'Mother' in other_members:
                    other_members.remove('Mother')
                
                mother += 1
                counter['Mother'] = mother

            member.nationality = GetCountryByName(member.nationality)
            member.country_of_stay = GetCountryByName(member.country_of_stay)
            additional_members.append(member)
            
        plans = Plan.objects.all()
        quote = Quote.objects.filter(deal = deal)
        if quote.exists():
            quote = quote[0]
            reference_number = quote.reference_number
            absolute_quote_url = f"{DOMAIN}/health-insurance-quote/{reference_number}/{deal.pk}/"
            quote_link = f"https://{DOMAIN}/health-insurance-quote/{reference_number}/{deal.pk}/"
        else:
            quote = None
        
        stage = self.request.GET.get("stage") or deal.stage
        stage_number = deal_stages_to_number(stage)
        sub_stage = deal.current_sub_stage
        sub_stage = sub_stage.sub_stage if sub_stage else None
        sub_stage_number = sub_stages_to_number(stage = stage, sub_stage = sub_stage)
        deal_files = DealFiles.objects.filter(deal = deal)  
        member_documents = MemberDocuments.objects.filter(deal = deal)  
        saved_files_types = []
        for file in deal_files:
            saved_files_types.append(file.type)
        
        deal.primary_member.country_of_stay = GetCountryByName(deal.primary_member.country_of_stay)
        deal.primary_member.nationality = GetCountryByName(deal.primary_member.nationality)
        other_benefits = ''
        count = 0
        additional_benefits = []
        for obj in deal.additional_benefits.all():
            additional_benefits.append(obj.benefit)
        if deal.other_benefits:
            for val in deal.other_benefits:
                count += 1
                other_benefits += val
                if count < len(deal.other_benefits):
                    other_benefits += ', '

        order = deal.get_order()
        policy = None
        policy_documents = None
        policy = HealthPolicy.objects.filter(deal = deal)
        if policy.exists():
            policy = policy[0]
            policy_documents = PolicyFiles.objects.filter(policy = policy)

        profile = UserProfile.objects.filter(user = request.user)
        is_producer = profile[0].has_producer_role() if profile.exists() else False
        self.request.session['selected_product_line'] = 'health-insurance'
        
        context = {
            'deal':deal,
            'deal_additional_benefits':additional_benefits,
            'deal_other_benefits':other_benefits,
            'insurers':insurers,
            "task_form": TaskForm(company=request.company),
            "entity": "health",
            "added_members":added_members,
            "other_members":other_members,
            "note_form_action": reverse('health-insurance:deals-notes', kwargs={"pk": deal.pk}),
            "counter":counter,
            "plans":plans,
            "quote":quote,
            "absolute_quote_url":absolute_quote_url,
            "quote_link":quote_link,
            "stage_number":stage_number,
            "sub_stage_number":sub_stage_number,
            "deal_files":deal_files,
            "member_documents":member_documents,
            "policy_documents":policy_documents,
            "saved_files_types": saved_files_types,
            "countries" : COUNTRIES,
            "additional_members" : additional_members,
            "order" : order,
            "policy": policy,
            "is_producer": is_producer,
            "order_pdf_link": order.get_pdf_url() if order else ''
        }
        
        return render(request,'healthinsurance/deals/deal_details.djhtml',context)

class DealMoreDetails(LoginRequiredMixin, View):
    def get(self, request,pk):
        deal = Deal.objects.filter(pk = pk)
        deal = deal[0] if deal.exists() else None
        deal.primary_member.country_of_stay = GetCountryByName(deal.primary_member.country_of_stay)
        deal.primary_member.nationality = GetCountryByName(deal.primary_member.nationality)
        additional_members = []
        for member in deal.primary_member.additional_members.all():
            member.nationality = GetCountryByName(member.nationality)
            member.country_of_stay = GetCountryByName(member.country_of_stay)
            additional_members.append(member)
        
        context = {'deal':deal, 'details':True,'entity':'health','additional_members':additional_members}        
        return render(request,'healthinsurance/deals/member_details.djhtml',context)

class AddEditTaskView(CoreAddEditTaskView):
    permission_required = 'auth.create_health_tasks'
    model = Task
    attached_model = Deal

class DealsNotes(AddNoteView):
    permission_required = ('auth.update_mortgage_deals',)
    model = Deal

    def get_success_url(self):
        return reverse('health-insurance:deals')

def delete_note(request, *args, **kwargs):
    from core.models import Note
    Note.objects.get(pk=kwargs.get("pk")).delete()
    return JsonResponse({"success":True})


def get_allowed_insurers(self, **kwargs):
        insurers = dict()
        visa = kwargs.get('visa')
        plan_applicable_visa = get_deal_visa(visa)
        
        for plan in Plan.objects.all().order_by('insurer__name'):
            if plan.insurer.is_active and plan.applicable_visa.all().filter(name = plan_applicable_visa).exists():
                insurer_id = plan.insurer_id
                if insurer_id not in insurers:
                    insurers[insurer_id] = {
                        'pk': insurer_id,
                        'name': plan.insurer.name,
                        'logo': plan.insurer.logo.url if plan.insurer.logo else '', 
                        'plans':[]
                    }
            # if plan.is_active:
            #     insurer_id = plan.insurer_id
            #     insurers[insurer_id]['plans'].append({
            #         "pk": plan.pk,
            #         "name": plan.name,
            #     })

        return insurers


class HealthDealStagesView(DetailView, CompanyAttributesMixin):
    template_name = "healthinsurance/deals/components/deal_overview.djhtml"
    permission_required = "auth.list_health_deals"
    model = Deal

    def get_context_data(self, **kwargs):
        deal = self.object
        ctx = super().get_context_data(**kwargs)
        closed_stages = ["lost","closed"]
        ctx["deal"] = deal
        quote = Quote.objects.filter(deal = deal)
        quote = quote[0] if quote.exists() else None
        stage = self.request.GET.get("stage") or deal.stage
        temp_stage = self.request.GET.get("stage")
        _quoted_products_data = {'products': [], 'quote': {'status': True, 'email': False, 'delete': False}}
        
        sub_stage = deal.current_sub_stage
        sub_stage = sub_stage.sub_stage if sub_stage else None
        quoted_products = QuotedPlan.objects.filter(quote = quote) if quote else None
        ctx['is_policy_link_active'] = True
        if temp_stage and 'edit-quote' in temp_stage:
            stage = 'edit-quote'
            self.template_name = 'healthinsurance/deals/components/deal_quote_form.djhtml'
            ctx['quoted_plans'] = quote.get_editable_quoted_plans()
            ctx['allowed_insurers'] = get_allowed_insurers(self, visa = deal.primary_member.visa)
            return ctx
        elif temp_stage and 'edit-plan' in temp_stage:
            plans = []
            self.template_name = 'healthinsurance/deals/components/quote_plan_form.djhtml'
            qp_id = self.request.GET.get("qp_id")
            qp = QuotedPlan.objects.filter(pk = qp_id)
            qp = qp.exclude(status = QuotedPlan.STATUS_DELETED)
            qp = qp[0] if qp.exists() else None
            if qp:
                insurer = qp.plan.insurer
                plans = Plan.objects.filter(insurer = insurer)

            ctx['quoted_plans'] = plans
            ctx['selected_plan'] = qp
            ctx['qp_id'] = qp_id
            return ctx
        

        if stage == STAGE_NEW:
            self.template_name = 'healthinsurance/deals/components/deal_overview.djhtml'
            ctx['allowed_insurers'] = get_allowed_insurers(self, visa = deal.primary_member.visa)

        elif stage == STAGE_QUOTE:
            self.template_name = 'healthinsurance/deals/components/deal_overview.djhtml'
            ctx['allowed_insurers'] = get_allowed_insurers(self, visa = deal.primary_member.visa)
            ctx['quoted_plans'] = quote.get_editable_quoted_plans()
            plan_details = GetQuotedPlanDetails(quote, quote_form = True)
            ctx['quoted_plan_details'] = plan_details

        elif stage == STAGE_BASIC:
            self.template_name = 'healthinsurance/deals/components/basic_plan_stage.djhtml'
            ctx['quoted_plans'] = quote.get_editable_quoted_plans()
            ctx['allowed_insurers'] = get_allowed_insurers(self, visa = deal.primary_member.visa)
            plan_details = GetQuotedPlanDetails(quote, quote_form = True)
            ctx['quoted_plan_details'] = plan_details
            if sub_stage == BASIC_SELECTED:
                ctx['order'] = deal.get_order()
            
        elif stage == STAGE_DOCUMENTS:
            self.template_name = 'healthinsurance/deals/components/document_stage.djhtml' 
            order = Order.objects.filter(deal=deal)
            ctx['order'] = order[0] if order.exists() else None
            if sub_stage == None:
                sub_stage = DOCUMENTS_RECEIVED
            if sub_stage == 'world check':
                ctx.update({'substage_obj': deal.current_sub_stage})    #world_check substage compliance details

        elif stage == STAGE_FINAL_QUOTE:
            self.template_name = 'healthinsurance/deals/components/final_quote_stage.djhtml'
            # order = deal.get_order()
            # if order and order.selected_plan.is_renewal_plan:
            #     ctx['plan_renewal_document'] = order.selected_plan.plan_renewal_document
            #     ctx['plan_renewal_document_name'] = order.selected_plan.plan_renewal_document.name.split('/')[-1]
        
        elif stage == STAGE_PAYMENT:
            #ctx["extended_expiry_date"]
            self.template_name = 'healthinsurance/deals/components/payment_stage.djhtml'
            order = deal.get_order()
            if order:
                insurer_details = InsurerDetails.objects.filter(insurer = order.selected_plan.plan.insurer)
                bank_name = insurer_details[0].bank_name if insurer_details.exists() else ""
                iban = insurer_details[0].iban if insurer_details.exists() else ""
                ctx['bank_name'] = bank_name
                ctx['iban'] = iban
            
        elif stage == STAGE_POLICY_ISSUANCE:
            #ctx["extended_expiry_date"]
            self.template_name = 'healthinsurance/deals/components/policy_stage.djhtml'
            ctx['referrers'] = self.get_company_agents_list()
        elif stage == STAGE_HOUSE_KEEPING:
            #ctx["extended_expiry_date"]
            self.template_name = 'healthinsurance/deals/components/housekeeping_stage.djhtml'
            policy = HealthPolicy.objects.filter(deal = deal)
            if policy.exists():
                ctx['is_policy_link_active'] = policy[0].get_policy_link_status()
            order = deal.get_order()
            ctx['is_basic_plan_selected'] = True if order and order.selected_plan.plan.coverage_type == 'basic' else False
            
        elif stage == STAGE_WON:
            self.template_name = 'healthinsurance/deals/components/deal_won.djhtml' 
            order = deal.get_order()
            policy = HealthPolicy.objects.filter(deal = deal)
            policy = policy[0] if policy.exists() else None
            ctx['order'] = order
            ctx['policy'] = policy
            if policy:
                ctx['is_policy_link_active'] = policy.get_policy_link_status()
            
        if stage in closed_stages:
            ctx['has_closed'] = deal.stage in closed_stages
            self.template_name = 'healthinsurance/deals/components/closed_overview.djhtml'
            
        
        sub_stage_number = sub_stages_to_number(stage = stage, sub_stage = sub_stage)
        stage_number = deal_stages_to_number(stage)
        if stage_number > 1:
            reference_number = None if quote.reference_number is None else quote.reference_number
            absolute_quote_url = f"{DOMAIN}/health-insurance-quote/{reference_number}/{deal.pk}/"
            quote_link = f"https://{DOMAIN}/health-insurance-quote/{reference_number}/{deal.pk}/"
            ctx['absolute_quote_url'] = absolute_quote_url
            ctx['quote_link'] = quote_link
        ctx["quote"] = quote
        ctx["quoted_products"] = quoted_products
        ctx['is_quote_link_active'] = deal.get_deal_quote_link_status()
        ctx['stage'] = stage
        ctx['sub_stage'] = sub_stage
        ctx['stage_number'] = stage_number
        ctx['sub_stage_number'] = sub_stage_number
        ctx["entity"] = "health"
        return ctx

def get_quote_data(quote, order=None):
    pass

class DealQuotedProductsView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = ('auth.create_health_quotes')
    model = Deal

    def get(self, request, *args, **kwargs):
        deal = self.get_object()
        response = []
        quote = Quote.objects.filter(deal = deal)
        plan_id = request.GET.get('qp_id', None)
        if plan_id:
            quoted_plan = QuotedPlan.objects.filter(pk = plan_id)
            quoted_plan = quoted_plan[0] if quoted_plan.exists() else None
            if quoted_plan:
                response.append({
                    'id': quoted_plan.pk,
                    'product_id': quoted_plan.plan.pk,
                    'plan_logo': quoted_plan.plan.insurer.logo.url,
                    'plan_name': quoted_plan.plan.name,
                    'premium': "{:,}".format(quoted_plan.total_premium),
                    'payment_frequency': quoted_plan.payment_frequency,
                    'area_of_cover': quoted_plan.area_of_cover,
                    'copayment': quoted_plan.copayment,
                    'inpatient_deductible': quoted_plan.inpatient_deductible,
                    'network': quoted_plan.network,
                    'annual_limit': quoted_plan.annual_limit,
                    'physiotherapy': quoted_plan.physiotherapy,
                    'alternative_medicine': quoted_plan.alternative_medicine,
                    'maternity_benefits': quoted_plan.maternity_benefits,
                    'maternity_waiting_period': quoted_plan.maternity_waiting_period,
                    'dental_benefits': quoted_plan.dental_benefits,
                    'wellness_benefits': quoted_plan.wellness_benefits,
                    'optical_benefits': quoted_plan.optical_benefits,
                    'pre_existing_cover': qp.pre_existing_cover,
                    'renewal_document': quoted_plan.plan_renewal_document,
                    'premium_breakdown' : quoted_plan.premium_info if quoted_plan.premium_info else dict(),
                    'is_renewal': quoted_plan.is_renewal_plan,
                    'is_repatriation_enabled': quoted_plan.is_repatriation_benefit_enabled,

                })
                return JsonResponse(response, safe=False)

        if quote.exists():
            quote = quote[0]
            for qp in quote.get_editable_quoted_plans():
                qp_dict = {
                    'id': qp.pk,
                    'product_id': qp.plan.pk,
                    'insurer_id' : qp.plan.insurer.id,
                    'plan_logo': qp.plan.insurer.logo.url,
                    'plan_name': qp.plan.name,
                    'total_premium': qp.total_premium if type(qp.total_premium) == str else "{:,}".format(qp.total_premium),
                    'currency': qp.currency.id if qp.currency else '',
                    'payment_frequency': qp.payment_frequency.id if qp.payment_frequency else '',
                    'area_of_cover': qp.area_of_cover.id if qp.area_of_cover else '',
                    'copay_mode': qp.plan.copay_mode,
                    "consultation_copay":qp.consultation_copay.id if qp.consultation_copay else '',
                    "diagnostics_copay":qp.diagnostics_copay.id if qp.diagnostics_copay else '',
                    "pharmacy_copay":qp.pharmacy_copay.id if qp.pharmacy_copay else '',
                    'inpatient_deductible': qp.inpatient_deductible.id if qp.inpatient_deductible else '',
                    "network":qp.network.id if qp.network else '',
                    "annual_limit":qp.annual_limit.id if qp.annual_limit else '',
                    'physiotherapy': qp.physiotherapy.id if qp.physiotherapy else '',
                    'alternative_medicine': qp.alternative_medicine.id if qp.physiotherapy else '',
                    'maternity_benefits': qp.maternity_benefits.id if qp.maternity_benefits else '',
                    'maternity_waiting_period': qp.maternity_waiting_period.id if qp.maternity_waiting_period else '',
                    'dental_benefits': qp.dental_benefits.id if qp.dental_benefits else '',
                    'wellness_benefits': qp.wellness_benefits.id if qp.wellness_benefits else '',
                    'optical_benefits': qp.optical_benefits.id if qp.optical_benefits else '',
                    'pre_existing_cover': qp.pre_existing_cover.id if qp.pre_existing_cover else '',
                    'is_renewal': qp.is_renewal_plan,
                    'is_repatriation_enabled': qp.is_repatriation_benefit_enabled,
                    'renewal_document': qp.plan_renewal_document.url if qp.plan_renewal_document else '',
                    'renewal_document_name': qp.renewal_filename if qp.plan_renewal_document else '',
                }
                premium_data = qp.premium_info
                if premium_data:
                    for key in premium_data:
                        qp_dict[key] = premium_data[key]

                response.append(qp_dict)

        return JsonResponse(response, safe=False)

    def post(self, request, **kwargs):
        try:
            deal = self.get_object()
            creating = True
            deleted = False
            request_data = json.loads(request.POST.get('data',''))
            primary_member = deal.primary_member
            quote = Quote.objects.filter(deal = deal)
            substage = deal.get_sub_stage(stage = STAGE_QUOTE ,substage = STAGE_QUOTE)
            try:
                if not substage:
                    substage = SubStage.objects.create(deal = deal, stage = STAGE_QUOTE, sub_stage = STAGE_QUOTE)
            except Exception as e:
                pass
            
            if not quote.exists():
                quote = Quote.objects.create(deal=deal, company=request.company,                                 
                                    status=Quote.STATUS_PUBLISHED)
            else:
                quote = quote[0]

            basic_plan_count = 0
            total_plans = len(request_data.get('products'))
            for request_qp in request_data['products']:
                if request_qp:
                    rqp = request_qp  # shortform
                    total_premium = rqp['total_premium'].replace(',', '')
                    total_premium = float(total_premium) if total_premium else 0.00
                    if request_qp.get('id'):
                        existing_qp = QuotedPlan.objects.filter(pk = rqp.get('id'))
                        if existing_qp.exists():
                                existing_qp = existing_qp[0]
                                data = {'primary_member_premium' : rqp.get('primary_member_premium')}
                                for member in deal.primary_member.additional_members.all():
                                    key = 'member_{0}_premium'.format(member.id)
                                    data[key] = rqp.get(key)

                                if rqp.get('deleted'):
                                    existing_qp.status = QuotedPlan.STATUS_DELETED
                                    total_plans -= 1
                                elif rqp.get('published'):
                                    existing_qp.status = QuotedPlan.STATUS_PUBLISHED
                                elif not rqp.get('published'):
                                    existing_qp.status = QuotedPlan.STATUS_UNPUBLISHED

                                existing_qp.plan_id = rqp.get('product_id')
                                #existing_qp.insurer_quote_reference = rqp.get('insurer_quote_reference')
                                existing_qp.total_premium = total_premium
                                existing_qp.payment_frequency_id = rqp.get('payment_frequency')
                                existing_qp.currency_id = rqp.get('currency')
                                existing_qp.area_of_cover_id = rqp.get('area_of_cover')
                                existing_qp.network_id = rqp.get('network')
                                existing_qp.annual_limit_id = rqp.get('annual_limit')
                                existing_qp.physiotherapy_id = rqp.get('physiotherapy')
                                existing_qp.alternative_medicine_id = rqp.get('alternative_medicine')
                                existing_qp.maternity_benefits_id = rqp.get('maternity_benefits')
                                existing_qp.maternity_waiting_period_id = rqp.get('maternity_waiting_period')
                                existing_qp.dental_benefits_id = rqp.get('dental_benefits')
                                existing_qp.wellness_benefits_id = rqp.get('wellness_benefits')
                                existing_qp.optical_benefits_id = rqp.get('optical_benefits')
                                existing_qp.consultation_copay_id = rqp.get('consultation_copay')
                                existing_qp.diagnostics_copay_id = rqp.get('diagnostics_copay')
                                existing_qp.pharmacy_copay_id = rqp.get('pharmacy_copay')
                                existing_qp.pre_existing_cover_id = rqp.get('pre_existing_cover')
                                existing_qp.inpatient_deductible_id = rqp.get('inpatient_deductible')
                                existing_qp.is_renewal_plan = rqp.get('is_renewal')
                                existing_qp.is_repatriation_benefit_enabled = rqp.get('is_repatriation_enabled')
                                existing_qp.premium_info = data
                                if request.FILES and request.FILES.get(rqp.get('product_id')):
                                    existing_qp.plan_renewal_document = request.FILES.get(rqp.get('product_id'))
                            
                                existing_qp.save(user=request.user)
                                quote.save(user = request.user)
                                for member in primary_member.additional_members.all():
                                        try:
                                            member_premium = rqp.get('member_{0}_premium'.format(member.id))
                                            member.premium = float(member_premium) if member_premium else 0
                                            member.save()
                                        except Exception as e:
                                            pass

                                basic_plan_count += 1 if existing_qp.plan.coverage_type == 'basic' else 0
                
                    else:
                                data = {'primary_member_premium' : rqp['primary_member_premium']}
                                for member in deal.primary_member.additional_members.all():
                                    key = 'member_{0}_premium'.format(member.id)
                                    data[key] = rqp.get(key)

                                new_qp = QuotedPlan(quote=quote, plan_id=rqp.get('product_id'),                        
                                total_premium = total_premium,
                                currency_id = rqp.get('currency'),
                                area_of_cover_id = rqp.get('area_of_cover'),
                                consultation_copay_id = rqp.get('consultation_copay'),
                                pharmacy_copay_id = rqp.get('pharmacy_copay'),
                                diagnostics_copay_id = rqp.get('diagnostics_copay'),
                                network_id = rqp.get('network'),payment_frequency_id = rqp.get('payment_frequency'),
                                annual_limit_id = rqp.get('annual_limit'), physiotherapy_id = rqp.get('physiotherapy'),
                                alternative_medicine_id = rqp.get('alternative_medicine'), maternity_benefits_id = rqp.get('maternity_benefits'),
                                maternity_waiting_period_id = rqp.get('maternity_waiting_period'), dental_benefits_id = rqp.get('dental_benefits'),
                                wellness_benefits_id = rqp.get('wellness_benefits'), optical_benefits_id = rqp.get('optical_benefits'),
                                pre_existing_cover_id = rqp.get('pre_existing_cover'),inpatient_deductible_id = rqp.get('inpatient_deductible'),
                                is_renewal_plan = rqp.get('is_renewal'),is_repatriation_benefit_enabled = rqp.get('is_repatriation_enabled'),
                                plan_renewal_document = request.FILES.get(rqp.get('product_id')) if request.FILES and request.FILES.get(rqp.get('product_id')) else None,
                                premium_info = data
                                )
                                if rqp.get('published'):
                                    new_qp.status = QuotedPlan.STATUS_PUBLISHED
                                else:
                                    new_qp.status = QuotedPlan.STATUS_UNPUBLISHED
                            
                                new_qp.save(user=request.user)
                                quote.save(user = request.user)
                                for member in primary_member.additional_members.all():
                                        try:
                                            member_premium = rqp.get('member_{0}_premium'.format(member.id))
                                            member.premium = float(member_premium) if member_premium else 0
                                            member.save()
                                        except Exception as e:
                                            pass

                                basic_plan_count += 1 if new_qp.plan.coverage_type == 'basic' else 0

            deal.status = STATUS_CLIENT                
            if total_plans == basic_plan_count:
                deal.stage = STAGE_BASIC
                substage.stage = STAGE_BASIC
                substage.sub_stage = BASIC_QUOTED
            else:
                deal.stage = STAGE_QUOTE
                substage.stage = STAGE_QUOTE
                substage.sub_stage = STAGE_QUOTE
            
            
            if request_data['quote']['delete']:         #and not quote.get_editable_quoted_products().count()
                deal.stage = STAGE_NEW
                quote.is_deleted = True
                deleted = True
            else:
                quote.status = Quote.STATUS_PUBLISHED if request_data['quote'].get('status') else Quote.STATUS_UNPUBLISHED
                quote.is_deleted = False

            substage.save()
            deal.save()
            quote.save()
            absolute_quote_url = f"{DOMAIN}/health-insurance-quote/{quote.reference_number}/{deal.pk}/"
            quote_link =  f"https://{DOMAIN}/health-insurance-quote/{quote.reference_number}/{{deal.pk}}/"
            return JsonResponse({'success': True, 'creating': creating, 'deleted': deleted, 'absolute_quote_url':absolute_quote_url,'quote_link' : quote_link})
    
        except Exception as e:
            api_logger.error('Error while creating deal quote Source: %s, Error: %s',
                                         'health-quote', e)
            return JsonResponse({'success': False, 'message': 'Could not create quote for this deal'})


class DealGetProductsAjax(DealEditBaseView, CompanyAttributesMixin, View):
    permission_required = 'auth.list_health_deals'

    def get(self, *args, **kwargs):
        return JsonResponse(self.serialize_products())


    def serialize_products(self):
        data = dict()

        for product in Plan.objects.all().order_by('insurer__name'):
            data[product.id] = {
                'id': product.pk,
                'name': product.name,
                'active': product.is_active,
                'insurer': product.insurer.name,
                'insurer_id': product.insurer_id,
                'code': product.code,
                #'allows_agency_repair': product.allows_agency_repair,
                #'is_tpl_product': product.is_tpl_product,
                'logo': product.get_logo(),
                #'addons': product.get_add_ons(),
            }

        return data


class DealAddAttachment(View):
    #permission_required = ('auth.update_motor_deals',)
    permission_classes = ('auth.update_health_deals',)

    # def get_permission(self):
    #     if self.request.method == 'POST':
    #         return [permission() for permission in self.permission_classes]
        #return [AllowAny()]

    def get(self, *args, **kwargs):
        return JsonResponse({"status":True, "file_names":{
        "pre":[ x for x,y in DOCUMENT_NAMES[:9]],
        "post":[ x for x,y in DOCUMENT_NAMES[9:]]
        }})

    def post(self, request, *args, **kwargs):
        #self.get_permission()
        doc_type = kwargs.get('type', None)
        deal = get_object_or_404(Deal, pk=kwargs.get("pk"))
        type = request.GET.getlist('type',"general")[0]
        member_id = request.GET.getlist('member',"")[0]
        files = request.FILES.getlist("file")
        response = {}
        if doc_type == 'member_documents':
            deal_member = AdditionalMember.objects.filter(pk = member_id)
            if deal_member.exists():
                deal_member = deal_member[0]
                new_deal_file = MemberDocuments(file=request.FILES['file'],deal=deal,type=type, member = deal_member)
                response['doc_type'] = 'member_documents'
                response['member'] = deal_member.pk
        else:
            new_deal_file = DealFiles(file=request.FILES['file'],deal=deal,type=type)
        new_deal_file.save()
        response = {
            "success":True,
            "url":new_deal_file.file.url,
            "file":new_deal_file.filename
        }
        return JsonResponse(response)

class DeleteAttachedFile(DeleteAttachmentView):
    permission_required = ('auth.update_health_deals',)
    #attached_model = PreApproval

    def get_success_url(self, attached_obj):
        if 'next' in self.request.GET:
            return self.request.GET['next']

        return "{}#tab_documents".format(
            reverse('health-insurance:edit-deal', kwargs={'pk': attached_obj.deal.pk})
        )
    def post(self, request, *args, **kwargs):
        deal = get_object_or_404(Deal, pk=kwargs.get("pk"))
        #type = request.GET.getlist('data_type',"general")
        type = kwargs.get("type")
        file_name = request.GET.get("file")
        is_member_document = request.GET.get("member_document", None)
        member_id = request.GET.get("member", None)
        document_type = request.GET.get("document_type", None)
        files = request.FILES.getlist("file")
        response = {}
        if member_id and is_member_document == '1':
            member_obj = get_object_or_404(AdditionalMember, pk=member_id)
            files = MemberDocuments.objects.filter(deal=deal,type=type,member=member_obj)
        elif document_type == 'policy':
            policy = deal.get_policy()
            if policy:
                files = PolicyFiles.objects.filter(policy=policy,type=type)
            else:
                response = {
                    "success":False,
                }
        else:
            files = DealFiles.objects.filter(deal=deal,type=type)
        
        for file in files:
            if file.filename == file_name:
                file.delete()
                response = {
                    "success":True,
                }
                break
            else:
                response = {
                    "success":False,
                }
        return JsonResponse(response)


def SubStageProcessor(*args, **kwargs):
    current_stage = kwargs.get('current_stage')
    current_sub_stage = kwargs.get('current_sub_stage')
    deal_id = kwargs.get('pk')
    deal = Deal.objects.filter(pk = deal_id)
    deal = deal[0] if deal.exists else None
    substage = deal.current_sub_stage
    if current_stage == 6:
        to_stage = STAGE_HOUSE_KEEPING
        to_sub_stage = ''
        if to_stage:
            deal.stage = to_stage
            deal.save()
            reload = True
            substage.stage = to_stage
        if to_sub_stage:
            substage.sub_stage = to_sub_stage
        substage.save()

    pass

class SubStageView(View):
    def save_file(self, **kwargs):
        file_type = kwargs.get('type')
        uploaded_file = kwargs.get('file')
        deal = kwargs.get('deal')
        deal_file = DealFiles.objects.filter(deal = deal, type = file_type)
        if deal_file.exists():
            deal_file[0].delete()
            deal_file = DealFiles.objects.create(deal = deal, type = file_type, file = uploaded_file)
        else:
            deal_file = DealFiles.objects.create(deal = deal, type = file_type, file = uploaded_file)
        
    def get(self, request, kwargs):
        print(request)
        pass
    def post(self, request, pk):
        print(request.POST)
        deal = Deal.objects.filter(pk = pk)
        deal = deal[0] if deal.exists else None
        stage_data = request.POST.get('stage_data')
        current_stage = ''
        current_sub_stage = ''
        next_sub_stage = ''
        if stage_data:
            data = json.loads(stage_data)
            try:
                current_stage = int(data['current_stage'])
            except:
                current_stage = float(data['current_stage'])
            current_sub_stage = int(data['current_sub_stage'])
            next_stage = int(current_stage) + 1
            next_sub_stage = int(current_sub_stage) + 1
        else:
            current_stage = deal_stages_to_number(deal.stage)
            current_stage = request.POST.get('current_stage')
            current_sub_stage = request.POST.get('current_sub_stage')
        
        substage = deal.current_sub_stage
        saved_stage = deal_stages_to_number(deal.stage)
        saved_substage = sub_stages_to_number(stage = deal.stage, sub_stage = deal.current_sub_stage.sub_stage if deal.current_sub_stage else None)
        if not (deal.stage == STAGE_FINAL_QUOTE and current_sub_stage == 1 and saved_substage == 2):  # case "Resend Final Quote"
            if current_stage != saved_stage or current_sub_stage != saved_substage:                   # handle multiple user scenario
                reload = True
                return JsonResponse(OrderedDict([
                ('saved',False), ('next_sub_stage',saved_substage),('reload',reload)
                ]))
        to_sub_stage = ''
        to_stage = ''
        reload = ''
        uploaded = ''
        status = ''
        is_saved = False
        response = {}
        if current_stage == 3:
            if current_sub_stage == 1 or current_sub_stage == 0:
                to_sub_stage = WORLD_CHECK
                reload = True
                status = STATUS_US
            elif current_sub_stage == 2:
                # if request.POST.get('is_document_verified') == '0':
                #     response['message'] = 'Please contact the compliance team'
                #     return JsonResponse(response)
                world_check_hit = request.POST.get('is_world_check_done')
                approved_by_compliance = request.POST.get('approved_by_compliance')
                substage.world_check_hit = True if world_check_hit == '1' else False
                substage.world_check_approved = approved_by_compliance.lower()
                substage.save()
                if approved_by_compliance == 'yes':
                    # order = deal.get_order()
                    # if order and order.selected_plan.is_renewal_plan:
                    #     to_stage = STAGE_FINAL_QUOTE
                    #     to_sub_stage = FINAL_QUOTE_SEND_TO_CLIENT
                    #     status = STATUS_INSURER
                    # else:
                    to_sub_stage = DOCUMENTS_SEND_TO_INSURER
                else:
                    next_sub_stage = 2
                    response['message'] = 'Please contact the compliance team'

                world_check_doc = request.FILES['world_check_proof']
                deal_file = DealFiles.objects.filter(deal = deal, type="world_check_proof")
                if deal_file.exists():
                    deal_file[0].delete()
                    DealFiles.objects.create(deal = deal, type="world_check_proof", file = world_check_doc)
                else:
                    DealFiles.objects.create(deal = deal, type="world_check_proof", file = world_check_doc)
                uploaded = True
                status = STATUS_US
                
            elif current_sub_stage == 3:
                to_stage = STAGE_FINAL_QUOTE
                to_sub_stage = FINAL_QUOTE_SEND_TO_CLIENT
                status = STATUS_INSURER
        elif current_stage == 4:
            if current_sub_stage == 1:
                to_sub_stage = FINAL_QUOTE_SIGNED
                total_premium = request.POST.get('total_premium')
                final_quote_document = request.FILES.get('final_quote_document')
                deal_file = DealFiles.objects.filter(deal = deal, type="final_quote")
                # order = deal.get_order()
                # if not final_quote_document and order and order.selected_plan.is_renewal_plan:
                #     final_quote_document = order.selected_plan.plan_renewal_document
                if deal_file.exists():
                    deal_file[0].delete()
                    deal_file = DealFiles.objects.create(deal = deal, type="final_quote", file = final_quote_document)
                else:
                    deal_file = DealFiles.objects.create(deal = deal, type="final_quote", file = final_quote_document)
                
                final_quote_additional_document = request.FILES.get('final_quote_additional_document')
                if final_quote_additional_document:
                    self.save_file(deal = deal, type='final_quote_additional_document', file = final_quote_additional_document)

                final_quote_file = deal_file.file.url
                final_quote_filename = deal_file.filename
                deal.total_premium = float(total_premium)
                deal.save()
                status = STATUS_CLIENT
                uploaded = True
                response['final_quote_file'] = final_quote_file
                response['total_premium'] = total_premium
                response['final_quote_filename'] = final_quote_filename
                
            elif current_sub_stage == 2:
                to_sub_stage = FINAL_QUOTE_SEND_TO_INSURER
                status = STATUS_US
            elif current_sub_stage == 3:
                to_stage = STAGE_PAYMENT
                to_sub_stage = PAYMENT_SEND_TO_CLIENT
                status = STATUS_INSURER
        elif current_stage == 5:
            if current_sub_stage == 1:
                to_sub_stage = PAYMENT_CONFIRMATION
                status = STATUS_CLIENT
                payment_url = request.POST.get('payment_url') if request.POST.get('payment_url') else ''
                bank_name = request.POST.get('bank_name') if request.POST.get('bank_name') else ''
                iban = request.POST.get('iban') if request.POST.get('iban') else ''
                payment_details = PaymentDetails.objects.filter(deal = deal)
                payment_mode = ''
                if payment_url and bank_name and iban:
                    payment_mode = "multiple"
                elif bank_name and iban and not payment_url:
                    payment_mode = "bank_details"
                else:
                    payment_mode = "payment_link"

                if payment_details.exists():
                    payment_details = payment_details[0]
                    payment_details.payment_url = payment_url
                    payment_details.bank_name = bank_name
                    payment_details.iban = iban
                    payment_details.payment_mode = payment_mode
                    payment_details.save()
                else:
                    payment_details = PaymentDetails.objects.create(deal = deal, payment_url = payment_url, bank_name = bank_name, iban = iban, payment_mode = payment_mode)
            elif current_sub_stage == 2:
                to_sub_stage = PAYMENT_SEND_TO_INSURER
                status = STATUS_US
            elif current_sub_stage == 3:
                to_stage = STAGE_POLICY_ISSUANCE
                to_sub_stage = POLICY_ISSUANCE
                status = STATUS_INSURER

        elif current_stage == 6:
            updated_request = request.POST.copy()
            quote = Quote.objects.filter(deal = deal)
            reference_number = ''
            if quote.exists:
                reference_number = quote[0].reference_number
            
            updated_request.update({'company':self.request.company,
            'customer':deal.customer,
            'reference_number':reference_number,
            'user':self.request.user,'deal':deal,
            'is_policy_link_active':True
            })
            
            existing_policy = None
            if not deal.deal_type == DEAL_TYPE_RENEWAL:
                policy_number = updated_request.get('policy_number')
                policy = HealthPolicy.objects.filter(policy_number = policy_number)
                if policy.exists():
                    return JsonResponse({
                    "saved":False,
                    "errors": 'Policy with this policy number already exists'
                })
            policy_kwargs = {
                'data': updated_request
            }
            try:
                existing_policy = deal.get_policy()
                if existing_policy and deal.deal_type == DEAL_TYPE_RENEWAL:
                    updated_request.update({'is_policy_link_active':True,
                        'policy_link_reactivated_on':timezone.now()
                    })
                policy_kwargs['instance'] = existing_policy
                creating = False
            except Exception as e:
                pass

            form = PolicyForm(**policy_kwargs)
            
            policy_form = HealthPolicyForm(**policy_kwargs)
            if policy_form.is_valid():
                policy = policy_form.save()
                for file in request.FILES:
                    PolicyFiles.objects.create(policy = policy, file = request.FILES[file], type=file)
                to_stage = STAGE_HOUSE_KEEPING
                status = STATUS_US
                if not deal.referrer and request.POST.get('referrer'):
                    referrer = updated_request['referrer']
                    deal.referrer_id = referrer
                    deal.save()
            else:
                print(policy_form.errors)
                return JsonResponse({
                    "saved":False,
                    "errors":policy_form.errors
                })
            
        elif current_stage == 7:
            to_stage = STAGE_WON

        elif current_stage == 6.5:
            to_stage = STAGE_HOUSE_KEEPING
            status = STATUS_US

        if to_stage:
            deal.stage = to_stage
            if status:
                deal.status = status
            deal.save()
            if not deal.stage == STAGE_HOUSE_KEEPING:
                reload = True
            is_saved = True
            if substage:
                substage.stage = to_stage
        if to_sub_stage:
            if substage:
                substage.sub_stage = to_sub_stage
                substage.save()
                is_saved = True
            else:
                SubStage.objects.create(deal = deal, stage = deal.stage, sub_stage = to_sub_stage)
            if status:
                deal.status = status
                deal.save()
                
        response.update({
            'saved' : is_saved,
            'next_sub_stage' : next_sub_stage,
            'reload' : reload,
            'status': status
        })
        return JsonResponse(response)


class StageProcessView(View):
    def post(self, request, *args, **kwargs):
        pk = request.POST.get("pk", None)
        #deal = get_object_or_404(Deal,pk)
        deal = Deal.objects.filter(pk = pk)
        deal = deal[0] if deal.exists() else None
        stage = deal.stage
        post_data = request.POST.dict()
        customer_form= CustomerForm(post_data)
        message = "stage updated"
        to_sub_stage = ''
        email_sent = False
        cc_email = []
        bcc_email = []
        notification_email = ''
        if deal.referrer and deal.referrer.email:
            cc_email.append(deal.referrer.email)
        if deal.primary_member and deal.primary_member.visa == EMIRATE_ABU_DHABI:
            notification_email = 'auhpls.hotline@nexusadvice.com'
            bcc_email.append(notification_email)
        else:
            notification_email = get_email_address_for_deal(deal)
            bcc_email.append(notification_email)
        if stage == STAGE_QUOTE or stage == STAGE_BASIC:
                if request.POST.get("plan"):
                        selected_plan = get_object_or_404(QuotedPlan, pk=request.POST.get("plan"))
                        post_data["selected_plan"] = selected_plan
                        post_data["deal"] = deal
                        post_data["status"] = STATUS_UNPAID
                        post_data["policy_start_date"] = deal.start_date if deal.start_date else datetime.today()
                        post_data["payment_amount"] = 0
                        form = OrderForm(post_data)
                        quote = deal.health_quote_deals
                        if form.is_valid():
                            order = form.save()
                            deal.status = STATUS_CLIENT
                            #sending order confirmation email to ind.medical
                            email_notification(deal, 'order confirmation team notification', notification_email)
                            # if selected_plan.is_renewal_plan:
                            #     deal.deal_type = DEAL_TYPE_RENEWAL

                            #PDF generation when order is created
                            # try:
                            #     source = order.get_pdf_url()
                            #     pdf = PDF().get_pdf_content(source)
                            #     pdf_file = io.BytesIO(pdf)
                            #     DealFiles.objects.create(deal = deal, type = 'order_confirmation', file = pdf_file)
                            # except Exception as e:
                            #     print(e)
                        else:
                            return JsonResponse(
                                {
                                    "success": False,
                                    "errors": form.errors,
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                        if selected_plan.plan.coverage_type == 'basic':
                            to_stage = STAGE_BASIC
                            to_sub_stage = BASIC_SELECTED
                        else:
                            to_stage = STAGE_DOCUMENTS
                            to_sub_stage = SUBMIT_DOCUMENTS

        elif stage == STAGE_DOCUMENTS:
            for file in request.FILES:
                if 'member' in file:
                    a = file.split('_')
                    id = a[2]
                    additional_member = AdditionalMember.objects.filter(pk = id)
                    if additional_member.exists():
                        additional_member = additional_member[0]
                        for doc in request.FILES.getlist(file):                     
                            MemberDocuments.objects.create(deal = deal, type = a[1], file = doc, member = additional_member)
                else:
                    for doc in request.FILES.getlist(file):
                        DealFiles.objects.create(deal = deal, type = file, file = doc)
            to_stage = STAGE_DOCUMENTS
            to_sub_stage = WORLD_CHECK
            deal.status = STATUS_US
            if deal.primary_member.email:
                #1. sending order confirmation email to customer
                email_notification(deal, 'order_confirmation', deal.primary_member.email, cc_emails = cc_email, bcc_emails = bcc_email)
                email_sent = True
            
        elif stage == STAGE_FINAL_QUOTE:
            for file in request.FILES:
                deal_file = DealFiles.objects.filter(deal = deal, type = file)
                if deal_file.exists():
                    deal_file[0].delete()
                    DealFiles.objects.create(deal = deal, type = file, file = request.FILES.get(file))
                else:
                    DealFiles.objects.create(deal = deal, type = file, file = request.FILES.get(file))
            to_stage = STAGE_FINAL_QUOTE
            to_sub_stage = FINAL_QUOTE_SEND_TO_INSURER
            deal.status = STATUS_US
            if deal.primary_member.email:
                email_notification(deal, 'final_quote_submitted', deal.primary_member.email, cc_emails = cc_email, bcc_emails = bcc_email)
                #email_notification(deal, 'final_quote_submitted', deal.primary_member.email, cc_emails=['ind.medical@nexusadvice.com'])
                #email_notification(deal, 'final quote signed internal notification', 'ind.medical@nexusadvice.com')   #CC Emails to ind.medical instead of different email
                email_sent = True
        
        elif stage == STAGE_PAYMENT:
            deal_file = DealFiles.objects.filter(deal = deal, type = 'payment_proof')                
            payment_proof = request.FILES.get('payment_proof')
            if payment_proof:
                if deal_file.exists():
                    deal_file[0].delete()
                    DealFiles.objects.create(deal = deal, type = 'payment_proof', file = payment_proof)
                else:
                    DealFiles.objects.create(deal = deal, type = 'payment_proof', file = payment_proof)
                
            to_stage = STAGE_PAYMENT
            to_sub_stage = PAYMENT_SEND_TO_INSURER
            deal.status = STATUS_US
            if deal.primary_member.email:
                email_notification(deal, 'payment_confirmation', deal.primary_member.email, cc_emails = cc_email, bcc_emails = bcc_email) #BCC to ind.medical instead of CC
                #email_notification(deal, 'payment proof uploaded internal notification', 'ind.medical@nexusadvice.com')  #CC Emails to ind.medical instead of different email
                email_sent = True
        
        
        deal.stage = to_stage
        substage = SubStage.objects.filter(deal = deal, stage = stage)
        if substage.exists():
            substage = substage[0]
            substage.stage = to_stage
            if to_sub_stage:
                substage.sub_stage = to_sub_stage
            substage.save()
        deal.save()
        response = {
            'success':True,
            'message':message,
            'stage':to_stage,
            'substage':to_sub_stage
        }
        if email_sent:
            response['email_sent'] = email_sent
        return JsonResponse(response)

class PolicyView(View):
    # policy_form = PolicyForm

    # def get_form_kwargs
    def post(self, request):
        updated_request = request.POST.copy()
        reference_number = ''
        updated_request.update({'company':self.request.company,
        'user':self.request.user,
        })
        customer_id = request.POST.get('customer')
        customer_name = request.POST.get('name')
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
        start_date = datetime.strptime(start_date, "%d/%m/%Y") if start_date else None
        expiry_date = request.POST.get('expiry_date',None)
        expiry_date = datetime.strptime(expiry_date, "%d/%m/%Y") if expiry_date else None
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


class HealthPlans(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        pk = kwargs.get('pk')
        plans = Plan.objects.filter(insurer_id = pk)
        deal_id = self.request.GET.get('deal')
        deal = get_object_or_404(Deal, pk=deal_id)
        visa = deal.primary_member.visa
        plan_applicable_visa = get_deal_visa(visa)
        plans_list = []
        for plan in plans:
            if plan.is_active and plan.applicable_visa.all().filter(name = plan_applicable_visa).exists():
                plans_list.append({
                    'id':plan.pk,
                    'name':plan.name,
                })

        return JsonResponse({
            'status':True,
            'plans':plans_list
        })


class BasicHealthPlans(View):
    @staticmethod
    def get(self, *args, **kwargs):
        deal_id = kwargs.get('pk')
        plans = Plan.objects.filter(coverage_type = 'basic')
        deal = get_object_or_404(Deal, pk=deal_id)
        visa = deal.primary_member.visa
        plan_applicable_visa = get_deal_visa(visa)
        plans_list = []
        response = {}
        data = []
        quote = deal.get_quote()
        
        for qp in quote.get_editable_quoted_plans():
            if qp.plan.is_active and qp.plan.applicable_visa.all().filter(name = plan_applicable_visa).exists():
                plans_list.append({
                    'id': qp.pk,
                    'product_id': qp.plan.pk,
                    'insurer_id' : qp.plan.insurer.id,
                    'plan_logo': qp.plan.insurer.logo.url,
                    'plan_name': qp.plan.name,                    
                    'total_premium': "{:,}".format(qp.total_premium),
                    'currency': qp.plan.currency,
                    'coverage_type': qp.plan.coverage_type,
                    'payment_frequency': qp.payment_frequency.id if qp.payment_frequency else '',
                    'area_of_cover': qp.area_of_cover.id if qp.area_of_cover else '',
                    'copay_mode': qp.plan.copay_mode,
                    "consultation_copay":qp.consultation_copay.id if qp.consultation_copay else '',
                    "diagnostics_copay":qp.diagnostics_copay.id if qp.diagnostics_copay else '',
                    "pharmacy_copay":qp.pharmacy_copay.id if qp.pharmacy_copay else '',
                    'deductible': qp.inpatient_deductible.id if qp.inpatient_deductible else '',
                    "network":qp.network.id if qp.network else '',
                    "annual_limit":qp.annual_limit.id if qp.annual_limit else '',
                    'physiotherapy': qp.physiotherapy.id if qp.physiotherapy else '',
                    'alternative_medicine': qp.alternative_medicine.id if qp.physiotherapy else '',
                    'maternity_benefits': qp.maternity_benefits.id if qp.maternity_benefits else '',
                    'maternity_waiting_period': qp.maternity_waiting_period.id if qp.maternity_waiting_period else '',
                    'dental_benefits': qp.dental_benefits.id if qp.dental_benefits else '',
                    'wellness_benefits': qp.wellness_benefits.id if qp.wellness_benefits else '',
                    'optical_benefits': qp.optical_benefits.id if qp.optical_benefits else '',
                    'pre_existing_cover': qp.pre_existing_cover.id if qp.pre_existing_cover else '',
                    'is_renewal': qp.is_renewal_plan,
                    'renewal_document': qp.plan_renewal_document.url if qp.plan_renewal_document else '',
                    'renewal_document_name': qp.renewal_filename if qp.plan_renewal_document else '',
                })

        deal_details = model_to_dict(deal)
        primary_member = model_to_dict(deal.primary_member)
        primary_member.pop('additional_members')
        deal_details['additional_benefits'] = [model_to_dict(benefit) for benefit in deal.additional_benefits.all()]

        response = {
            "quoted_plans": plans_list,
            "deal":deal_details,
            "primary_member":primary_member,
            "additional_members": [model_to_dict(additional_member) for additional_member in deal.primary_member.additional_members.all()]
            }
        
        return JsonResponse(response)


class GetPlanDetails(DealEditBaseView, CompanyAttributesMixin, View):
    permission_required = 'auth.list_health_deals'
    
    def get(self, *args, **kwargs):
        data = dict()
        pk = kwargs.get('pk')
        action = self.request.GET.get('action')
        plans = Plan.objects.all()
        plan = Plan.objects.filter(pk = pk)
        if plan.exists():
            plan = plan[0]

        plan_serializer = PlanSerializer(plan)
        plan_data = plan_serializer.data
        plan_data['plan_logo'] = plan.insurer.logo.url
        if action == 'edit':
            quoted_plan = QuotedPlan.objects.filter(plan = plan)
            quoted_plan = quoted_plan[0] if quoted_plan.exists() else None
            if quoted_plan:
                qp_serializer = QuotedPlanSerializer(quoted_plan)

                return JsonResponse(OrderedDict([
                    ('data', plan_data),
                    ('quoted_plan', qp_serializer.data)
                    ]))
            else:
                return JsonResponse(OrderedDict([
                ('data', plan_data),
                ]))
        else:
             return JsonResponse(OrderedDict([
                ('data', plan_data),
                ]))


class DealJsonAttributesList(DealEditBaseView, CompanyAttributesMixin, View):
    permission_required = 'auth.list_health_deals'
    
    def get(self, *args, **kwargs):
        type = self.request.GET.get('type')        
        response = {}
        if type == 'assigned_to':
            response = self.get_health_app_user_admin_list()
        elif type == 'agents':
            response = self.get_company_agents_list()
        elif type == 'producers':
            response = self.get_company_producers_list()

        return JsonResponse(response, safe=False)


class DealUpdateFieldView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "auth.update_health_deals"

    def get_object(self, **kwargs):
        try:
            return Deal.objects.get(pk=self.kwargs['pk'])
        except Deal.DoesNotExist:
            raise Http404()

    def post(self, request, *args, **kwargs):
        deal = self.get_object()
        field_name = request.POST['name']
        field_value = strip_tags(request.POST['value'])
        excluded_fields = ['created_on', 'updated_on']

        success = True
        status_code = 200
        message = 'Updated successfully'

        if deal.pk != int(request.POST['pk']) or field_name in excluded_fields:
            return JsonResponse({'success': False, 'message': 'Not allowed.'}, status=401)

        return_value = field_value

        if field_value == '-1':  # To handle the case when user wants to unassign 'assigned_to' and 'producer' fields
            field_value = None
            return_value = 0

        elif field_name == 'referrer_id' and not field_value:
            success = False
            status_code = 400
            message = 'Please select an option.'

        data = {'name': field_name, 'value': return_value}
        if success:
            if field_name == 'insurer_quote_reference':
                quote = deal.get_quote()
                if quote:
                    quote.insurer_quote_reference = field_value
                    quote.save()
            else:
                    setattr(deal, field_name, field_value)
                    deal.save()
            
        return JsonResponse({'success': success, 'message': message, 'data': data}, status=status_code)

class QuoteAPIView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        pk = kwargs.get("pk")
        deal = get_object_or_404(Deal, pk=pk)
        sub_stage = ''
        quote = Quote.objects.filter(deal = deal)
        quote = quote[0] if quote.exists() else None
        plans_detail = GetQuotedPlanDetails(quote)
        deal_details = model_to_dict(deal)
        deal_details['additional_benefits'] = [model_to_dict(benefit) for benefit in deal.additional_benefits.all()]
        quote_details = model_to_dict(quote)
        primary_member = model_to_dict(deal.primary_member)
        primary_member['salary_band'] = SalaryBandText(primary_member['salary_band'])
        additional_members = GetAdditionalMemberDetails(deal.primary_member)
        primary_member.pop('additional_members')
        stage = deal.stage

        response = {}
        data = []
        if deal and stage:
            stage_number = deal_stages_to_number(stage)
            # if stage_number < 6:
            deal_details['is_quote_link_active'] = deal.get_deal_quote_link_status()
            substage = SubStage.objects.filter(deal = deal, stage = deal.stage)
            response["data"] = {
                "quote_reference_number":quote.reference_number if quote else '',
                "quoted_plans":plans_detail,
                "deal":deal_details,
                "quote":quote_details,
                "primary_member":primary_member,
                "additional_members":additional_members,
            }
            if substage.exists():
                substage = substage[0]
                substage = substage.sub_stage
                deal_details['substage'] = substage
            if stage_number > 2:
                order = Order.objects.filter(deal = deal)
                if order.exists():
                    order = order[0]
                    selected_plan = order.selected_plan
                    sp = GetSelectedPlanDetails(selected_plan)
                    if deal.deal_type == DEAL_TYPE_RENEWAL or selected_plan.is_renewal_plan:
                        sp['is_previous_plan_selected'] = True

                    response["data"]["selected_plan"] = sp
            if stage_number == 4:
                quote_file = DealFiles.objects.filter(deal = deal, type = "final_quote")
                quote_file = quote_file[0].file.url if quote_file.exists() else ""
                response['data']['final_quote_document'] = quote_file
                quote_file = DealFiles.objects.filter(deal = deal, type = "final_quote_additional_document")
                if quote_file.exists():
                    response['data']['final_quote_additional_document'] = quote_file[0].file.url

            if stage_number == 5:
                quote_file = DealFiles.objects.filter(deal = deal, type = "payment_proof")
                quote_file = quote_file[0].file.url if quote_file.exists() else ""
                response['data']['payment_proof_document'] = quote_file
            
            if stage_number > 6:
                total_members = len(deal.primary_member.additional_members.all()) + 1
                policy = HealthPolicy.objects.filter(deal = deal)
                policy = policy[0] if policy.exists() else None
                receipt_of_payment, tax_invoice, certificate_of_insurance, medical_card, confirmation_of_cover = [],[],[],[],[]                
                
                policy_files = DealFiles.objects.filter(deal = deal, type = 'receipt_of_payment')
                for doc in policy_files:
                    receipt_of_payment.append(doc.file.url)
                policy_files = PolicyFiles.objects.filter(policy = policy, type = 'receipt_of_payment')
                for doc in policy_files:
                    receipt_of_payment.append(doc.file.url)
                
                policy_files = DealFiles.objects.filter(deal = deal, type = 'tax_invoice')
                for doc in policy_files:
                    tax_invoice.append(doc.file.url)
                policy_files = PolicyFiles.objects.filter(policy = policy, type = 'tax_invoice')
                for doc in policy_files:
                    tax_invoice.append(doc.file.url)

                policy_files = DealFiles.objects.filter(deal = deal, type = 'certificate_of_insurance')
                for doc in policy_files:
                    certificate_of_insurance.append(doc.file.url)
                policy_files = PolicyFiles.objects.filter(policy = policy, type = 'certificate_of_insurance')
                for doc in policy_files:
                    certificate_of_insurance.append(doc.file.url)
                
                
                policy_files = DealFiles.objects.filter(deal = deal, type = 'medical_card')
                for doc in policy_files:
                    medical_card.append(doc.file.url)
                policy_files = PolicyFiles.objects.filter(policy = policy, type = 'medical_card')
                for doc in policy_files:
                    medical_card.append(doc.file.url)
                
                
                policy_files = DealFiles.objects.filter(deal = deal, type = 'confirmation_of_cover')
                for doc in policy_files:
                    confirmation_of_cover.append(doc.file.url)
                policy_files = PolicyFiles.objects.filter(policy = policy, type = 'confirmation_of_cover')
                for doc in policy_files:
                    confirmation_of_cover.append(doc.file.url)
                
                if policy:
                    policy_details = {
                        "total_premium": policy.total_premium_vat_inc,
                        "start_date": policy.start_date,
                        "expiry_date": policy.expiry_date,
                        "policy_number": policy.policy_number,
                        "total_members": total_members,
                        "receipt_of_payment": receipt_of_payment,
                        "tax_invoice": tax_invoice,
                        "certificate_of_insurance": certificate_of_insurance,
                        "medical_card": medical_card,
                        "confirmation_of_cover": confirmation_of_cover,
                        "is_policy_link_active": policy.get_policy_link_status()
                    }
                    response["data"]["policy"] = policy_details

        response["status"] = "ok"
        data.append(response)
        return JsonResponse(response)

class ReactivateQuoteLink(View):
    def post(self, request, *args, **kwargs):
        deal = get_object_or_404(Deal, pk=kwargs.get("pk"))
        #policy = get_object_or_404(HealthPolicy, deal=deal)
        policy = deal.get_policy()
        stage_number = deal_stages_to_number(deal.stage) >= 7
        response = {}
        try:
            if deal and not deal.get_deal_quote_link_status():
                deal.deal_quote_link_reactivated_on = timezone.now()
                deal.save()
                response = {'success':True,
                            'message':'Quote link reactivated successfully'}
            if policy and not policy.get_policy_link_status():
                policy.is_policy_link_active = True
                policy.policy_link_reactivated_on = timezone.now()
                policy.save()
                response = {'success':True,
                        'message':'Quote link reactivated successfully'}
        except Exception as e:
            response = {'success':False,
                        'message':'Could not reactivate Quote link'}
        
        return JsonResponse(response)


class HealthDealHistoryView(DealEditBaseView, CompanyAttributesMixin, TemplateView):
    permission_required = "auth.update_health_deals"
    template_name = "core/_history.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["history"] = Timeline.get_formatted_object_history(self.get_object())
        ctx['entity'] = "health"
        return ctx


class DocumentsZipFile(View):
    def get(self,request, pk, type):
        deal = Deal.objects.filter(pk = pk)
        deal = deal[0] if deal.exists() else None
        sub_type = request.GET.get('subtype')
        ZIPFILE_NAME = type + 'files'
        response = HttpResponse(content_type='application/zip')
        byte = io.BytesIO()
        zf = zipfile.ZipFile(byte, 'w')
        zipped_files = []
        if sub_type:
            zip_filename = 'deal_{0}_documents_{1}.zip'.format(sub_type,deal.primary_member.name.lower())
        else:
            zip_filename = 'deal_{0}_documents_{1}.zip'.format(type,deal.primary_member.name.lower())
        
        if type == 'policy':
            policy_documents = ['receipt_of_payment','tax_invoice','certificate_of_insurance','medical_card','confirmation_of_cover']
            if not request.user.userprofile.has_producer_role():
                policy_documents.extend(['credit_note','other_document'])
            policy = HealthPolicy.objects.filter(deal = deal)
            policy = policy[0] if policy.exists() else None
            policy_files = None
            
            if sub_type:
                policy_files = PolicyFiles.objects.filter(policy = policy, type = sub_type)
                zip_filename = 'policy_{0}_documents_{1}.zip'.format(sub_type,deal.primary_member.name.lower())
            else:
                policy_files = PolicyFiles.objects.filter(policy = policy)
                zip_filename = 'policy_documents_{0}.zip'.format(deal.primary_member.name.lower())
            
            temp_file = io.BytesIO()
            for file in policy_files:
                try:
                    data = file.file.read()
                    file_name = file.filename
                    open(file_name,'wb').write(data)
                    zf.write(file_name)
                except Exception as e:
                    print(e)
            
            
            if sub_type:
                deal_files = DealFiles.objects.filter(deal = deal, type__iexact=sub_type)                
            else:
                deal_files = DealFiles.objects.filter(deal = deal, type__in=policy_documents)            
            
            for file in deal_files:
                try:
                    data = file.file.read()
                    file_name = file.filename
                    open(file_name,'wb').write(data)
                    zf.write(file_name)
                except Exception as e:
                    print(e)

        elif type == 'primary':
            if sub_type:
                deal_files = DealFiles.objects.filter(deal = deal, type = sub_type)
            else:
                deal_files = DealFiles.objects.filter(deal = deal, type__contains = 'primary')
            for file in deal_files:
                try:            
                    data = file.file.read()
                    file_name = file.filename
                    open(file_name,'wb').write(data)
                    zf.write(file_name)
                except Exception as e:
                    print(e)

        elif type == 'member':
            for member in deal.primary_member.additional_members.all():
                if sub_type:
                    member_documents = MemberDocuments.objects.filter(deal = deal, member = member, type = sub_type)
                    zip_filename = 'deal_{0}_{1}_documents_{2}_{3}.zip'.format(type,member.name,sub_type,deal.primary_member.name.lower())
                else:
                    member_documents = MemberDocuments.objects.filter(deal = deal, member = member)
                    zip_filename = 'deal_{0}_{1}_documents_{2}.zip'.format(type,member.name,deal.primary_member.name.lower())
                for file in member_documents:
                    try:
                        data = file.file.read()                        
                        file_name = file.filename
                        open(file_name,'wb').write(data)
                        zf.write(file_name)
                    except Exception as e:
                        print(e)
        
        elif type == 'other':
            deal_files = DealFiles.objects.filter(deal = deal).exclude(type__contains = 'primary')
            for file in deal_files:
                try:
                    data = file.file.read()
                    file_name = file.filename
                    open(file_name,'wb').write(data)
                    zf.write(file_name)
                except Exception as e:
                    print(e)
        

        zf.close()
        resp = HttpResponse(
        byte.getvalue(), content_type="application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp


class DealBaseView(LoginRequiredMixin, PermissionRequiredMixin, AjaxListViewMixin, View):
    permission_required = 'auth.list_health_deals'
    

    def get_queryset(self):
        qs = Deal.objects.filter().order_by('created_on')

        so_form = self.get_search_and_ordering_form()

        if so_form.is_valid():
            # if so_form.cleaned_data['status']:
            #     qs = qs.filter(status=so_form.cleaned_data['status'])
            # else:
            #     qs = qs.filter(~Q(status=HealthPolicy.STATUS_DELETED))

            if so_form.cleaned_data['created_on_after']:
                qs = qs.filter(created_on__gte=so_form.cleaned_data['created_on_after'])
            if so_form.cleaned_data['created_on_before']:
                qs = qs.filter(created_on__lte=so_form.cleaned_data['created_on_before'] + relativedelta(days=1))

            if so_form.cleaned_data['search_term']:
                st = so_form.cleaned_data['search_term']
                qs = qs.filter(
                    Q(customer__name__icontains=st) |
                    Q(customer__email__icontains=st)
                )

            order_by = so_form.cleaned_data.get('order_by')

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
        return DealSearchAndOrderingForm(data=self.request.GET, company=self.request.company)


class DealExportView(DealBaseView, View):
    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = list()
        column_labels = [
            '#','Stage', 'Status','Primary Customer','Primary Customer Email','Primary Customer Phone','Insurer', 'Budget', 'Premium', 
            'No. of Members', 'Emirate', 'Selected Plan','User', 'Referrer',
            'Created On', 'Updated On']

        counter = 1
        for deal in qs:
            customer = deal.customer
            created_on = deal.created_on.strftime('%Y-%m-%d') if deal.created_on else ''
            start_date = deal.start_date.strftime('%Y-%m-%d') if deal.start_date else ''
            user = ''
            referrer = ''
            order = deal.get_order()
            selected_plan = ''
            insurer = ''
            total_premium = ''
            if order:
                    selected_plan = order.selected_plan.plan
                    insurer = order.selected_plan.plan.insurer.name
                    total_premium = f'{selected_plan.currency} {deal.total_premium}'

            selected_plan_name = selected_plan.name if selected_plan else ''
            data.append([
                counter, deal.stage, deal.status_text, customer.name, customer.email, customer.phone, 
                insurer, deal.indicative_budget, total_premium, 
                deal.primary_member.additional_members.all().count(), deal.primary_member.visa,
                selected_plan_name, deal.user, deal.referrer, created_on, start_date
            ])

            counter+=1

        exporter = ExportService()

        return exporter.to_csv(column_labels, data, filename='deals-{}.csv'.format(datetime.today()))


class DealVoid(View):
    def post(self, request, pk):
        deal = get_object_or_404(Deal, pk=pk)
        quote = deal.get_quote()
        deal.stage = STAGE_QUOTE
        sub_stages = SubStage.objects.filter(deal = deal)
        #quote_sub_stage = deal.get_sub_stage(stage = STAGE_QUOTE, substage = STAGE_QUOTE)
        try:
            orders = Order.objects.filter(deal = deal)
            for order in orders:
                order.delete()
            if sub_stages.exists():
                for sub_stage in sub_stages:
                    sub_stage.delete()
            substage = SubStage.objects.create(deal = deal, stage = STAGE_QUOTE, sub_stage = STAGE_QUOTE)
        except Exception as e:
                pass

        deal.save()
        return JsonResponse({
            'success' : True,
            'message':'Deal has been voided successfully'
        })


def DealJsonView(request):
        try:
            data = []
            start = request.GET.get('start')
            length = request.GET.get('length')
            if start and length:
                start = int(start)
                length = int(length)
                page = math.ceil(start / length) + 1
                per_page = length
            search_term = request.GET.get('search[value]')
            stage_filter = request.GET.get('stage')
            status_filter = request.GET.get('status')
            user = request.GET.get('user')
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            deals = Deal.objects.none()
            is_filtered = False
            query = ''
            
            if(search_term):
                first_name = search_term.split(' ')[0]
                last_name = search_term.split(' ').pop()
                if(search_term == 'user_filter_active' and user):
                    if not user == 'all':
                        first_name = user.split(' ')[0]
                        last_name = user.split(' ').pop()
                        query += f'Q(user__first_name__icontains = "{first_name}", user__last_name__icontains = "{last_name}")'
                        query += f' | Q(referrer__first_name__icontains = "{first_name}", referrer__last_name__icontains = "{last_name}")'
                        is_filtered = True
                else:
                    orders = Order.objects.filter(selected_plan__plan__insurer__name__icontains = search_term)
                    query += f'Q(customer__name__icontains = "{search_term}")'
                    query += f' | Q(user__first_name__icontains = "{first_name}")'
                    query += f' | Q(referrer__first_name__icontains = "{first_name}")'
                    query += f' | Q(user__last_name__icontains = "{last_name}")'
                    query += f' | Q(referrer__last_name__icontains = "{last_name}")'
                    is_filtered = True
                
            if stage_filter:
                query += f'Q(stage__iexact = stage_filter)' if not query \
                        else f'& Q(stage__iexact = stage_filter)'
                is_filtered = True
            if status_filter:
                query += f'Q(status__icontains = status_filter)' if not query \
                         else f'& Q(status__icontains = status_filter)'
                is_filtered = True
            if from_date and to_date:
                from_date = datetime.strptime(from_date, '%Y/%m/%d')
                to_date = datetime.strptime(to_date, '%Y/%m/%d')
                query += 'Q(created_on__gte = from_date, created_on__lte = to_date)' if not query \
                        else '& Q(created_on__gte = from_date, created_on__lte = to_date)'
                is_filtered = True
            if not is_filtered:
                deals = Deal.objects.all()
            else:
                deals = Deal.objects.filter(eval(query))
                
            deals = deals.exclude(status = STATUS_DELETED).order_by('-created_on')
            if request.user.userprofile.has_producer_role():
                deals = deals.filter(Q(user = request.user) | Q(referrer = request.user))
            recordsTotal= deals.count()
            deals = deals[start:start + length]
            for deal in deals:
                checkbox = f'''<label class="felix-checkbox">
                    <input class="select-record" type="checkbox" data-id="{deal.pk}" value="{deal.pk}" />
                    <span class="checkmark"></span>'''
                    
                stage = deal.deal_stage_text
                status = '-' if deal.stage == 'lost' or deal.stage == 'won' else f'<span class="badge badge-{deal.status_badge} badge-font-light badge">{deal.status_text}</span>'
                created_on = deal.deal_timeinfo
                customer = f'<div><a>{deal.primary_member.name} </a> </div>'
                if deal.deal_type == 'renewal':
                    customer += f'<span class="m-t-15 badge badge-default badge-font-light badge-renewal-deal">Renewal Deal</span>'
                selected_plan = deal.selected_plan.insurer.name if deal.selected_plan else '-'
                budget = f'{deal.indicative_budget} AED' if deal.indicative_budget else '-'
                premium = f'{deal.total_premium} {deal.selected_plan.currency}' if deal.total_premium and deal.selected_plan else '-'
                
                if deal.customer:
                    p = {
                        'id' : deal.pk,
                        'checkbox' : checkbox,
                        'stage' : stage,
                        'status' : status,
                        'created_on' : created_on,
                        'customer': customer,
                        'selected_plan': deal.selected_plan.insurer.name if deal.selected_plan else '-',
                        'budget': f'{deal.indicative_budget} AED' if deal.indicative_budget else '-',
                        'premium': premium,
                        'members': deal.primary_member.additional_members.all().count()+1,
                        'visa': deal.primary_member.visa if deal.primary_member.visa else '-',
                        'user': deal.user.get_full_name() if deal.user else '',
                        'referrer': deal.referrer.get_full_name() if deal.referrer else '',
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
        
        except Exception as e:
                return JsonResponse({'success': False,
                                     'message': f'Error while fetching deal list:{e}'
                                })