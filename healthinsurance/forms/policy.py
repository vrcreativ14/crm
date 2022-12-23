from django import forms
from django.utils.html import strip_tags, escape

from core.utils import add_empty_choice
from core.custom_fields import MoneyField

from customers.models import Customer
from healthinsurance.models.policy import *


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
        model = HealthPolicy
        fields = (
            'policy_number', 'invoice_number',
            'start_date', 'expiry_date')


class PolicySearchAndOrderingForm(forms.Form):
    search_term = forms.CharField(label='Search for', required=False,
                                  widget=forms.TextInput(attrs={'placeholder': 'Search by policy number or customer name'}))

    created_on_after = forms.DateField(input_formats=['%d-%m-%Y'], label='Created on or after', required=False,
                                       widget=forms.TextInput(attrs={'class': 'form-control datepicker'}))
    created_on_before = forms.DateField(input_formats=['%d-%m-%Y'], label='Created on or before', required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control datepicker'}))

    status = forms.ChoiceField(choices=add_empty_choice(HealthPolicy.STATUSES, '-' * 5), required=False)

    order_by = forms.CharField(required=False)
    expiry = forms.CharField(required=False)

    def __init__(self, **kwargs):
        company = kwargs.pop('company')

        super(PolicySearchAndOrderingForm, self).__init__(**kwargs)


class RenewalsSearchAndOrderingForm(forms.Form):
    search_term = forms.CharField(label='Search for', required=False,
                                  widget=forms.TextInput(attrs={'placeholder': 'Search by name, email or reference'}))
    hide_renewal_deal = forms.BooleanField(required=False)
    from_date = forms.CharField(required=False)
    to_date = forms.CharField(required=False)
