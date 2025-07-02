import datetime
from django.conf import settings
from django.db.models import Q
from django.contrib.auth import models
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import DeleteView
from mortgage.views.quote import quote_info
from django.apps import apps
from django.forms import model_to_dict
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect, JsonResponse
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.html import escape, strip_tags
from django.views.generic import TemplateView, View, DetailView
from rest_framework.views import status
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from core.views import  DeleteAttachmentView
from core.models import Attachment
from core.timeline import Timeline
from core.mixins import AjaxListViewMixin, CompanyAttributesMixin
from accounts.models import Company
from customers.models import Customer
from mortgage.forms import CreateDealForm, UpdateDealForm, CustomerForm, DealSearchAndOrderingForm, NewDealForm, \
    BankInterestRateForm
from mortgage.models import Bank, DealFiles,CustomerProfile, Deal, IssuedDeal, Order, PostApproval, PreApproval, Quote, SegmentedRate, order_number
from mortgage.serializers import UserSerializer
from mortgage.utils import BankHelper, deal_stages_to_number
from mortgage.constants import *
from core.views import AddNoteView, DeleteNoteView, AddEditTaskView
from decimal import Decimal
from mortgage.utils import get_quote_data
from core.forms import TaskForm, AttachmentForm

def attachment_serializer_for_frontend(attachments, location_label="", location_url=""):
        data = []
        for attachment in attachments:
            file_info =   {
                "id": attachment.id,
                "label": attachment.filename,
                "url": attachment.file.url,
                "can_preview": True,
                "extension": attachment.file.name.rsplit('.', 1)[-1].upper(),
                "added_by": '',
                "created_on": attachment.created_on.strftime("%Y-%m-%d"),
            }
        return data

class MortgageDealBaseView(LoginRequiredMixin, PermissionRequiredMixin, AjaxListViewMixin, View):
    def get_search_and_ordering_form(self):
        return DealSearchAndOrderingForm(data=self.request.GET, company=self.request.company)


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
                # and deal.assigned_to != self.request.user 
            ):
                raise Http404()

            return deal
        except Deal.DoesNotExist:
            raise Http404()

    def serialize_banks(self):
        data = dict()

        for bank in Bank.objects.all().order_by("name"):
            data[bank.bank_id] = {
                "bank_id": bank.bank_id,
                "name": bank.name,
                "logo": bank.logo,
                "property_valuation_fee": bank.property_valuation_fee,
                "bank_processing_fee_rate": bank.bank_processing_fee_rate,
                # "bank_processing_fee_extra": bank.bank_processing_fee_extra,
                # "max_bank_processing_fee": bank.max_bank_processing_fee,
                "life_insurance_monthly_rate": bank.life_insurance_monthly_rate,
                "full_settlement_percentage": bank.full_settlement_percentage,
                "full_settlement_max_value": bank.full_settlement_max_value,
                "free_partial_payment_per_year": bank.free_partial_payment_per_year,
                "add_fees_to_loan_amount": bank.add_fees_to_loan_amount,
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
                deal.get_car_title(),
                reverse("mortgage:deal-edit", kwargs=dict(pk=deal.pk)),
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

    def get_auto_quotable_insurers(self):
        return [
            {"pk": insurer.pk, "name": insurer.name}
            for insurer in self.request.company.quotable_motor_insurers.all().order_by(
                "name"
            )
        ]

    # Caching can be added here.
    def get_allowed_banks(self):
        banks = dict()

        auto_quotable_insurer_ids = set(
            self.request.company.quotable_motor_insurers.values_list(
                "id", flat=True
            ).all()
        )

        for bank in Bank.objects.all().order_by("name"):
            bank_id = bank.bank_id
            if bank_id not in banks:
                banks[bank_id] = {
                    "pk": bank_id,
                    "name": bank.name,
                    "logo": bank.logo.url if bank.logo else "",
                    "auto_quotable": bank_id in auto_quotable_insurer_ids,
                }
        return banks


class MortgageDealSingleView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        today = datetime.datetime.today()

        try:
            deal = Deal.objects.get(pk=kwargs['pk'])
            data = {'success': True}

            data['deal'] = {
                "id": deal.pk,
                "deal_type": deal.deal_type,

                "selected_product": '',
                "selected_product_insurer": '',
                "selected_product_premium": '',
                "order_payment_amount": '',
                "selected_product_cover": '',

                "created_on": deal.created_date.isoformat()
            }

            if deal.customer:
                data['customer'] = {
                    "name": deal.customer.name,
                    "email": deal.customer.email,
                    "dob": deal.customer.dob,
                    "age": deal.customer.get_age(),
                    "gender": deal.customer.get_gender_display(),
                    "nationality": deal.customer.get_nationality_display(),
                }

        except Deal.DoesNotExist:
            data = {'success': False}

        return JsonResponse(data)


class MortgageDeals(TemplateView, MortgageDealBaseView):
    template_name = "mortgage/deal/mortgage_deal_list.djhtml"
    permission_required = "auth.list_motor_deals"

    def get_context_data(self, **kwargs):
        filters = ""
        if self.request.user.userprofile.has_producer_role():
            filters = "producer_id:{user_id} OR assigned_to_id:{user_id}".format(
                user_id=self.request.user.pk
            )

        ctx = super(MortgageDeals, self).get_context_data(**kwargs)
        self.request.session["selected_product_line"] = "mortgage"
        ctx["deal_form"] = CreateDealForm()
        ctx["mortgage_deal_form"] = CreateDealForm()

        ctx["search_form"] = self.get_search_and_ordering_form()

        ctx["default_sort_by"] = self.request.GET.get("sort_by") or "created_on_desc"
        ctx["stage"] = self.request.GET.get("stage", "")
        ctx["sub_stage"] = self.request.GET.get("sub_stage", "")
        ctx["page"] = self.request.GET.get("page", 1)

        ctx["entity"] = "mortgage"
        ctx["entity_switch"] = True
        qs = Deal.objects.filter(~Q(status=STATUS_DELETED))
        if self.request.user.userprofile.has_producer_role():
            qs_ref = qs.filter(referrer=self.request.user)
            qs_producer = qs_ref.union(qs.filter(user=self.request.user))
            qs = qs_producer
        ctx["deals"] = qs.order_by('-pk')
        ctx["banks"] = Bank.objects.all()
        ctx["users"] = User.objects.all()
        ctx["stages"] = DEAL_STATUSES

        return ctx


class MortgageDealsItem(View):
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
                deal_stage_number = deal_stages_to_number(deal.stage)
                context = {
                    "deal": deal,
                    "deal_stage_number":deal_stage_number,
                    "entity": "mortgage",
                    "task_form": TaskForm(company=request.company),
                    "attachment_form": attachment_form,
                    "note_form_action": reverse('mortgage:notes', kwargs={"pk": deal.pk}),
                }
                if hasattr(deal, 'mortgage_quote_deals'):
                    quote_instance = deal.mortgage_quote_deals
                    context["quote_instance"] = quote_instance
                    context["quote"] = quote_instance
                template_name = "mortgage/deal/mortgage_deal_details.djhtml"
                return render(request, template_name, context)
        return HttpResponseRedirect(reverse("mortgage:deals"))

    @staticmethod
    def serialize_attachments(attachments, location_label="", location_url=""):
        data = []
        for attachment in attachments:
            file_info =   {
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
            }
            if attachment.content_type.id == 59:
                file_info["document_name"] =PostApproval.objects.get(pk=attachment.object_id).name
            if attachment.content_type.id == 60:
                file_info["document_name"] =PreApproval.objects.get(pk=attachment.object_id).name
            data.append(file_info)

        return data

    def post(self, request, *args, **kwargs):
        deal = Deal.objects.get(pk=kwargs.get("pk"))
        return JsonResponse(
            {
                "title": "Deal",
                "documents": self.serialize_attachments(deal.get_attachments()),
            }
        )


class MortgageDealUpdateFieldView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "auth.update_mortgage_deals"

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
            if field_name == 'l_tv':
                ltv = float(field_value)
                field_name = 'loan_amount'
                field_value = int((ltv * (deal.property_price)) / 100)
                
            setattr(deal, field_name, field_value)
            if (Decimal(deal.down_payment) + Decimal(deal.loan_amount)) > Decimal(deal.property_price):
                if not (field_name == "property_price"):
                    return JsonResponse({
                        'success': False,
                        'message': 'Down Payment and Loan amount should be less than property price '},
                        status=401)
            if not (int(deal.tenure) in range(1, 361)):
                return JsonResponse({'success': False, 'message': 'Ensure value  is  between 1,360 '}, status=401)
            form = UpdateDealForm(model_to_dict(deal), instance=deal)
            if form.is_valid():
                if field_name == "property_price":
                    deal.down_payment = int(field_value) - int(deal.loan_amount)
                    deal.save()
                deal.save(user=self.request.user)
            else:
                return JsonResponse({'success': False, 'message': form.errors.get('__all__')}, status=401)
        return JsonResponse({'success': success, 'message': message, 'data': data}, status=status_code)


class MortgageDealCurrentStageView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.list_motor_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'stage': self.get_object().stage,
        })


class MortgageDealHistoryView(DealEditBaseView, CompanyAttributesMixin, TemplateView):
    permission_required = "auth.update_motor_deals"
    template_name = "core/_history.djhtml"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["history"] = Timeline.get_formatted_object_history(self.get_object())
        for x in ctx['history']:
            if 'L Tv' in x['content']:
                x['content'] = x['content'].replace('L Tv', 'LTV') 
        ctx['entity'] = "mortgage"
        return ctx


class MortgageDealStagesView(DealEditBaseView, DetailView):
    template_name = "mortgage/deal/components/deal_overview.djhtml"
    permission_required = "auth.list_motor_deals"
    model = Deal

    def get_context_data(self, **kwargs):
        deal = self.object
        ctx = super().get_context_data(**kwargs)
        closed_stages = [STAGE_ClosedLOST, STAGE_ClosedWON, "closed"]

        deal_stage_number = deal_stages_to_number(deal.stage)

        modification_allowed = deal.stage not in closed_stages

        if hasattr(deal, 'mortgage_quote_deals'):
            ctx["quote"] = deal.mortgage_quote_deals
            quote_instance = deal.mortgage_quote_deals
            ctx["quote_instance"] = quote_instance
            ctx['quote_info'] = quote_info(quote_instance.pk)

        ctx["modification_allowed"] = modification_allowed
        ctx["allowed_banks"] = self.get_allowed_banks()
        ctx["products_data"] = self.serialize_banks()
        ctx["deal"] = deal
        ctx["interest_form"] = BankInterestRateForm({"deals": Deal.objects.last()}, instance=None)
        ctx["extended_expiry_date"] = None

        if hasattr(deal, "quote"):
            ctx["extended_expiry_date"] = datetime.date.today() + datetime.timedelta(
                days=EXPIRED_QUOTE_EXTENSION_DAYS
            )

        stage = self.request.GET.get("stage") or deal.stage

        ctx["deal_stage_number"] = deal_stage_number

        if hasattr(deal, "deal_bank"):
            bank = deal.deal_bank.bank
            bank_info = Bank.objects.bank_info(pk=bank.pk)
            if deal.mortgage_quote_deals.is_segmented:
                rate = SegmentedRate.objects.get(quote=deal.mortgage_quote_deals).rate
                ctx['rate'] = rate.get_rate
                bank_info = Bank.objects.bank_info(pk=bank.pk, **{"bank_ins": rate})
            else:
                ctx['rate'] = bank.bank_interest_rates.get(is_default=True).get_rate
            
            ctx['monthly_repayment'] = BankHelper(bank_info, deal.property_price, deal.loan_amount, deal.tenure, deal.govt_fee.pk, deal = deal).monthly_repayment

        if stage == STAGE_NEW:
            self.template_name = 'mortgage/deal/components/deal_overview.djhtml'

        if stage == STAGE_QUOTE:
            ctx["extended_expiry_date"]
            self.template_name = 'mortgage/deal/components/deal_overview.djhtml'
            if hasattr(deal, 'deal_bank'):
                ctx['selected_bank'] = deal.deal_bank.bank.pk
                ctx['quote_info'] = get_quote_data(deal.mortgage_quote_deals, deal.deal_bank)[0]

        if stage == "preApproval":
            if hasattr(deal, 'deal_bank'):
                ctx['order'] = deal.deal_bank
                ctx['deal'] = deal
                ctx['quote_info'] = get_quote_data(deal.mortgage_quote_deals, deal.deal_bank)[0] 
            self.template_name = 'mortgage/deal/components/pre_approval_overview.djhtml'

        if stage == STAGE_VALUATION:
            if hasattr(deal, 'deal_bank'):
                ctx['order'] = deal.deal_bank
                ctx['quote_info'] = get_quote_data(deal.mortgage_quote_deals, deal.deal_bank)[0]
            self.template_name = 'mortgage/deal/components/valuation_overview.djhtml'

        if stage == "offer":
            if hasattr(deal, 'deal_bank'):
                ctx['order'] = deal.deal_bank
                ctx['quote_info'] = get_quote_data(deal.mortgage_quote_deals, deal.deal_bank)[0]
            self.template_name = 'mortgage/deal/components/order_overview.djhtml'

        if stage == STAGE_SETTLEMENT:
            if hasattr(deal, 'deal_bank'):
                ctx['order'] = deal.deal_bank
                ctx['quote_info'] = get_quote_data(deal.mortgage_quote_deals, deal.deal_bank)[0]
            self.template_name = 'mortgage/deal/components/settlement_overview.djhtml'

        if stage == "loanDisbursal":
            if hasattr(deal, 'deal_bank'):
                ctx['order'] = deal.deal_bank
                ctx['quote_info'] = get_quote_data(deal.mortgage_quote_deals, deal.deal_bank)[0]
            self.template_name = 'mortgage/deal/components/loan_disbursal_overview.djhtml'

        if stage == "propertyTransfer":
            if hasattr(deal, 'deal_bank'):
                ctx['order'] = deal.deal_bank
                ctx['quote_info'] = get_quote_data(deal.mortgage_quote_deals, deal.deal_bank)[0]
            self.template_name = 'mortgage/deal/components/property_transfer_overview.djhtml'

        if stage in closed_stages:
            if hasattr(deal, 'deal_bank'):
                ctx['order'] = deal.deal_bank
                ctx['quote_info'] = get_quote_data(deal.mortgage_quote_deals, deal.deal_bank)[0]
                ctx["has_closed"] = deal.stage in closed_stages
            self.template_name = "mortgage/deal/components/closed_overview.djhtml"

        return ctx


class MortgageDealAddAttachment(View):
    # permission_required = ('auth.update_motor_deals',)

    def get(self, *args, **kwargs):
        return JsonResponse({"status":True, "file_names":{
        "pre":[ x for x,y in DOCUMENT_NAMES[:9]],
        "post":[ x for x,y in DOCUMENT_NAMES[9:]]
        }})

    def post(self, request, *args, **kwargs):
        deal = get_object_or_404(Deal, pk=kwargs.get("pk"))
        type = kwargs.get("type")
        print(request.path,'\n')
        files = request.FILES.getlist("file")
        file_names = request.POST.getlist("file_names")
        attachments = []
        for i,file in enumerate(files):
            attachments.append(DealFiles.objects.create(files=request.FILES['file'],deal=deal,type=files_names[i].replace(" ","-")))
        response= {"uploaded":"success"}
        return JsonResponse(response)
        file = attachment_serializer_for_frontend(attachments)
        response = {
            "success":True,
            "file":file,
        }
        if failed_uploads:
            response = {
            "status":"ok",
            "message":"Some files not uploaded",
            "detail":{
                "description": "Please check allowed file types is in ['jpeg','jpg', 'png', 'pdf']",
                "files": failed_uploads
                },
        }
        return JsonResponse(response)


class MortgageDealGetProductsView(View):
    permission_required = 'auth.list_mortgage_deals'

    def get(self, *args, **kwargs):
        return JsonResponse({})


class MortgageDealsAddView(TemplateView):
    template_name = "mortgage_deal_list.djhtml"

    def post(self, request):
        post_data = request.POST.dict()
        if post_data.get('customer', None):
            post_data['customer_id'] = post_data.pop('customer') 
        if post_data.get('customer_id'):
            customer = Customer.objects.get(pk=post_data.get('customer_id'))
            post_data['customer_email'] = customer.email
            post_data['customer_phone'] = customer.phone
        form = CreateDealForm(post_data)
        if form.is_valid():
            deal = form.save(commit=False)
            if self.request.user.userprofile.has_producer_role():
                deal.producer = self.request.user
                if deal.referrer is None:
                    deal.referrer = self.request.user

            elif self.request.user.userprofile.has_user_role():
                deal.user = self.request.user

            elif self.request.user.userprofile.has_admin_role():
                deal.user = self.request.user

            if not form.cleaned_data["customer"]:
                customer_form = CustomerForm(post_data)
                if customer_form.is_valid():
                    customer = Customer(**customer_form.cleaned_data)
                    customer.save(user=self.request.user, entity = "mortgage")
                else:
                    return JsonResponse({"success": False, "errors": form.errors})
                deal.customer = customer

            if not hasattr(deal.customer, "customer_mortgage_profiles"):
                CustomerProfile.objects.create(customer=deal.customer)
            
            deal.user = self.request.user
            deal.save()
            return JsonResponse(
                {
                    "success": True,
                    "deal_id": deal.pk,
                    "redirect_url": reverse('mortgage:deal-edit', kwargs={"pk":deal.pk}),
                    "message": "Deal created",
                }
            )
        return JsonResponse({"success": False, "errors": form.errors})

class MortgageDealAttachment(View):
    def get(self, request, *args, **kwargs):
        deal = get_object_or_404(Deal, pk=kwargs.get("pk"))
        data = {}
        attachments_pre = []
        attachments_post =[]
        if PreApproval.objects.filter(deal=deal):
            all_doc = []
            for deal_obj in PreApproval.objects.filter(deal=deal):
                    all_doc += [*deal_obj.attachments.all()] 
            attachments_pre = MortgageDealsItem.serialize_attachments(all_doc
            )
        if PostApproval.objects.filter(deal=deal):
            all_doc = []
            for deal_obj in PostApproval.objects.filter(deal=deal):
                    all_doc += [*deal_obj.attachments.all()] 
            attachments_post = MortgageDealsItem.serialize_attachments(all_doc
            )
        data = {
                "entity": "mortgage",
                'preapproval': attachments_pre,
                "postapproval": attachments_post
            }
        return JsonResponse(data)


class MortgageBrokerDealAdd(View):
    @staticmethod
    def post(request, *args, **kwargs):
        post_data = request.POST.dict()
        form = CustomerForm(post_data)

        if form.is_valid():

            if Customer.objects.filter(email=form.cleaned_data.get('email')):
                customer = Customer.objects.filter(email=form.cleaned_data.get('email'))[0]
            else:
                customer = Customer.objects.create(**form.cleaned_data)
            post_data["customer"] = customer
        else:
            return JsonResponse({"status": "failed", "message": form.errors})

        form = NewDealForm(post_data)
        if form.is_valid():
            instance = Deal.objects.create(customer=customer,**form.cleaned_data)
            val = BankHelper(
                Bank.objects.bank_info(pk=Bank.objects.first().pk),
                instance.property_price,
                instance.loan_amount,
                instance.tenure,
                instance.govt_fee.pk,
            )
            return JsonResponse({"status": "ok", "value": val.monthly_repayment})
        return JsonResponse({"status": "failed", "message": form.errors})



class MortgageDealAddAttachment(View):
    # permission_required = ('auth.update_motor_deals',)

    def get(self, *args, **kwargs):
        return JsonResponse({"status":True, "file_names":{
        "pre":[ x for x,y in DOCUMENT_NAMES[:9]],
        "post":[ x for x,y in DOCUMENT_NAMES[9:]]
        }})

    def post(self, request, *args, **kwargs):
        print(request.FILES)
        deal = get_object_or_404(Deal, pk=kwargs.get("pk"))
        type = request.GET.getlist('type',"general")[0]
        print(type)
        print(request.path,'\n')
        files = request.FILES.getlist("file")
        new_deal_file = DealFiles(file=request.FILES['file'],deal=deal,type=type)
        new_deal_file.save()
        response = {
            "success":True,
            "url":new_deal_file.file.url,
            "file":new_deal_file.filename
        }
        return JsonResponse(response)

class MortgageDealMarkasLostView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.update_mortgage_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        deal = self.get_object()

        if deal.stage not in [STAGE_ClosedWON, STAGE_ClosedLOST]:
            deal.stage = STAGE_ClosedLOST
            deal.save(user=self.request.user)

            return JsonResponse({'success': True})

        return JsonResponse({'success': False})


class MortgageDealReopenView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'auth.update_mortgage_deals'
    model = Deal

    def get(self, request, *args, **kwargs):
        deal = self.get_object()

        if deal.stage in [STAGE_ClosedLOST]:
            if hasattr(deal, 'policy'):
                last_stage = STAGE_PREAPPROVAL
            elif hasattr(deal, 'order'):
                last_stage = STAGE_FINAL_OFFER
            else:
                last_stage = STAGE_NEW

            deal.stage = last_stage
            deal.save(user=self.request.user)

            return JsonResponse({'success': True})

        return JsonResponse({'success': False})


class MortgageDealsNotes(AddNoteView):
    permission_required = ('auth.update_mortgage_deals',)
    model = Deal

    def get_success_url(self):
        return reverse('mortgage:deals')


def delete_note(request, *args, **kwargs):
    from core.models import Note
    Note.objects.get(pk=kwargs.get("pk")).delete()
    return JsonResponse({"success":True})

class EditNote(View):
    def post(self, request, *args, **kwargs):
        from core.models import Note
        Note.objects.filter(pk=request.POST['pk']).update(content=request.POST['content'])
        return JsonResponse({"sucess":True})
    
class MortgageDealsTaskAdd(AddEditTaskView):
    permission_required = ('auth.update_mortgage_deals',)
    attached_model = Deal

class MortgageDealsTasks(AddEditTaskView):
    permission_required = ('auth.update_mortgage_deals',)
    attached_model = Deal

class MortgageDealDeleteAttachment(DeleteAttachmentView):
    permission_required = ('auth.update_mortgage_deals',)
    attached_model = PreApproval

    def get_success_url(self, attached_obj):
        if 'next' in self.request.GET:
            return self.request.GET['next']

        return "{}#tab_documents".format(
            reverse('mortgage:deal-edit', kwargs={'pk': attached_obj.deal.pk})
        )

class MortgageDeleteAttachedFile(DeleteAttachmentView):
    permission_required = ('auth.update_mortgage_deals',)
    attached_model = PreApproval

    def get_success_url(self, attached_obj):
        if 'next' in self.request.GET:
            return self.request.GET['next']

        return "{}#tab_documents".format(
            reverse('mortgage:deal-edit', kwargs={'pk': attached_obj.deal.pk})
        )
    def post(self, request, *args, **kwargs):
        deal = get_object_or_404(Deal, pk=kwargs.get("pk"))
        #type = request.GET.getlist('data_type',"general")
        type = kwargs.get("type")
        file_name = request.GET.get("file")
        print(type)
        print(request.path,'\n')
        files = request.FILES.getlist("file")
        deal_files = DealFiles.objects.filter(deal=deal,type=type)
        for file in deal_files:
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


class MortgageDealDeleteView(View):

    def get(self, request, *args, **kwargs):
        deal = Deal.objects.get(pk=kwargs.get('pk'))
        deal.status = STATUS_DELETED
        deal.save()
        return JsonResponse({
            "success":True
        })


class StatusToggleView(View):
    def post(self, request, *args, **kwargs):
        deal = get_object_or_404(Deal, pk=request.POST.get('deal'))
        deal.status = request.POST.get('status')
        deal.save()
        return JsonResponse({"success":True, "message":"status updated"})


class DeleteDeals(View):
    def post(self, request, *args, **kwargs):
        Deal.objects.filter(pk__in=request.POST.getlist(('deals[]'))).delete()
        return JsonResponse({"success":True, "message":"deleted" })


class BankRefNumber(View):
    def post(self, request, *args, **kwargs):
        try:
            deal = get_object_or_404(Deal,pk=kwargs.get('pk'))
            bankrefno = request.POST.get("bankrefno",'')
            loan_amount = request.POST.get("loan_amount",'')
            property_price = request.POST.get("property_price",'')
            tenure_months = request.POST.get("tenure_months",'')
            ltv = request.POST.get("ltv",'')
            order = Order.objects.filter(deal = deal)
            if order:
                order = deal.deal_bank
                order.bank_reference_number = bankrefno
                order.save()
            issued_deal = IssuedDeal.objects.filter(deal = deal)
            if not issued_deal:
                issued_deal = IssuedDeal.objects.create(deal = deal)
                issued_deal.loan_amount = int(loan_amount) if loan_amount else 0
                issued_deal.property_price = int(property_price) if property_price else 0
                issued_deal.tenure = abs(int(tenure_months)) if tenure_months else 0
                issued_deal.l_tv = float(ltv) if ltv else 0
                issued_deal.save()
            else:
                issued_deal[0].loan_amount = int(loan_amount) if loan_amount else 0
                issued_deal[0].property_price = int(property_price) if property_price else 0
                issued_deal[0].tenure = abs(int(tenure_months)) if tenure_months else 0
                issued_deal[0].l_tv = float(ltv) if ltv else 0
                issued_deal[0].save()
            return JsonResponse({"success":True, "message":"Bank Reference Number & Issued Deal details Saved"})

        except Exception as e:
            return JsonResponse({'error': _(e.args[0])}, status=status.HTTP_400_BAD_REQUEST)

class DealJsonAttributesList(DealEditBaseView, CompanyAttributesMixin, View):
    permission_required = 'auth.list_mortgage_deals'
    
    def get(self, *args, **kwargs):
        type = self.request.GET.get('type')        
        response = {}
        if type == 'assigned_to':
            response = self.get_company_user_admin_list()

        elif type == 'agents':
            response = self.get_company_agents_list()
        elif type == 'producers':
            response = self.get_company_producers_list()

        return JsonResponse(response, safe=False)


class GetDealDetail(View):
    @staticmethod
    def get(request, *args, **kwargs):
        pk = kwargs.get("pk")
        deal_pk = request.GET.get("deal_id")
        bank_pk = request.GET.get("bank_id")
        attribute = request.GET.get("attribute")
        updated_mortgage_amount = int(request.GET.get("mortgage_amount"))
        if not deal_pk or not bank_pk:
            return JsonResponse({
                "data": "",
                "message": "please provide bank_id and deal_id in query params"
            })
        if attribute == 'monthly_repayment':
            if Deal.objects.filter(pk=deal_pk).exists():
                deal = Deal.objects.get(pk=deal_pk)

            if Bank.objects.filter(pk=bank_pk).exists():
                bank = Bank.objects.bank_info(pk=bank_pk)

            data = BankHelper(bank, deal.property_price, updated_mortgage_amount, deal.tenure, deal.govt_fee.pk, deal = deal)
            Updated_monthly_repayment = data.monthly_repayment
            Updated_land_mortgage_registration = data.land_dep_mortgage_registration
            Updated_bank_processing_fee = data.get_bank_processing_fee
            Updated_life_insurance_monthly = data.get_life_insurance_monthly
            
            return JsonResponse({
                'monthly_repayment' : Updated_monthly_repayment,
                'land_dep_mortgage_registration' : Updated_land_mortgage_registration,
                'bank_processing_fee' : Updated_bank_processing_fee,
                'life_insurance_monthly' : Updated_life_insurance_monthly,
                })
        else:
            return JsonResponse({'error' : 'attribute name is not correct'})