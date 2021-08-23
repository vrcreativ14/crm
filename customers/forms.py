from django import forms
from core.utils import add_empty_choice

from customers.models import Customer
from felix.constants import COUNTRIES, GENDER_CHOICES, SORTING_CHOICES
from motorinsurance.constants import LICENSE_AGE_LIST


class CustomerForm(forms.ModelForm):
    status = forms.ChoiceField(choices=add_empty_choice(Customer.STATUSES, '-' * 5), required=False)

    class Meta:
        model = Customer
        exclude = ('created_on', 'updated_on', 'company',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'nationality': forms.Select(attrs={'class': 'form-control'}),
        }


class CustomerMergeForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    gender = forms.ChoiceField(choices=add_empty_choice(GENDER_CHOICES, '-' * 5), required=False)
    nationality = forms.ChoiceField(choices=add_empty_choice(COUNTRIES, '-' * 5))

    first_license_age = forms.ChoiceField(choices=add_empty_choice(LICENSE_AGE_LIST, '-' * 5), required=False)
    uae_license_age = forms.ChoiceField(choices=add_empty_choice(LICENSE_AGE_LIST, '-' * 5), required=False)

    first_license_country = forms.ChoiceField(choices=add_empty_choice(COUNTRIES, '-' * 5), required=False)
    first_license_issue_date = forms.DateField(
        input_formats=['%d-%m-%Y'], required=False,
        widget=forms.TextInput(attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}))
    uae_license_issue_date = forms.DateField(
        input_formats=['%d-%m-%Y'], required=False,
        widget=forms.TextInput(attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}))


class CustomerSearchAndOrderingForm(forms.Form):
    search_term = forms.CharField(label='Search for', required=False,
                                  widget=forms.TextInput(attrs={'placeholder': 'Search by name, email or phone'}))

    created_on_after = forms.DateField(input_formats=['%d-%m-%Y'], label='Created on or after', required=False,
                                       widget=forms.TextInput(attrs={
                                           'class': 'form-control datepicker',
                                           'autocomplete': 'off'
                                       }))
    created_on_before = forms.DateField(input_formats=['%d-%m-%Y'], label='Created on or before', required=False,
                                        widget=forms.TextInput(attrs={
                                            'class': 'form-control datepicker',
                                            'autocomplete': 'off'
                                        }))

    status = forms.ChoiceField(choices=add_empty_choice(Customer.STATUSES, '-' * 5), required=False)
    sort_by = forms.ChoiceField(choices=SORTING_CHOICES, required=False)
