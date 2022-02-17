from django.db import transaction
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from mortgage.models import *
from customers.models import Customer
from mortgage.forms import BankInterestRateSegmentedForm, MortgageQuoteForm
from mortgage.models import Bank, Deal, Quote, SegmentedRate
from mortgage.serializers import BankSerializer, PeopleSerializer


class PeopleView(View):
    def get(self, request, *args, **kwargs):
        qs = Customer.objects.filter(customer_mortgage_profiles__isnull=False)
        serializer = PeopleSerializer(qs, many=True)
        context = {"data": serializer.data, "entity": "mortgage"}
        return render(request, "mortgage/people_list.html", context)


class SegmentedCustomer(View):
    @staticmethod
    def post(request, *args, **kwargs):
        post_data = request.POST.dict()
        deal = get_object_or_404(Deal, pk=kwargs.get("pk"))
        bank = get_object_or_404(Bank, pk=request.POST.get("banks"))
        # bank = Bank.objects.first()
        quote_instance = None
        if hasattr(deal, 'mortgage_quote_deals'):
            quote_instance = deal.mortgage_quote_deals
        else:
            post_quote_data = {
            "deals": deal,
            "banks":request.POST.getlist('banks')
        }
            form = MortgageQuoteForm(post_quote_data, instance=quote_instance)
            if form.is_valid():
                quote_instance = form.save(commit=False)
            else:
                return JsonResponse({"message": form.errors, "section": "Quote"})
            if not request.POST.get("is_segmented"):
                quote_instance.is_segmented = True
                quote_instance.save()
                quote_instance.bank.add(bank)
                return JsonResponse({"status": "success", "message":"Quote saved"})
        if request.POST.get("is_segmented"):
            post_data['bank'] = bank
            post_data['interest_rate'] = post_data['interest_rate'].replace('%','')
            post_data['post_introduction_rate'] = post_data['post_introduction_rate'].replace('%','')
            form = BankInterestRateSegmentedForm(post_data)
            if form.is_valid():
                instance = BankInterestRate(**form.clean())
                with transaction.atomic():
                    instance.save()
                    quote_instance.is_segmented = True
                    quote_instance.save()
                    quote_instance.bank.add(bank)
                    SegmentedRate.objects.filter(quote=quote_instance, bank=bank).delete()
                    SegmentedRate.objects.create(quote=quote_instance, rate=instance, bank=bank)
                return JsonResponse({"status": "success", "message":"Bank Interest Rate Added"})
            return JsonResponse({"sucess":False, "status":"failed","section":"Bank Interest Rate","message": form.errors})

