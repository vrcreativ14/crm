import datetime

from django.utils.timezone import now as tz_now

from django import forms

from core.utils import add_empty_choice

from motorinsurance.models import Order
from motorinsurance.models import Quote, QuotedProduct, Deal

from core.custom_fields import MoneyField
from motorinsurance_shared.models import Product


class MotorInsuranceQuoteForm(forms.ModelForm):
    def __init__(self, **kwargs):
        company = kwargs.pop('company')

        super(MotorInsuranceQuoteForm, self).__init__(**kwargs)

        self.fields['deal'].queryset = Deal.objects.filter(company=company)

        self.fields['expiry_date'].initial = tz_now().date() + datetime.timedelta(
            days=company.workspacemotorsettings.quote_expiry_days)

    class Meta:
        model = Quote
        fields = ('deal', 'status', 'insured_car_value', 'is_suv', 'is_coupe',
                  'expiry_date', 'note')
        widgets = {
            'insured_car_value': forms.TextInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.TextInput(attrs={'class': 'form-control datepicker'}),
            'note': forms.Textarea(attrs={'class': 'form-control textarea', 'rows': 3}),
            'is_coupe': forms.CheckboxInput(attrs={'switch': ''}),
            'is_suv': forms.CheckboxInput(attrs={'switch': ''}),
        }


class MotorInsuranceQuotedProductForm(forms.ModelForm):
    class ProductModelChoiceField(forms.ModelChoiceField):
        def label_from_instance(self, obj):
            return obj.name

    product = ProductModelChoiceField(
        queryset=Product.objects.none(), widget=forms.Select(attrs={'class': 'product-field sorted'})
    )

    premium = MoneyField(
        widget=forms.TextInput(attrs={'class': 'form-control auto-format-money-field'})
    )

    sale_price = MoneyField(
        widget=forms.TextInput(attrs={'class': 'form-control auto-format-money-field'})
    )

    deductible = MoneyField(
        widget=forms.TextInput(attrs={'class': 'form-control auto-format-money-field'}),
        required=False
    )

    insured_car_value = MoneyField(
        widget=forms.TextInput(attrs={'class': 'form-control auto-format-money-field'}),
        required=False
    )

    insurer_quote_reference = MoneyField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False
    )

    def __init__(self, **kwargs):
        company = kwargs.pop('company')

        super(MotorInsuranceQuotedProductForm, self).__init__(**kwargs)

        self.fields['product'].queryset = company.available_motor_insurance_products.all()

    class Meta:
        model = QuotedProduct
        fields = ('product', 'agency_repair', 'premium', 'deductible', 'deductible_extras', 'insured_car_value',
                  'ncd_required', 'default_add_ons', 'status')
        widgets = {
            'deductible_extras': forms.TextInput(attrs={'class': 'form-control'}),
            'default_add_ons': forms.SelectMultiple(attrs={'class': 'product-addons'}),
            'agency_repair': forms.CheckboxInput(),
            'ncd_required': forms.CheckboxInput(),
        }


class OrderForm(forms.ModelForm):
    payment_amount = MoneyField(
        widget=forms.TextInput(attrs={'class': 'hide form-control auto-format-money-field'})
    )

    policy_start_date = forms.DateField(input_formats=['%d-%m-%Y'], required=True, widget=forms.TextInput(
        attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}))

    def __init__(self, *args, **kwargs):
        quoted_products = kwargs.pop('quoted_products')

        super(OrderForm, self).__init__(*args, **kwargs)

        self.fields['selected_product'].queryset = quoted_products

    class Meta:
        model = Order
        exclude = ('deal', 'created_on', 'updated_on',)
        widgets = {
            'selected_product': forms.Select(attrs={'class': 'hide'}),
            'selected_add_ons': forms.SelectMultiple(attrs={'class': 'product-addons hide'}),
            'discount': forms.TextInput(attrs={'class': 'form-control align-right'}),
            'mortgage_by': forms.TextInput(attrs={'class': 'form-control'}),
        }


class QuoteSearchAndOrderingForm(forms.Form):
    search_term = forms.CharField(label='Search for', required=False,
                                  widget=forms.TextInput(attrs={'placeholder': 'Search by name or email'}))

    stage = forms.ChoiceField(choices=add_empty_choice(Deal.STAGES, '-' * 5), required=False)

    created_on_after = forms.DateField(label='Created after', required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control datepicker'}))
    created_on_before = forms.DateField(label='Created before', required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control datepicker'}))

    order_by = forms.CharField(required=False)

    def __init__(self, **kwargs):
        super(QuoteSearchAndOrderingForm, self).__init__(**kwargs)
