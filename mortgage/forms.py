import datetime
from django.contrib.postgres import fields
from django.db.models.fields import NullBooleanField
from accounts.models import UserProfile
from core.custom_fields import MoneyField
from core.utils import add_empty_choice
from customers.models import Customer
from django import forms
from django.contrib.auth.models import User
from felix.constants import SORTING_CHOICES
from mortgage.models import Bank, BankInterestRate, Deal, Eibor, GovernmentFee, Order,  Quote, EiborPost
from mortgage.constants import *
from django.conf import settings
from rolepermissions.checkers import get_user_roles

BOOLEAN_CHOICE = (
    (1, 'Yes'),
    (0, 'No')
)

class CustomerForm(forms.Form):
    customer_phone = forms.CharField(max_length=20)
    customer_name = forms.CharField(max_length=50)
    customer_email = forms.EmailField()
    
    def clean(self, *args):
        self.cleaned_data['phone'] = self.cleaned_data.pop('customer_phone', None)
        self.cleaned_data['email'] = self.cleaned_data.pop('customer_email', None)
        self.cleaned_data['name'] = self.cleaned_data.pop('customer_name', None)
        self.cleaned_data['company_id'] = settings.COMPANY_ID
        return self.cleaned_data


class CreateDealForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset=Customer.objects.none(), required=False)
    customer_email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    customer_phone = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    customer_name = forms.CharField()
    stage = forms.ChoiceField(choices=DEAL_STAGES, initial=('new', "New Deal"))
    deal_type = forms.ChoiceField(choices=DEAL_TYPES, initial=DEAL_TYPE_NEW)
    status = forms.ChoiceField(choices=DEAL_STATUSES, initial=STATUS_ACTIVE)

    property_price = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": "form-control price-input"}))
    down_payment = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": "form-control price-input"}))
    tenure = forms.CharField(
        label='Tenure',
        widget=forms.TextInput(attrs={"class": "form-control", 'min': 1, 'max': '30', 'type': 'number'}))

    referrer = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.filter(
            pk__in=[
                y.pk
                for y in User.objects.all()
                if get_user_roles(y)
                if get_user_roles(y)[0].__name__ == "Producer"
            ]
        )
    )

    class Meta:
        model = Deal
        exclude = ("l_tv", "govt_fee")

    def clean_customer(self):
        self.cleaned_data = super().clean()
        if self.data.get("customer_id", None):
            self.cleaned_data["customer"] = Customer.objects.get(pk=self.data.get("customer_id", None))

    def clean(self):
        self.cleaned_data = super().clean()
        from decimal import Decimal 
        property_price = int(Decimal(self.cleaned_data.get("property_price").replace(',', '')))
        down_payment = int(Decimal(self.cleaned_data.get("down_payment").replace(',', '')))
        if int(Decimal(property_price)) < int(Decimal(down_payment)):
            self.add_error('property_price', "Property price can not be less than down payment")
            self.add_error('down_payment', "Down payment can not be more than property price")
        else:
            self.cleaned_data['property_price'] = property_price
            self.cleaned_data['down_payment'] = down_payment
        return self.cleaned_data


class NewDealForm(forms.Form):
    loan_duration = forms.IntegerField()
    property_price = forms.IntegerField()
    down_payment = forms.IntegerField()
    referrer = forms.EmailField(required=False)
 
    def clean(self, *args):
        user = User.objects.filter(email=self.cleaned_data.get('referrer', None))
        self.cleaned_data.pop('referrer', None)
        if user:
            self.cleaned_data['referrer'] = user[0]
        self.cleaned_data['tenure'] = self.cleaned_data.pop('loan_duration', None)
        self.cleaned_data['loan_amount'] = self.cleaned_data['property_price'] - self.cleaned_data.get('down_payment', 0)
        return self.cleaned_data


class UpdateDealForm(forms.ModelForm):
    class Meta:
        model = Deal
        exclude = ('customer',)


class DealSearchAndOrderingForm(forms.Form):
    search_term = forms.CharField(
        label="Search for",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search by deal, customer, referrer, etc",
            }
        ),
    )

    stage = forms.ChoiceField(choices=add_empty_choice(DEAL_STAGES, "-" * 5), required=False)
    assigned_to = forms.ChoiceField(choices=add_empty_choice([], "-" * 5), required=False)
    producer = forms.ChoiceField(choices=add_empty_choice([], "-" * 5), required=False)

    created_on_after = forms.DateField(
        input_formats=["%d-%m-%Y"],
        label="Created on or after",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control datepicker", "autocomplete": "off"}))

    created_on_before = forms.DateField(
        input_formats=["%d-%m-%Y"],
        label="Created on or before",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control datepicker", "autocomplete": "off"}))

    sort_by = forms.ChoiceField(choices=SORTING_CHOICES, required=False)
    deleted = forms.ChoiceField(choices=add_empty_choice(((STATUS_DELETED_TRUE, "Yes"),), "-" * 5), required=False)

    def __init__(self, **kwargs):
        company = kwargs.pop("company")

        super(DealSearchAndOrderingForm, self).__init__(**kwargs)

        self.fields["assigned_to"].choices = [
            ("", "Select user to filter"),
            ("unassigned", "All Unassigned"),
        ] + list(
            (user.pk, user.get_full_name())
            for user in User.objects.filter(
                userprofile__company=company, is_active=True
            ).order_by("first_name")
        )

        producers = list()
        for up in UserProfile.objects.filter(company=company, user__is_active=True).order_by("user__first_name"):
            producers.append((up.user.pk, up.user.get_full_name()))

        self.fields["producer"].choices = [
            ("", "Select a referrer to filter"),
            ("unassigned", "All Unassigned"),
        ] + producers


class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = "__all__"


class MortgageQuoteForm(forms.ModelForm):
    banks = forms.ModelMultipleChoiceField(queryset=Bank.objects.all())

    class Meta:
        model = Quote
        fields = ('banks', 'deals')


class DateInput(forms.DateInput):
    input_type = 'date'


class BankInterestRateForm(forms.ModelForm):
    class Meta:
        model = BankInterestRate
        exclude = ('bank', 'is_default', 'eibor_rate', 'eibor_post_rate')


class BankInterestRateSegmentedForm(forms.ModelForm):
    class Meta:
        model = BankInterestRate
        exclude = ('eibor_rate', 'eibor_post_rate')

    def clean(self):
        self.cleaned_data = super().clean()
        if self.cleaned_data["eibor_duration"] == "0M":
            self.cleaned_data["eibor_rate"] = Eibor.objects.get().eibor_rate_0m
        if self.cleaned_data["eibor_duration"] == "1M":
            self.cleaned_data["eibor_rate"] = Eibor.objects.get().eibor_rate_1m
        if self.cleaned_data["eibor_duration"] == "3M":
            self.cleaned_data["eibor_rate"] = Eibor.objects.get().eibor_rate_3m
        if self.cleaned_data["eibor_duration"] == "6M":
            self.cleaned_data["eibor_rate"] = Eibor.objects.get().eibor_rate_6m

        if self.cleaned_data["eibor_post_duration"] == "0M":
            self.cleaned_data["eibor_post_rate"] = EiborPost.objects.get().eibor_post_rate_0m
        if self.cleaned_data["eibor_post_duration"] == "1M":
            self.cleaned_data["eibor_post_rate"] = EiborPost.objects.get().eibor_post_rate_1m
        if self.cleaned_data["eibor_post_duration"] == "3M":
            self.cleaned_data["eibor_post_rate"] = EiborPost.objects.get().eibor_post_rate_3m
        if self.cleaned_data["eibor_post_duration"] == "6M":
            self.cleaned_data["eibor_post_rate"] = EiborPost.objects.get().eibor_post_rate_6m

        return self.cleaned_data


class EiborForm(forms.ModelForm):
    class Meta:
        model = Eibor
        fields = "__all__"


class EiborPostForm(forms.ModelForm):
    class Meta:
        model = EiborPost
        fields = "__all__"


class GovtForm(forms.ModelForm):
    class Meta:
        model = GovernmentFee
        fields = "__all__"


class CreateBankForm(forms.ModelForm):
    interest_rate = BankInterestRateForm().fields['interest_rate']
    eibor_duration = BankInterestRateForm().fields['eibor_duration']
    eibor_post_duration = BankInterestRateForm().fields['eibor_post_duration']
    introduction_period_in_years = BankInterestRateForm().fields['introduction_period_in_years']
    post_introduction_rate = BankInterestRateForm().fields['post_introduction_rate']
    extra_financing_allowed = forms.ChoiceField(choices=BOOLEAN_CHOICE, label="Extra Financing Allowed ?", initial=0, widget=forms.Select(), required=False)
    class Meta:
        model = Bank
        fields = (
            "name",
            "logo",
            "interest_rate",
            "eibor_duration",
            "introduction_period_in_years",
            "post_introduction_rate",
            "eibor_post_duration",
            "property_valuation_fee",
            "bank_processing_fee_rate",
            # "bank_processing_fee_extra",
            # "max_bank_processing_fee",
            "life_insurance_monthly_rate",
            "property_insurance_yearly_rate",
            "full_settlement_percentage",
            "full_settlement_max_value",
            "free_partial_payment_per_year",
            "sample_form",
            "extra_financing_allowed",
        )


class OrderForm(forms.ModelForm):

    status = forms.ChoiceField(required=False)
    payment_amount = forms.DecimalField(required=False)
    discount = forms.DecimalField(required=False)

    class Meta:
        model = Order
        exclude = ('order_number',)


class NewIssuedForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), required=False)
    customer_email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    customer_phone = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    property_price = forms.CharField(
        required=True, widget=forms.TextInput(attrs={"class": "form-control price-input"}))
    # bank = forms.ChoiceField(required=False)
    # sum_insured = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    issue_date = forms.DateField(
        input_formats=['%d-%m-%Y'],
        widget=forms.TextInput(attrs={'class': 'form-control datepicker', 'autocomplete': 'off'}),
        initial=datetime.date.today().strftime('%d-%m-%Y')
    )

    class Meta:
        model = Deal
        exclude = ('stage', 'deal_type', 'down_payment', 'expat', 'tenure', 'govt_fee', 'property_price', )


class FilterIssuedForm(forms.Form):
    search_term = forms.CharField(
        label="Search for",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search by deal, customer, referrer, etc",
            }
        ),
    )          

    created_on_after = forms.DateField(
        input_formats=["%d-%m-%Y"],
        label="Created on or after",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control datepicker", "autocomplete": "off"}))

    created_on_before = forms.DateField(
        input_formats=["%d-%m-%Y"],
        label="Created on or before",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control datepicker", "autocomplete": "off"}))

    sort_by = forms.ChoiceField(choices=SORTING_CHOICES, required=False)
    deleted = forms.ChoiceField(choices=add_empty_choice(((STATUS_DELETED_TRUE, "Yes"),), "-" * 5), required=False)

    def __init__(self, **kwargs):
        #company = kwargs.pop("company")

        super(FilterIssuedForm, self).__init__(**kwargs)

        # self.fields["assigned_to"].choices = [
        #     ("", "Select user to filter"),
        #     ("unassigned", "All Unassigned"),
        # ] + list(
        #     (user.pk, user.get_full_name())
        #     for user in User.objects.filter(
        #         userprofile__company=company, is_active=True
        #     ).order_by("first_name")
        # )

        # producers = list()
        # for up in UserProfile.objects.filter(company=company, user__is_active=True).order_by("user__first_name"):
        #     producers.append((up.user.pk, up.user.get_full_name()))

        # self.fields["producer"].choices = [
        #     ("", "Select a referrer to filter"),
        #     ("unassigned", "All Unassigned"),
        # ] + producers
