from pyexpat import model
from attr import field, fields
from rest_framework import serializers
from healthinsurance.models.deal import AdditionalMember, Deal, PrimaryMember
from healthinsurance.models.policy import HealthPolicy
from healthinsurance.models.quote import QuotedPlan
from healthinsurance_shared.models import *

class AreaofCoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area_Of_Cover
        fields = '__all__'

class ConsultationCopaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationCopay
        fields = '__all__'

class DiagnosticsCopaySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticsCopay
        fields = '__all__'

class PharmacyCopaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyCopay
        fields = '__all__'

class DeductibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = InpatientDeductible
        fields = '__all__'

class AnnualLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnualLimit
        fields = '__all__'

class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = '__all__'

class PhysiotherapySerializer(serializers.ModelSerializer):
    class Meta:
        model = Physiotherapy
        fields = '__all__'

class PaymentFrequencySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentFrequency
        fields = '__all__'

class AlternativeMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlternativeMedicine
        fields = '__all__'

class DentalBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DentalBenefit
        fields = '__all__'

class OpticalBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpticalBenefit
        fields = '__all__'

class WellnessBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellnessBenefit
        fields = '__all__'

class MaternityBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaternityBenefits
        fields = '__all__'

class MaternityWaitingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaternityWaitingPeriod
        fields = '__all__'

class PreExistingCoverSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreExistingCover
        fields = '__all__'

class InpatientDeductibleSerializer(serializers.ModelSerializer):
    class Meta:
        model = InpatientDeductible
        fields = '__all__'

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'

class QuotedPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotedPlan
        fields = '__all__'

class PlanSerializer(serializers.ModelSerializer):
    area_of_cover = serializers.SerializerMethodField()
    consultation_copay = serializers.SerializerMethodField()
    diagnostics_copay = serializers.SerializerMethodField()    
    pharmacy_copay = serializers.SerializerMethodField()    
    annual_limit = serializers.SerializerMethodField()
    network = serializers.SerializerMethodField()
    physiotherapy = serializers.SerializerMethodField()
    payment_frequency = serializers.SerializerMethodField()
    alternative_medicine = serializers.SerializerMethodField()
    dental_benefits = serializers.SerializerMethodField()
    optical_benefits = serializers.SerializerMethodField()
    wellness_benefits = serializers.SerializerMethodField()
    maternity_benefits = serializers.SerializerMethodField()
    maternity_waiting_period = serializers.SerializerMethodField()
    pre_existing_cover = serializers.SerializerMethodField()
    inpatient_deductible = serializers.SerializerMethodField()
    currencies = serializers.SerializerMethodField()
    
    def get_area_of_cover(self, instance):
        qs = instance.area_of_cover.all().order_by('area')
        return AreaofCoverSerializer(qs, many = True).data

    def get_consultation_copay(self, instance):
        qs = instance.consultation_copay.all().order_by('copayment')
        return ConsultationCopaySerializer(qs, many = True).data

    def get_diagnostics_copay(self, instance):
        qs = instance.diagnostics_copay.all().order_by('copayment')
        return DiagnosticsCopaySerializer(qs, many = True).data

    def get_pharmacy_copay(self, instance):
        qs = instance.pharmacy_copay.all().order_by('copayment')
        return PharmacyCopaySerializer(qs, many = True).data

    def get_annual_limit(self, instance):
        qs = instance.annual_limit.all().order_by('limit')
        return AnnualLimitSerializer(qs, many = True).data
    
    def get_network(self, instance):
        qs = instance.network.all().order_by('network')     #query_set
        return NetworkSerializer(qs, many = True).data

    def get_physiotherapy(self, instance):
        qs = instance.physiotherapy.all().order_by('sessions')
        return PhysiotherapySerializer(qs, many = True).data

    def get_payment_frequency(self, instance):
        qs = instance.payment_frequency.all().order_by('frequency')
        return PaymentFrequencySerializer(qs, many = True).data

    def get_alternative_medicine(self, instance):
        qs = instance.alternative_medicine.all().order_by('medicine')
        return AlternativeMedicineSerializer(qs, many = True).data

    def get_dental_benefits(self, instance):
        qs = instance.dental_benefits.all().order_by('benefit')
        return DentalBenefitSerializer(qs, many = True).data

    def get_optical_benefits(self, instance):
        qs = instance.optical_benefits.all().order_by('benefit')
        return OpticalBenefitSerializer(qs, many = True).data

    def get_wellness_benefits(self, instance):
        qs = instance.wellness_benefits.all().order_by('benefit')
        return WellnessBenefitSerializer(qs, many = True).data

    def get_maternity_benefits(self, instance):
        qs = instance.maternity_benefits.all().order_by('benefit')
        return MaternityBenefitSerializer(qs, many = True).data

    def get_maternity_waiting_period(self, instance):
        qs = instance.maternity_waiting_period.all().order_by('period')
        return MaternityWaitingPeriodSerializer(qs, many = True).data

    def get_pre_existing_cover(self, instance):
        qs = instance.pre_existing_cover.all().order_by('cover')
        return PreExistingCoverSerializer(qs, many = True).data

    def get_inpatient_deductible(self, instance):
        qs = instance.inpatient_deductible.all().order_by('deductible')
        return InpatientDeductibleSerializer(qs, many = True).data
    
    def get_currencies(self, instance):
        qs = instance.currencies.all().order_by('name')
        return CurrencySerializer(qs, many = True).data

    class Meta:
        model = Plan
        exclude = ('logo',)


class AdditionalMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalMember
        fields = '__all__'

class PrimaryMemberSerializer(serializers.ModelSerializer):
    additional_members = AdditionalMemberSerializer(many = True, read_only=True)
    class Meta:
        model = PrimaryMember
        fields = '__all__'

class DealSerializer(serializers.ModelSerializer):
    primary_member = PrimaryMemberSerializer(read_only=True)
    class Meta:
        model = Deal
        fields = '__all__'

class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthPolicy
        fields = '__all__'