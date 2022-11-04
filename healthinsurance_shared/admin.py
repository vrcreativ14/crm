from django.contrib import admin
from healthinsurance_shared.admin_form import ProductAdminModelForm
from .models import *
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin


class NetworkAdmin(admin.ModelAdmin):
    search_fields = ['network']

class PhysiotherapyAdmin(admin.ModelAdmin):
    search_fields = ['sessions']

class AlternativeMedicineAdmin(admin.ModelAdmin):
    search_fields = ['medicine']

class MaternityBenefitsAdmin(admin.ModelAdmin):
    search_fields = ['benefit']

class AnnualLimitAdmin(admin.ModelAdmin):
    search_fields = ['limit']

class DentalBenefitAdmin(admin.ModelAdmin):
    search_fields = ['benefit']

class ConsultationCopayAdmin(admin.ModelAdmin):
    search_fields = ['copayment']

class DiagnosticsCopayAdmin(admin.ModelAdmin):
    search_fields = ['copayment']

class PharmacyCopayAdmin(admin.ModelAdmin):
    search_fields = ['copayment']

class PreExistingCoverAdmin(admin.ModelAdmin):
    search_fields = ['cover']


class MessageTemplatesResource(resources.ModelResource):
    class Meta:
        model = MessageTemplates

class MessageTemplatesAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    resource_classes = [MessageTemplatesResource]

class MessageTypeResource(resources.ModelResource):
    class Meta:
        model = MessageType

class MessageTypeAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    resource_classes = [MessageTypeResource]


class InsurerResource(resources.ModelResource):
    class Meta:
        model = Insurer

class InsurerAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    resource_classes = [InsurerResource]


class PlanResource(resources.ModelResource):
    class Meta:
        model = Plan

class PlanAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    form = ProductAdminModelForm
    def is_active(self, obj):
        return obj.is_active
    is_active.short_description = 'Status'
    search_fields = ['insurer__name','name','display_name','code']
    autocomplete_fields = ['network','annual_limit','dental_benefits','physiotherapy','alternative_medicine','consultation_copay','diagnostics_copay','pharmacy_copay','pre_existing_cover']
    list_display = ['insurer', 'name', 'code','is_active']
    list_filter = ['is_active']
    resource_classes = [PlanResource]
    # class Media:
    #         css = {
    #         'all': ('healthinsurance_shared/css/product-attribute-multi-widget.css',)
    #     }

admin.site.register(Area_Of_Cover)
admin.site.register(DiagnosticsCopay,DiagnosticsCopayAdmin)
admin.site.register(Deductible)
admin.site.register(Network, NetworkAdmin)
admin.site.register(TPA)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Insurer, InsurerAdmin)
admin.site.register(InsurerDetails)
admin.site.register(AnnualLimit, AnnualLimitAdmin)
admin.site.register(Physiotherapy, PhysiotherapyAdmin)
admin.site.register(PreExistingCover, PreExistingCoverAdmin)
admin.site.register(AlternativeMedicine, AlternativeMedicineAdmin)
admin.site.register(MaternityBenefits)
admin.site.register(MaternityWaitingPeriod)
admin.site.register(DentalBenefit, DentalBenefitAdmin)
admin.site.register(WellnessBenefit)
admin.site.register(OpticalBenefit)
admin.site.register(PaymentFrequency)
admin.site.register(Emirate)
admin.site.register(ConsultationCopay,ConsultationCopayAdmin)
admin.site.register(PharmacyCopay,PharmacyCopayAdmin)
admin.site.register(VisaCategory)
admin.site.register(MessageTemplates, MessageTemplatesAdmin)
admin.site.register(MessageType, MessageTypeAdmin)