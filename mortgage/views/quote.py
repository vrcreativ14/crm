from django.forms import model_to_dict
from datetime import date
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mortgage.forms import MortgageQuoteForm, OrderForm,  CustomerForm
from mortgage.models import Bank, Deal, PreApproval, PostApproval, Quote, Order, SubStage
from mortgage.utils import BankHelper, get_quote_data
from mortgage.constants import *
from mortgage.views.email import StageEmail
from customers.models import Customer


class MortgageQuote(View):
    @staticmethod
    def get(request, *args, **kwargs):
        form = MortgageQuoteForm()
        deal_pk = request.GET.get("deal_id")
        bank_pk = request.GET.get("bank_id")
        bank = deal = None

        if not deal_pk or not bank_pk:
            return JsonResponse({
                "data": "",
                "message": "please provide bank_id and deal_id in query params"
            })

        if Deal.objects.filter(pk=deal_pk).exists():
            deal = Deal.objects.get(pk=deal_pk)

        if Bank.objects.filter(pk=bank_pk).exists():
            bank = Bank.objects.bank_info(pk=bank_pk)

        if not (bank and deal):
            return JsonResponse({"error": "query parameter did not fetch any record"})

        data = BankHelper(bank, deal.property_price, deal.loan_amount, deal.tenure, deal.govt_fee.pk)
        bank_data = {
            "down_payment": data.get_down_payment,
            "bank_processing_fee": data.get_bank_processing_fee,
            "life_insurance_monthly": data.get_life_insurance_monthly,
            "property_insurance_yearly": data.get_property_insurance_yearly,
            "trustee_center_fee_vat": data.trustee_center_fee_vat,
            "land_dep_property_registration": data.land_dep_property_registration,
            "land_dep_mortgage_registration": data.land_dep_mortgage_registration,
            "real_estate_fee_vat": data.real_estate_fee_vat,
            "total_down_payment": data.calculate_total_down_payment,
            "extra_financing": data.calculate_extra_financing,
            "net_down_payment": data.calculate_net_down_payment,
            "loan": data.loan,
            "monthly_repayment": data.monthly_repayment,
        }
        return JsonResponse({"data": bank_data})

    @staticmethod
    def post(request, *args, **kwargs):
        post_data = request.POST.dict()
        post_data["banks"] = request.POST.getlist("banks")
        deal = get_object_or_404(Deal, pk=request.POST.get("deals"))
        quote_instance = None

        if hasattr(deal, "mortgage_quote_deals"):
            quote_instance = deal.mortgage_quote_deals
        form = MortgageQuoteForm(post_data, instance=quote_instance)
        if form.is_valid():
            quote = form.save()
            deal.stage = "quote"
            deal.status = STATUS_US
            deal.save()
            if post_data.get("remove"):
                quote.bank.clear()
            quote.bank.add(*form.cleaned_data.get("banks"))
            return JsonResponse({"status": "ok"})

        return JsonResponse({"status": "failed", "message": form.errors})


def quote_info(pk):
    quote = get_object_or_404(Quote, pk=pk)
    data = get_quote_data(quote)
    deal = quote.deals
    quote_dict = quote
    return {
        "status": "ok",
        "data": {
            "quote_details": data,
            "customer_info": deal.customer,
            "deal_info": deal,
            "quote_info": quote_dict,
        },
    }


class QuoteAPI(View):
    @staticmethod
    def get(request, *args, **kwargs):
        pk = kwargs.get("pk")
        deal = get_object_or_404(Deal, pk=pk)
        sub_stage = ''
        if hasattr(deal, 'current_sub_stage'):
            if(deal.current_sub_stage):
                sub_stage = model_to_dict(deal.current_sub_stage)
        deal_bank = ''
        if hasattr(deal, 'deal_bank'):
            deal_bank = deal.deal_bank.bank.pk
        quote = deal.mortgage_quote_deals
        data = get_quote_data(quote)
        deal = quote.deals
        quote_dict = model_to_dict(quote)
        quote_dict.pop("bank")

        return JsonResponse(
            {
                "status": "ok",
                "data": {
                    "quote_details": data,
                    "customer_info": model_to_dict(deal.customer),
                    "deal_info": model_to_dict(deal),
                    "quote_info": quote_dict,
                    "sub_stage": sub_stage,
                    "deal_bank": deal_bank,
                },
            }
        )


class StagePropagateView(View):
    permission_required = "auth.update_mortgage_deals"

    def post(self, request, *args, **kwargs):
        order, create_sub_stage = None, False
        deal = get_object_or_404(Deal, pk=request.POST.get("deal"))
        post_data = request.POST.dict()
        stage = post_data.pop("stage", None)
        stage = deal.stage
        message = "Stage Updated"
        post_data["policy_start_date"] = date.today()
        valid_stage = False

        customer_form = CustomerForm(post_data)

        if hasattr(deal, "deal_bank"):
            order = deal.deal_bank
            message = "Order Updated"

        if stage == STAGE_QUOTE:
            if not deal.customer.email:
                if customer_form.is_valid():
                    Customer.objects.filter(pk=deal.customer.pk).update(**customer_form.cleaned_data)
                else:
                    return JsonResponse(
                    {
                        "success": False,
                        "errors": "Please update customer email first",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            valid_stage = True
            if request.POST.get('bank'):
                bank = get_object_or_404(Bank, pk=request.POST.get("bank"))
                post_data["bank"] = bank
                form = OrderForm(post_data, instance=order)
                if form.is_valid():
                    form.save()
                    deal.status = STATUS_US
                else:
                    return JsonResponse(
                        {
                            "success": False,
                            "errors": form.errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                deal.stage = STAGE_PREAPPROVAL
                create_sub_stage = WAIT_PREAPPROVAL_DOC

        elif stage == STAGE_PREAPPROVAL:
            # if ((not PreApproval.objects.filter(deal=deal)) and (not PostApproval.objects.filter(deal=deal))):
            #     if hasattr(deal, "deal_bank"):
            #         return JsonResponse(
            #         {
            #             "success": False,
            #             "errors": "Please upload the Pre Approval documents.",
            #         },
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )

            valid_stage = True
            deal.stage = STAGE_VALUATION
            deal.status = STATUS_CLIENT
            create_sub_stage = WAITING_FOR_VALUATION_DOCUMENTS


        elif stage == STAGE_VALUATION:
            valid_stage = True
            deal.status = STATUS_BANK
            deal.stage = STAGE_FINAL_OFFER
            create_sub_stage = FOL_REQUESTED_FROM_BANK


        elif stage == STAGE_FINAL_OFFER:
            valid_stage = True
            deal.status = STATUS_ACTIVE
            deal.stage = STAGE_LOAN_DISBURSAL


        elif stage == STAGE_LOAN_DISBURSAL:
            valid_stage = True
            deal.stage = STAGE_PROPERTY_TRANSFER
            create_sub_stage = SUB_SETTLEMENT


        elif stage == STAGE_PROPERTY_TRANSFER:
            valid_stage = True
            deal.stage = STAGE_ClosedWON or STAGE_ClosedLOST

        if not valid_stage:
            return JsonResponse(
                {"success": False, "errors": "Invalid stage"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        deal.save()
        deal.refresh_from_db()
        if create_sub_stage and not deal.current_sub_stage:
            SubStage.objects.create(deal=deal, stage=deal.stage, sub_stage=create_sub_stage)
        # send_email = StageEmail(deal)
        # send_email.stage_propagation_email(stage=True)
        return JsonResponse(
            {
                "success": True,
                "message": message,
            },
            status=status.HTTP_201_CREATED,
        )

class SubStageToggle(View):
    permission_required = "auth.update_mortgage_deals"

    def post(self, request, *args, **kwargs):
        deal = get_object_or_404(Deal, pk=request.POST.get("deal"))
        sub_stage = deal.current_sub_stage
        
        if not sub_stage:
            return JsonResponse(
            {
                "success": False,
                "error": "Please Contact Admin",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        if deal.stage == STAGE_QUOTE:
            if sub_stage.sub_stage == SELECT_BANK:
                sub_stage.sub_stage = CONFIRM_BANK
            else:
                sub_stage.sub_stage = SELECT_BANK
        elif deal.stage == STAGE_PREAPPROVAL:
            if sub_stage.sub_stage == WAIT_PREAPPROVAL_DOC:
                sub_stage.sub_stage = SENT_TO_BANK_FOR_PREAPPROVAL
            else:
                sub_stage.sub_stage = WAIT_PREAPPROVAL_DOC

        elif deal.stage == STAGE_VALUATION:
            if sub_stage.sub_stage == WAITING_FOR_VALUATION_DOCUMENTS:
                sub_stage.sub_stage = SENT_TO_BANK_FOR_APPROVAL
            else:
                sub_stage.sub_stage = WAITING_FOR_VALUATION_DOCUMENTS

        elif deal.stage == STAGE_FINAL_OFFER:
            if sub_stage.sub_stage == FOL_REQUESTED_FROM_BANK:
                sub_stage.sub_stage = FOL_SIGNED
            else:
                sub_stage.sub_stage = FOL_REQUESTED_FROM_BANK

        elif deal.stage == STAGE_PROPERTY_TRANSFER:
            change_sub_stage = request.POST.get('change_sub_stage')
            to_sub_stage = SUB_SETTLEMENT
            if change_sub_stage == '1':
                to_sub_stage = SUB_SETTLEMENT
            elif change_sub_stage == '2':
                to_sub_stage = SUB_PROPERTY_TRANSFER
            elif change_sub_stage == '3':
                to_sub_stage = SUB_PAYMENT
            sub_stage.sub_stage = to_sub_stage

        sub_stage.save()
        return JsonResponse(
            {
                "success": True,
                "message": "Sub Stage Updated",
            },
            status=status.HTTP_201_CREATED,
        )
