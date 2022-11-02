from pyexpat import model
from django import forms
from models.deal import *
from models.quote import *
from felix.constants import FIELD_LENGTHS, GENDER_CHOICES, MARITAL_STATUS_LIST
from core.custom_fields import MoneyField
from core.utils import add_empty_choice

class DealForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'required' : 'True' }), required=True)
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect)
    additional_members = forms.ModelMultipleChoiceField(queryset=AdditionalMember.objects.all())
    #prima
    class Meta:
        model = Deal
        fields = '__all__'

class DealSaveForm(forms.ModelForm):
    primary_member = forms.ModelChoiceField(queryset=PrimaryMember.objects.all())
    class Meta:
        model = Deal
        fields = '__all__'

class PrimaryMemberForm(forms.ModelForm):
    class Meta:
        model = PrimaryMember
        exclude = ('additional_members',)


# class MotorInsuranceQuotedProductForm(forms.ModelForm):
#     class ProductModelChoiceField(forms.ModelChoiceField):
#         def label_from_instance(self, obj):
#             return obj.name

#     product = ProductModelChoiceField(
#         queryset=Plan.objects.none(), widget=forms.Select(attrs={'class': 'product-field sorted'})
#     )

#     premium = MoneyField(
#         widget=forms.TextInput(attrs={'class': 'form-control auto-format-money-field'})
#     )

#     sale_price = MoneyField(
#         widget=forms.TextInput(attrs={'class': 'form-control auto-format-money-field'}),
#         required=True
#     )

#     deductible = MoneyField(
#         widget=forms.TextInput(attrs={'class': 'form-control auto-format-money-field'}),
#         required=True
#     )

#     insured_car_value = MoneyField(
#         widget=forms.TextInput(attrs={'class': 'form-control auto-format-money-field'}),
#         required=False
#     )

#     insurer_quote_reference = MoneyField(
#         widget=forms.TextInput(attrs={'class': 'form-control'}), required=False
#     )

#     def __init__(self, **kwargs):
#         company = kwargs.pop('company')

#         super(MotorInsuranceQuotedProductForm, self).__init__(**kwargs)

#         self.fields['product'].queryset = company.available_motor_insurance_products.all()

#     class Meta:
#         model = QuotedPlan
#         fields = ('product', 'agency_repair', 'premium', 'deductible', 'deductible_extras', 'insured_car_value',
#                   'ncd_required', 'default_add_ons', 'status')
#         widgets = {
#             'deductible_extras': forms.TextInput(attrs={'class': 'form-control'}),
#             'default_add_ons': forms.SelectMultiple(attrs={'class': 'product-addons'}),
#             'agency_repair': forms.CheckboxInput(),
#             'ncd_required': forms.CheckboxInput(),
#         }


