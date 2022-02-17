from django.shortcuts import render
from django.views.generic import View


class MortgageLead(View):
    @staticmethod
    def get(request):
        return render(request, "mortgage/lead/mortgage_lead.html", {})

