from django import forms
from django.contrib.auth.models import User

from core.utils import add_empty_choice
from django.utils.html import strip_tags, escape
from customers.models import Customer
from felix.constants import CAR_YEARS_LIST, SORTING_CHOICES
from motorinsurance.constants import LEAD_TYPES
from motorinsurance.models import Deal
from accounts.models import UserProfile

from core.custom_fields import MoneyField

from motorinsurance.helpers import CarTreeHelper


class DealForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset=Customer.objects.none(), required=False)
    customer_name = forms.CharField()
    car_make = forms.ChoiceField(choices=[])
    car_trim = forms.ChoiceField(choices=[])
    car_year = forms.ChoiceField(
        choices=add_empty_choice(CAR_YEARS_LIST), widget=forms.widgets.Select(
            attrs={'class': 'form-control'}
        )
    )
    custom_car_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

    lead_type = forms.ChoiceField(
        choices=LEAD_TYPES, widget=forms.widgets.Select(
            attrs={'class': 'form-control'}
        )
    )

    vehicle_insured_value = MoneyField(
        widget=forms.TextInput(attrs={'class': 'form-control auto-format-money-field'})
    )

    private_car = forms.ChoiceField(
        choices=[('commercial', "Commercial"), ('private', "Private")], widget=forms.widgets.Select(
            attrs={'class': 'form-control'}
        )
    )

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company')
        self.user = kwargs.pop('user')

        super(DealForm, self).__init__(*args, **kwargs)

        self.fields['customer'].queryset = Customer.objects.filter(company=self.company, status=Customer.STATUS_ACTIVE)

        if self.data:
            # Validating Car's Year, Make & Model
            year, make = self.data.get("car_year"), self.data.get("car_make")

            if year:
                self.fields['car_make'].choices = CarTreeHelper.get_makes_for_year(year)

            if make:
                self.fields['car_trim'].choices = CarTreeHelper.get_models_and_trims_for_year_and_make(year, make)

            if self.data.get('custom_car_name'):
                self.fields['car_trim'].required = False

    def clean_custom_car_name(self):
        val = self.cleaned_data['custom_car_name']

        if val:
            val = escape(strip_tags(val))

        return val

    class Meta:
        model = Deal
        exclude = ('created_on', 'updated_on', 'company', 'car_trim', 'car_make', 'number_of_passengers',
                   'stage', 'private_car', 'car_unmodified', 'car_gcc_spec', 'deal_type',)


class DealSearchAndOrderingForm(forms.Form):
    search_term = forms.CharField(
        label='Search for', required=False, widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Search by deal, customer or vehicle'}))

    stage = forms.ChoiceField(choices=add_empty_choice(Deal.STAGES, '-' * 5), required=False)
    assigned_to = forms.ChoiceField(choices=add_empty_choice([], '-' * 5), required=False)
    producer = forms.ChoiceField(choices=add_empty_choice([], '-' * 5), required=False)

    created_on_after = forms.DateField(
        input_formats=['%d-%m-%Y'],
        label='Created on or after', required=False, widget=forms.TextInput(
            attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}))
    created_on_before = forms.DateField(
        input_formats=['%d-%m-%Y'],
        label='Created on or before', required=False, widget=forms.TextInput(
            attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}))

    sort_by = forms.ChoiceField(choices=SORTING_CHOICES, required=False)

    deleted = forms.ChoiceField(choices=add_empty_choice(((Deal.STATUS_DELETED, 'Yes'),), '-' * 5), required=False)

    def __init__(self, **kwargs):
        company = kwargs.pop('company')

        super(DealSearchAndOrderingForm, self).__init__(**kwargs)

        self.fields['assigned_to'].choices = [('', 'Select user to filter'), ('unassigned', 'All Unassigned')] + list(
            (user.pk, user.get_full_name()) for user in User.objects.filter(userprofile__company=company, is_active=True).order_by('first_name'))

        producers = list()
        for up in UserProfile.objects.filter(company=company, user__is_active=True).order_by('user__first_name'):
            producers.append((up.user.pk, up.user.get_full_name()))

        self.fields['producer'].choices = [('', 'Select a referrer to filter'), ('unassigned', 'All Unassigned')] + producers
