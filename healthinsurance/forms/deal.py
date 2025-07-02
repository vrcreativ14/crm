from pyexpat import model
from django import forms
from healthinsurance.models.deal import *
from healthinsurance.models.quote import *
from healthinsurance.models.policy import *
from customers.models import *
from felix.constants import FIELD_LENGTHS, GENDER_CHOICES, MARITAL_STATUS_LIST, SORTING_CHOICES
from core.custom_fields import MoneyField
from core.utils import add_empty_choice
from healthinsurance.constants import DEAL_STAGES

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
    # customer = forms.ModelChoiceField(queryset=Customer.objects.none(), required=False)
    # customer_email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    # customer_phone = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    # customer_name = forms.CharField()
    primary_member = forms.ModelChoiceField(queryset=PrimaryMember.objects.all())
    class Meta:
        model = Deal
        exclude = ('status',)

class PrimaryMemberForm(forms.ModelForm):
    class Meta:
        model = PrimaryMember
        exclude = ('additional_members',)

class HealthPolicyForm(forms.ModelForm):     
    company = forms.ModelChoiceField(queryset=Company.objects.all())
    class Meta:
        model = HealthPolicy
        exclude = ['status']

class PolicyForm(forms.ModelForm):
    #deal = forms.ModelChoiceField(queryset=Deal.objects.all())
    class Meta:
        model = HealthPolicy
        exclude = ['status']


class CustomerForm(forms.ModelForm):        
    class Meta:
        model = Customer
        exclude = ['status',]


class DealSearchAndOrderingForm(forms.Form):
    search_term = forms.CharField(
        label='Search for', required=False, widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Search by deal, customer'}))

    stage = forms.ChoiceField(choices=add_empty_choice(DEAL_STAGES, '-' * 5), required=False)
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

    #deleted = forms.ChoiceField(choices=add_empty_choice(((Deal.status, 'Yes'),), '-' * 5), required=False)

    def __init__(self, **kwargs):
        company = kwargs.pop('company')

        super(DealSearchAndOrderingForm, self).__init__(**kwargs)

        self.fields['assigned_to'].choices = [('', 'Select user to filter'), ('unassigned', 'All Unassigned')] + list(
            (user.pk, user.get_full_name()) for user in User.objects.filter(userprofile__company=company, is_active=True).order_by('first_name'))

        producers = list()
        for up in UserProfile.objects.filter(company=company, user__is_active=True).order_by('user__first_name'):
            producers.append((up.user.pk, up.user.get_full_name()))

        self.fields['producer'].choices = [('', 'Select a referrer to filter'), ('unassigned', 'All Unassigned')] + producers
