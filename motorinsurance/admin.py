from django.contrib import admin

from felix.admin import tenant_admin
from motorinsurance.models import Deal
from motorinsurance.models import Lead
from motorinsurance.models import Quote
from motorinsurance.models import QuotedProduct
from motorinsurance.models import Policy


class MotorQuotedProductAdmin(admin.TabularInline):
    model = QuotedProduct


class MotorQuoteAdmin(admin.ModelAdmin):
    inlines = [
        MotorQuotedProductAdmin
    ]


tenant_admin.register(Quote, MotorQuoteAdmin)
tenant_admin.register(Deal)
tenant_admin.register(Lead)
tenant_admin.register(Policy)
