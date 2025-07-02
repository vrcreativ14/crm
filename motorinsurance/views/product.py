from django.http.response import JsonResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from motorinsurance_shared.models import Product
from motorinsurance.models import QuotedProduct


class ProductAddonListView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            product = Product.objects.get(pk=kwargs['pk'])
            response = {'success': True, 'addons': product.get_add_ons()}
        except Product.DoesNotExist:
            response = {'success': False}

        return JsonResponse(response)


class QuotedProductAddonListView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            qp = QuotedProduct.objects.get(pk=kwargs['pk'])
            response = {'success': True, 'addons': qp.product.get_add_ons()}
        except QuotedProduct.DoesNotExist:
            response = {'success': False}

        return JsonResponse(response)
