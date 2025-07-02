from django.db import transaction
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import UpdateView, View
from django.contrib import messages

from mortgage.forms import BankForm, BankInterestRateForm, CreateBankForm, EiborForm, GovtForm, EiborPostForm
from mortgage.models import Bank, Eibor, BankInterestRate, GovernmentFee, EiborPost
from mortgage.serializers import BankListSerializer, BankSerializer

from django.shortcuts import get_object_or_404


class MortgageBank(View):
    def get(self, request, *args, **kwargs):
        form = CreateBankForm()
        banks = Bank.objects.all()
        serializer = BankListSerializer(banks, many=True)

        if self.request.is_ajax():
            return JsonResponse({"banks": serializer.data})

        serializer = BankSerializer(banks, many=True)

        context = {
            "deal": Bank.objects.last(),
            "entity": "mortgage",
            "form": form,
            "banks": serializer.data,
            "bankInterestRate": BankInterestRate.objects.all(),
            "eibor_form": EiborForm(instance=Eibor.objects.last()),
            "eibor_post_form": EiborPostForm(instance=EiborPost.objects.last()),
            "govt_fee_form": GovtForm(instance=GovernmentFee.objects.last()),
            "banks_full": Bank.objects.all()
        }
        template_name = "mortgage/banks/banks_list.html"
        return render(request, template_name, context)

    def post(self, request, *args, **kwargs):
        bank_interest_inst = None
        bank__instance = None


        if kwargs.get("pk"):
            bank__instance = Bank.objects.get(pk=kwargs.get("pk"))
            if bank__instance.bank_interest_rates.all():
                bank_interest_inst = bank__instance.bank_interest_rates.get(is_default=True)
        form = BankInterestRateForm(self.request.POST, instance=bank_interest_inst)

        if form.is_valid():
            interest_rate = form.save(commit=False)
        else:
            return JsonResponse({"errors": form.errors})

        form = BankForm(self.request.POST, self.request.FILES, instance=bank__instance)
        if form.is_valid():
            bank = form.save(commit=False)
            with transaction.atomic():
                bank.save()
                interest_rate.bank = bank

                if interest_rate.eibor_duration == "0M":
                    interest_rate.eibor_rate = Eibor.objects.get().eibor_rate_0m
                if interest_rate.eibor_duration == "1M":
                    interest_rate.eibor_rate = Eibor.objects.get().eibor_rate_1m
                if interest_rate.eibor_duration == "3M":
                    interest_rate.eibor_rate = Eibor.objects.get().eibor_rate_3m
                if interest_rate.eibor_duration == "6M":
                    interest_rate.eibor_rate = Eibor.objects.get().eibor_rate_6m

                if interest_rate.eibor_post_duration == "0M":
                    interest_rate.eibor_post_rate = EiborPost.objects.get().eibor_post_rate_0m
                if interest_rate.eibor_post_duration == "1M":
                    interest_rate.eibor_post_rate = EiborPost.objects.get().eibor_post_rate_1m
                if interest_rate.eibor_post_duration == "3M":
                    interest_rate.eibor_post_rate = EiborPost.objects.get().eibor_post_rate_3m
                if interest_rate.eibor_post_duration == "6M":
                    interest_rate.eibor_post_rate = EiborPost.objects.get().eibor_post_rate_6m
                interest_rate.save()

            if not self.request.is_ajax():
                return HttpResponseRedirect(reverse("mortgage:banks"))

            return JsonResponse(
                {"message": "bank_created", "bank": BankSerializer(bank).data}
            )

        return JsonResponse({"errors": form.errors})

    def delete(self, request):
        bank = get_object_or_404(Bank, pk=request.GET.get('bank'))
        bank.delete()
        return JsonResponse({"status": "ok", "message": "Bank deleted"})


class EiborView(View):
    def post(self, request, *rag, **kwargs):
        post_data = request.POST.dict()
        eibor = Eibor.objects.first()
        form = EiborForm(post_data, instance=eibor)
        if form.is_valid():
            eibor = form.save()
        else:
            return JsonResponse({"success": False, "errors": form.errors})
        if post_data.get("banks") == "all":
            qs = BankInterestRate.objects.all()
        else:
            qs = BankInterestRate.objects.filter(bank__pk__in=request.POST.getlist('banks'))
        qs.filter(eibor_duration="6M").update(eibor_rate=request.POST.get('eibor_rate_6m'))
        qs.filter(eibor_duration="3M").update(eibor_rate=request.POST.get('eibor_rate_3m'))
        qs.filter(eibor_duration="1M").update(eibor_rate=request.POST.get('eibor_rate_1m'))
        qs.filter(eibor_duration="0M").update(eibor_rate=request.POST.get('eibor_rate_0m'))
        return HttpResponseRedirect(reverse("mortgage:banks"))


class EiborPostView(View):
    def post(self, request, *rag, **kwargs):
        post_data = request.POST.dict()
        eibor_post = EiborPost.objects.first()
        form = EiborPostForm(post_data, instance=eibor_post)
        if form.is_valid():
            eibor_post = form.save()
        else:
            return JsonResponse({"success": False, "errors": form.errors})
        if post_data.get("banks") == "all":
            qs = BankInterestRate.objects.all()
        else:
            qs = BankInterestRate.objects.filter(bank__pk__in=request.POST.getlist('banks'))
        qs.filter(eibor_post_duration="6M").update(eibor_post_rate=request.POST.get('eibor_post_rate_6m'))
        qs.filter(eibor_post_duration="3M").update(eibor_post_rate=request.POST.get('eibor_post_rate_3m'))
        qs.filter(eibor_post_duration="1M").update(eibor_post_rate=request.POST.get('eibor_post_rate_1m'))
        qs.filter(eibor_post_duration="0M").update(eibor_post_rate=request.POST.get('eibor_post_rate_0m'))

        return HttpResponseRedirect(reverse("mortgage:banks"))


class GovernmentFeeView(View):

    def post(self, request, *rag, **kwargs):
        post_data = request.POST.dict()
        government_fee = GovernmentFee.objects.last()
        government_fee.trustee_center_fee = float(post_data['trustee_center_fee'])
        government_fee.property_fee_rate = float(post_data['property_fee_rate'])
        government_fee.property_fee_addition = int(float(post_data['property_fee_addition']))
        government_fee.mortgage_fee_rate = float(post_data['mortgage_fee_rate'])
        government_fee.mortgage_fee_addition = int(float(post_data['mortgage_fee_addition']))
        government_fee.real_state_fee = float(post_data['real_state_fee'])
        government_fee.save()
        # form = GovtForm(post_data)
        # if form.is_valid():
        #     form.save()
        # messages.add_message(request, level=1, message="ok")
        return HttpResponseRedirect(reverse("mortgage:banks"))

