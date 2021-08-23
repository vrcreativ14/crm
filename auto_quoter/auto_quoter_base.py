from django import forms

from felix.constants import CAR_YEARS_LIST
from felix.constants import COUNTRIES, GENDER_CHOICES, EMIRATES_LIST
from motorinsurance.constants import LICENSE_AGE_LIST
from motorinsurance.constants import NO_CLAIMS, INSURANCE_TYPES


class AutoQuoterBase:
    def __init__(self):
        self.company = None
        self.config = None

    def get_deal_missing_data_fields(self, deal):
        raise NotImplemented('Subclasses of AutoQuoterBase must implement this method')

    def deal_missing_fields(self, deal):
        fields = {
            # Customer
            'customer.name': {
                'name': 'customer___name',
                'error_message': 'Customer name is required',
                'field': forms.CharField(
                    required=True,
                    label='Customer name',
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            },
            'customer.email': {
                'name': 'customer___email',
                'error_message': 'Customer email is required',
                'field': forms.EmailField(
                    required=True,
                    label='Customer email address',
                    widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'email'})
                )
            },
            'customer.dob': {
                'name': 'customer___dob',
                'error_message': 'Customer date of birth is required',
                'field': forms.DateField(
                    required=True,
                    input_formats=["%d-%m-%Y"],
                    label='Customer date of birth',
                    widget=forms.TextInput(attrs={'class': 'form-control datepicker dp', 'autocomplete': 'off'})
                )
            },
            'customer.phone': {
                'name': 'customer___phone',
                'error_message': 'Customer phone number is required',
                'field': forms.CharField(
                    required=True,
                    label='Customer phone',
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            },

            # Customer Motor Profile
            'customer.gender': {
                'name': 'customer___gender',
                'error_message': 'Customer gender is required',
                'field': forms.ChoiceField(
                    required=True,
                    choices=GENDER_CHOICES,
                    label='Customer gender',
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            },

            'customer.nationality': {
                'name': 'customer___nationality',
                'error_message': 'Customer nationality is required',
                'field': forms.ChoiceField(
                    required=True,
                    choices=COUNTRIES,
                    label='Customer nationality',
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            },

            'customer_profile.uae_license_age': {
                'name': 'customer_profile___uae_license_age',
                'error_message': 'UAE license age of customer required',
                'field': forms.ChoiceField(
                    required=True,
                    choices=LICENSE_AGE_LIST,
                    label='UAE license age of customer',
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            },

            'customer_profile.first_license_country': {
                'name': 'customer_profile___first_license_country',
                'error_message': 'Country of first license required',
                'field': forms.ChoiceField(
                    required=True,
                    choices=COUNTRIES,
                    label='Country of first license',
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            },

            # Deal
            'deal.car_year': {
                'name': 'deal___car_year',
                'field': forms.ChoiceField(
                    required=True,
                    choices=CAR_YEARS_LIST,
                    label='Car model year',
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            },
            'deal.place_of_registration': {
                'name': 'deal___place_of_registration',
                'field': forms.ChoiceField(
                    required=True,
                    choices=EMIRATES_LIST,
                    label='Place of registration',
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            },
            'deal.date_of_first_registration': {
                'name': 'deal___date_of_first_registration',
                'field': forms.DateField(
                    required=True,
                    input_formats=["%d-%m-%Y"],
                    label='Date of first registration',
                    widget=forms.TextInput(attrs={'class': 'form-control datepicker', 'autocomplete': 'off'})
                )
            },

            'deal.custom_car_name': {
                'name': 'deal___custom_car_name',
                'error_message': 'Car trim must be set to a valid choice or a custom value',
                'field': forms.CharField(
                    required=True,
                    label='Custom car name',
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            },
            'deal.number_of_passengers': {
                'name': 'deal__number_of_passengers',
                'error_message': 'Number of passengers must be set accurately',
                'field': forms.IntegerField(
                    required=True,
                    label='No. of passengers',
                    widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'})
                )
            },
            'deal.current_insurance_type': {
                'name': 'deal___current_insurance_type',
                'error_message': 'Current insurance type must be set for cars that are not brand new',
                'field': forms.ChoiceField(
                    required=True,
                    choices=INSURANCE_TYPES,
                    label='Current cover',
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            },
            'deal.vehicle_insured_value': {
                'name': 'deal___vehicle_insured_value',
                'error_message': 'Insured value of car must be set',
                'field': forms.IntegerField(
                    required=True,
                    label='Car sum insured',
                    widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number'})
                )
            },
            'deal.years_without_claim': {
                'name': 'deal___years_without_claim',
                'error_message': 'Years without claim must be set',
                'field': forms.ChoiceField(
                    required=True,
                    choices=NO_CLAIMS,
                    label='Years without claim',
                    widget=forms.Select(attrs={'class': 'form-control'})
                )
            },
        }

        missing_fields = self.get_deal_missing_data_fields(deal)

        return [fields.get(field_name) for field_name in missing_fields]

    def get_quote_for_insurer_with_deal(self, insurer, deal, form_data):
        """Response data format:
            {
                'productCode': Our Product Code,
                'quoteReference': Ref. No,
                'insuredCarValue': Insured Value,
                'canInsure': True/False,
                'referralRequired': True/False,
                'agencyRepair': True/False,
                'premium': Premium,
                'deductible': Deductible,
                'rulesTrace': Array of strings with info on how quote was generated
            }
        """
        raise NotImplemented('Subclasses of AutoQuoterBase must implement this method')

    def setup_for_company(self, company):
        pass
