from django.contrib import admin
from felix.admin import tenant_admin
from customers.models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'company', 'updated_on')


tenant_admin.register(Customer, CustomerAdmin)
