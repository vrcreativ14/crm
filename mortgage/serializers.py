import base64
from pyexpat import model

from jmespath import search
from customers.models import Customer

from django.contrib.auth.models import User
from django.contrib.postgres import fields
from rest_framework import serializers
from mortgage.models import Bank, Deal, Order, IssuedDeal
from datetime import datetime


class BankListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ["bank_id", "name", "logo"]


class BankSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField("get_image")
    # eibor_rate = serializers.SerializerMethodField("get_eibor_rate")
    # eibor_duration = serializers.SerializerMethodField("get_eibor_duration")
    interest_rate = serializers.SerializerMethodField("get_interest_rate")
    eibor_post_duration = serializers.SerializerMethodField("get_eibor_post_duration")
    
    introduction_period_in_years = serializers.SerializerMethodField(
        "get_introduction_period_in_years"
    )
    post_introduction_rate = serializers.SerializerMethodField(
        "get_post_introduction_rate"
    )

    def get_image(self, obj):
        try:
            image_path = obj.logo.path
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
                image = image_data
            return image
        except:
            print("error")
            return True

    def get_interest_rate(self, obj):
        try:
            return obj.bank_interest_rates.get(is_default=True).interest_rate
        except:
            return ""

    def get_introduction_period_in_years(self, obj):
        try:
            return obj.bank_interest_rates.get(
                is_default=True
            ).introduction_period_in_years
        except:
            return ""

    def get_post_introduction_rate(self, obj):
        try:
            return obj.bank_interest_rates.get(is_default=True).post_introduction_rate
        except:
            return ""

    def get_eibor_post_duration(self, obj):
        try:
            return obj.bank_interest_rates.get(is_default=True).eibor_post_duration
        except:
            return ""

    
    # def get_eibor_rate(self, obj):
    #     try:
    #         return obj.bank_interest_rates.get(
    #             is_default=True
    #         ).eibor_rate
    #     except:
    #         return ""

    
    # def get_eibor_duration(self, obj):
    #     try:
    #         return obj.bank_interest_rates.get(
    #             is_default=True
    #         ).eibor_duration
    #     except:
    #         return ""

    
    class Meta:
        model = Bank
        fields = [
            "image",
            "bank_id",
            "name",
            "logo",
            "interest_rate",
            # "eibor_rate",
            "introduction_period_in_years",
            "eibor_post_duration",
            "post_introduction_rate",
            "property_valuation_fee",
            "bank_processing_fee_rate",
            # "bank_processing_fee_extra",
            # "max_bank_processing_fee",
            "life_insurance_monthly_rate",
            "property_insurance_yearly_rate",
            "full_settlement_percentage",
            "full_settlement_max_value",
            "free_partial_payment_per_year",
        ]


class PeopleSerializer(serializers.ModelSerializer):
    updated_on = serializers.SerializerMethodField('get_updated_on')
    created_on = serializers.SerializerMethodField('get_created_on')
    entity = serializers.SerializerMethodField('get_entity')

    def get_updated_on(self, obj):
        return obj.updated_on.strftime("%b %d, %Y")

    def get_created_on(self, obj):
        return obj.created_on.strftime("%b %d, %Y")

    def get_entity(self, obj):
        return "mortgage"

    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "entity", "nationality", "updated_on", "created_on")


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField('get_role')

    def get_role(self, obj):
        if hasattr(obj, "userprofile"):
            return obj.userprofile.get_assigned_role()
        return ''

    class Meta:
        model = User
        fields = ('username', 'id', 'role')

class IssuedDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssuedDeal
        fields = ('property_price','loan_amount','tenure', 'l_tv')


class OrderSerializer(serializers.ModelSerializer):    
    bank = serializers.SerializerMethodField("get_bank")
    class Meta:
        model = Order
        fields = ('bank','bank_reference_number')
    
    def get_bank(self, obj):
        try:
            if obj:
                if obj.bank:
                    return obj.bank.name
            else:
                return ""
        except:
            return ""



class DealSerializer(serializers.ModelSerializer):
    order = serializers.SerializerMethodField("get_order")
    issued = serializers.SerializerMethodField("get_issued_deal")
    customer = serializers.SerializerMethodField("get_customer")
    created_date = serializers.SerializerMethodField("get_created_date")
    updated_on = serializers.SerializerMethodField("get_updated_on")
    class Meta:
        model = Deal
        fields = ('property_price','status','created_date','customer', 'updated_on','order','issued')
    def get_customer(self, obj):
        
        if obj.customer:
            return obj.customer.name
        else:
            return ""
        
    def get_order(self, obj):
        orders = Order.objects.filter(deal=obj.pk)        
        return OrderSerializer(orders, many = True).data
    
    def get_issued_deal(self, obj):
        issued_deals = IssuedDeal.objects.filter(deal=obj.pk)   
        return IssuedDealSerializer(issued_deals, many = True).data
    
    def get_created_date(self, obj):
        created_date = obj.created_date        
        year = datetime.strftime(created_date, '%Y')
        day = datetime.strftime(created_date, '%d')
        month = datetime.strftime(created_date, '%b')
        return month + " " + day + ", " + year

    def get_updated_on(self, obj):
        updated_on = obj.updated_on
        year = datetime.strftime(updated_on, '%Y')
        day = datetime.strftime(updated_on, '%d')
        month = datetime.strftime(updated_on, '%b')
        return month + " " + day + ", " + year

    

