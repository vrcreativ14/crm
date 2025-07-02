from django.contrib.admin import ModelAdmin

from felix import admin

from auto_quoter.models import AutoQuoterConfig, InsurerApiTransactionLog

admin.tenant_admin.register(AutoQuoterConfig)


class InsurerApiTransactionLogModelAdmin(ModelAdmin):
    list_display = ['insurer', 'deal', 'created_on']
    list_filter = ['insurer']


admin.tenant_admin.register(InsurerApiTransactionLog, InsurerApiTransactionLogModelAdmin)