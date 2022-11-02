from django import forms
from django.utils.html import strip_tags, escape

from core.utils import add_empty_choice
from core.custom_fields import MoneyField

from customers.models import Customer
from healthinsurance.models.policy import HealthPolicy as Policy


from felix.constants import CAR_YEARS_LIST


class PolicyForm(forms.ModelForm):
    policy_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    invoice_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    start_date = forms.DateField(input_formats=['%d-%m-%Y'], widget=forms.TextInput(
        attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}))
    expiry_date = forms.DateField(input_formats=['%d-%m-%Y'], widget=forms.TextInput(
        attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}))
    # policy_document = forms.FileField(widget=forms.FileInput(
    #     attrs={'class': 'filestyle', 'data-input': 'false', 'data-buttonname': 'btn-secondary'}
    # ))
    # invoice_document = forms.FileField(widget=forms.FileInput(
    #     attrs={'class': 'filestyle', 'data-input': 'false', 'data-buttonname': 'btn-secondary'}
    # ), required=False)

    status = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    def __init__(self, **kwargs):
        company = kwargs.pop('company')

        super(PolicyForm, self).__init__(**kwargs)

        

    class Meta:
        model = Policy
        fields = (
            'policy_number', 'invoice_number',
            'start_date', 'expiry_date')


class NewPolicyForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset=Customer.objects.none(), required=False)
    customer_name = forms.CharField()

    car_year = forms.ChoiceField(
        choices=add_empty_choice(CAR_YEARS_LIST), widget=forms.widgets.Select(
            attrs={'class': 'form-control'}
        )
    )
    custom_car_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    reference_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    start_date = forms.DateField(input_formats=['%d-%m-%Y'], widget=forms.TextInput(
        attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}))
    expiry_date = forms.DateField(input_formats=['%d-%m-%Y'], widget=forms.TextInput(
        attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}))

    custom_product_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    premium = MoneyField(
        widget=forms.TextInput(attrs={'class': 'form-control auto-format-money-field'})
    )
    deductible = MoneyField(
        widget=forms.TextInput(attrs={'class': 'form-control auto-format-money-field'})
    )

    insured_car_value = MoneyField(
        widget=forms.TextInput(attrs={'class': 'form-control auto-format-money-field'})
    )

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')

        super(NewPolicyForm, self).__init__(*args, **kwargs)

        self.fields['customer'].queryset = Customer.objects.filter(company=self.company, status=Customer.STATUS_ACTIVE)

    def clean_custom_car_name(self):
        val = self.cleaned_data['custom_car_name']

        if val:
            val = escape(strip_tags(val))

        return val

    class Meta:
        model = Policy
        fields = ('customer', 'customer_name', 'policy_number',
                  'start_date', 'expiry_date','premium')


class PolicySearchAndOrderingForm(forms.Form):
    search_term = forms.CharField(label='Search for', required=False,
                                  widget=forms.TextInput(attrs={'placeholder': 'Search by name, email or policy number'}))

    #products = forms.ModelChoiceField(queryset=Customer.objects.none(), required=False)

    created_on_after = forms.DateField(input_formats=['%d-%m-%Y'], label='Created on or after', required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control datepicker'}))
    created_on_before = forms.DateField(input_formats=['%d-%m-%Y'], label='Created on or before', required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control datepicker'}))

    status = forms.ChoiceField(choices=add_empty_choice(Policy.STATUSES, '-' * 5), required=False)

    order_by = forms.CharField(required=False)
    expiry = forms.CharField(required=False)

    def __init__(self, **kwargs):
        company = kwargs.pop('company')

        super(PolicySearchAndOrderingForm, self).__init__(**kwargs)

        #self.fields['products'].queryset = company.available_motor_insurance_products.all()


class RenewalsSearchAndOrderingForm(forms.Form):
    search_term = forms.CharField(label='Search for', required=False,
                                  widget=forms.TextInput(attrs={'placeholder': 'Search by name, email or reference'}))
    hide_renewal_deal = forms.BooleanField(required=False)
    from_date = forms.CharField(required=False)
    to_date = forms.CharField(required=False)
