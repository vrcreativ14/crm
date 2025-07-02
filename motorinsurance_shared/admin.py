from django.contrib import admin

from accounts.models import Company
from felix.admin import global_admin
from motorinsurance_shared.admin_form import ProductAdminModelForm
from motorinsurance_shared.models import Product, CarMake, CarModel, CarTrim, AutoQuoterCarTrimData


class ProductModelAdmin(admin.ModelAdmin):
    form = ProductAdminModelForm
    list_display = ['insurer', 'name', 'code', 'companies_using']
    list_filter = ['insurer']
    search_fields = ['name', 'code']
    actions = ['set_inactive']

    def set_inactive(self, request, queryset):
        queryset.update(is_active=False)

    set_inactive.short_description = 'Make selected products inactive'

    def companies_using(self, obj):
        return Company.objects.filter(available_motor_insurance_products=obj).count()

    companies_using.short_description = 'Companies using this product'

    class Media:
        css = {
            'all': ('motorinsurance_shared/css/product-attribute-multi-widget.css',)
        }


class CarTrimModelAdmin(admin.ModelAdmin):
    list_display = ['year', 'model', 'title']
    search_fields = ['model__name', 'title']
    list_filter = ['year', 'model__make']


global_admin.register(Product, ProductModelAdmin)
global_admin.register(CarMake)
global_admin.register(CarModel)
global_admin.register(CarTrim, CarTrimModelAdmin)
global_admin.register(AutoQuoterCarTrimData)
