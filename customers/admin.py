from django.contrib import admin
from felix.admin import tenant_admin
from customers.models import Customer
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin

class CustomerResource(resources.ModelResource):
    class Meta:
        model = Customer

class CustomerAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'company', 'updated_on')
    resource_classes = [CustomerResource]


tenant_admin.register(Customer, CustomerAdmin)