from rest_framework import serializers

from insurers.models import Insurer
from motorinsurance.models import Policy
from motorinsurance_shared.models import Product


class InsurerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurer
        fields = ['pk', 'name']


class ProductSerializer(serializers.ModelSerializer):
    insurer = InsurerSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['pk', 'name', 'insurer']


class PolicySerializer(serializers.Serializer):
    status = serializers.CharField(source='get_policy_expiry_status')
    policy_number = serializers.CharField(source='reference_number')
    start_date = serializers.DateField(source='policy_start_date')
    expiry_date = serializers.DateField(source='policy_expiry_date')

    insurer = serializers.SerializerMethodField(method_name='get_insurer')
    product = serializers.SerializerMethodField(method_name='get_product')

    premium = serializers.DecimalField(max_digits=10, decimal_places=2)
    deductible = serializers.DecimalField(max_digits=10, decimal_places=2)

    customer_name = serializers.CharField(source='customer.name')
    customer_email = serializers.CharField(source='customer.email')
    customer_phone = serializers.CharField(source='customer.phone')
    customer_nationality = serializers.CharField(source='customer.get_nationality_display')
    customer_dob = serializers.DateField(source='customer.dob')

    car_year = serializers.IntegerField()
    car_make = serializers.CharField(source='car_make.name')
    car_model_and_trim = serializers.SerializerMethodField(method_name='get_model_and_trim')
    sum_insured = serializers.DecimalField(max_digits=10, decimal_places=2, source='insured_car_value')

    emirate_of_registration = serializers.SerializerMethodField(method_name='get_emirate_of_registration')

    agent_email = serializers.SerializerMethodField(method_name='get_agent_email')
    referrer_email = serializers.SerializerMethodField(method_name='get_referrer_email')

    created_on = serializers.DateTimeField()
    updated_on = serializers.DateTimeField()

    def get_insurer(self, policy):
        if policy.product:
            return InsurerSerializer(policy.product.insurer).data

    def get_product(self, policy):
        if policy.product:
            return ProductSerializer(policy.product).data
        else:
            return {
                'pk': None,
                'name': policy.custom_product_name,
                'insurer': None
            }

    def get_model_and_trim(self, policy):
        return (policy.car_trim and policy.car_trim.get_title_with_model()) or policy.custom_car_name

    def get_emirate_of_registration(self, policy):
        return (policy.deal and policy.deal.get_place_of_registration_display()) or ''

    def get_agent_email(self, policy):
        return (policy.owner and policy.owner.email) or (
                policy.deal and policy.deal.assigned_to and policy.deal.assigned_to.email
        ) or ''

    def get_referrer_email(self, policy):
        return (policy.deal and policy.deal.producer and policy.deal.producer.email) or ''
