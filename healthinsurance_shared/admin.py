from django.contrib import admin
from healthinsurance_shared.admin_form import ProductAdminModelForm, InsurerAdminForm
from .models import *
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin


class MessageTemplatesResource(resources.ModelResource):
    class Meta:
        model = MessageTemplates

class MessageTypeResource(resources.ModelResource):
    class Meta:
        model = MessageType

class InsurerResource(resources.ModelResource):
    class Meta:
        model = Insurer

class InsurerDetailsResource(resources.ModelResource):
    class Meta:
        model = InsurerDetails

class NetworkResource(resources.ModelResource):
    class Meta:
        model = Network

class PhysiotherapyResource(resources.ModelResource):
    class Meta:
        model = Physiotherapy

class AlternativeMedicineResource(resources.ModelResource):
    class Meta:
        model = AlternativeMedicine

class MaternityBenefitsResource(resources.ModelResource):
    class Meta:
        model = MaternityBenefits

class MaternityWaitingPeriodResource(resources.ModelResource):
    class Meta:
        model = MaternityWaitingPeriod

class Area_Of_CoverResource(resources.ModelResource):
    class Meta:
        model = Area_Of_Cover

class AnnualLimitResource(resources.ModelResource):
    class Meta:
        model = AnnualLimit

class DentalBenefitResource(resources.ModelResource):
    class Meta:
        model = DentalBenefit

class OpticalBenefitResource(resources.ModelResource):
    class Meta:
        model = OpticalBenefit

class WellnessBenefitResource(resources.ModelResource):
    class Meta:
        model = WellnessBenefit

class ConsultationCopayResource(resources.ModelResource):
    class Meta:
        model = ConsultationCopay

class DiagnosticsCopayResource(resources.ModelResource):
    class Meta:
        model = DiagnosticsCopay

class PharmacyCopayResource(resources.ModelResource):
    class Meta:
        model = PharmacyCopay

class PaymentFrequencyResource(resources.ModelResource):
    class Meta:
        model = PaymentFrequency

class PreExistingCoverResource(resources.ModelResource):
    class Meta:
        model = PreExistingCover
        
class TPAResource(resources.ModelResource):
    class Meta:
        model = TPA

class VisaCategoryResource(resources.ModelResource):
    class Meta:
        model = VisaCategory

class InpatientDeductibleResource(resources.ModelResource):
    class Meta:
        model = InpatientDeductible


class InpatientDeductibleAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['deductible']
    resource_classes = [InpatientDeductibleResource]

class NetworkAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['network']
    resource_classes = [NetworkResource]

class PhysiotherapyAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['sessions']
    resource_classes = [PhysiotherapyResource]

class AlternativeMedicineAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['medicine']
    resource_classes = [AlternativeMedicineResource]

class MaternityBenefitsAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['benefit']
    resource_classes = [MaternityBenefitsResource]

class MaternityWaitingPeriodAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['period']
    resource_classes = [MaternityWaitingPeriodResource]

class Area_Of_CoverAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['area']
    resource_classes = [Area_Of_CoverResource]

class TPAAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):    
    resource_classes = [TPAResource]

class AnnualLimitAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['limit']
    resource_classes = [AnnualLimitResource]

class DentalBenefitAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['benefit']
    resource_classes = [DentalBenefitResource]

class OpticalBenefitAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['benefit']
    resource_classes = [OpticalBenefitResource]

class WellnessBenefitAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['benefit']
    resource_classes = [WellnessBenefitResource]

class ConsultationCopayAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['copayment']
    resource_classes = [ConsultationCopayResource]

class DiagnosticsCopayAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['copayment']
    resource_classes = [DiagnosticsCopayResource]

class PharmacyCopayAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['copayment']
    resource_classes = [PharmacyCopayResource]

class PaymentFrequencyAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['frequency']
    resource_classes = [PaymentFrequencyResource]

class PreExistingCoverAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    search_fields = ['cover']
    resource_classes = [PreExistingCoverResource]

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

class InsurerAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    form = InsurerAdminForm
    resource_classes = [InsurerResource]

class InsurerDetailsAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):    
    resource_classes = [InsurerDetailsResource]

class MessageTypeAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    resource_classes = [MessageTypeResource]

class MessageTemplatesAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    resource_classes = [MessageTemplatesResource]

class VisaCategoryAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    resource_classes = [VisaCategoryResource]


admin.site.register(Area_Of_Cover, Area_Of_CoverAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(TPA, TPAAdmin)
admin.site.register(Plan, PlanAdmin)
admin.site.register(Insurer, InsurerAdmin)
admin.site.register(InsurerDetails, InsurerDetailsAdmin)
admin.site.register(AnnualLimit, AnnualLimitAdmin)
admin.site.register(Physiotherapy, PhysiotherapyAdmin)
admin.site.register(PreExistingCover, PreExistingCoverAdmin)
admin.site.register(AlternativeMedicine, AlternativeMedicineAdmin)
admin.site.register(MaternityBenefits, MaternityBenefitsAdmin)
admin.site.register(MaternityWaitingPeriod, MaternityWaitingPeriodAdmin)
admin.site.register(DentalBenefit, DentalBenefitAdmin)
admin.site.register(WellnessBenefit, WellnessBenefitAdmin)
admin.site.register(OpticalBenefit, OpticalBenefitAdmin)
admin.site.register(PaymentFrequency, PaymentFrequencyAdmin)
admin.site.register(Emirate)
admin.site.register(ConsultationCopay,ConsultationCopayAdmin)
admin.site.register(DiagnosticsCopay,DiagnosticsCopayAdmin)
admin.site.register(PharmacyCopay,PharmacyCopayAdmin)
admin.site.register(InpatientDeductible,InpatientDeductibleAdmin)
admin.site.register(VisaCategory, VisaCategoryAdmin)
admin.site.register(MessageTemplates, MessageTemplatesAdmin)
admin.site.register(MessageType, MessageTypeAdmin)
admin.site.register(Currency)