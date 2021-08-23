from django import forms

from core.utils import is_valid_number, normalize_phone_number, add_empty_choice
from felix.constants import CAR_YEARS_LIST, AGE_YEARS, COUNTRIES, UAE_COUNTRY_CODE, EMIRATES_LIST
from motorinsurance.constants import LEAD_TYPES, TOP_TIER_INSURERS, INSURANCE_TYPES, LICENSE_AGE_LIST, NO_CLAIMS, \
    LEAD_TYPES_NEW_CAR, LEAD_TYPES_OWN_CAR, NO_CLAIMS_CANT_REMEMBER
from motorinsurance.helpers import CarTreeHelper


class MotorInsuranceLeadForm(forms.Form):
    # Personal details
    name = forms.CharField(max_length=255, widget=forms.widgets.TextInput(attrs={'placeholder': 'First & Last Name'}))
    email = forms.EmailField(widget=forms.widgets.TextInput(attrs={'placeholder': 'Email address', 'type': 'email'}))
    contact_number = forms.CharField(max_length=20, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'Mobile number', 'type': 'tel'}))

    lead_type = forms.ChoiceField(choices=LEAD_TYPES)

    car_make = forms.ChoiceField()
    car_model = forms.ChoiceField()
    car_year = forms.ChoiceField(choices=add_empty_choice(CAR_YEARS_LIST), widget=forms.widgets.Select(
        attrs={
            'class': 'numeric-field'
        })
                                 )

    vehicle_insured_value = forms.IntegerField(required=True, widget=forms.widgets.TextInput(
        attrs={
            'placeholder': 'Enter your Vehicle Insured Value',
            'class': 'auto-format-money-field',
            'maxlength': 10,
            'type': 'tel'
        }
    ))

    current_insurer = forms.ChoiceField(choices=TOP_TIER_INSURERS, required=False)
    current_insurance_type = forms.ChoiceField(choices=INSURANCE_TYPES, required=False)

    date_of_first_registration = forms.DateField(input_formats=[
        "%Y-%m"
    ], required=False)
    place_of_registration = forms.ChoiceField(choices=EMIRATES_LIST)

    age = forms.DateField(input_formats=["%d/%m/%Y"], required=False, widget=forms.widgets.TextInput(
        attrs={
            'placeholder': 'DD/MM/YYYY',
            'class': 'datepicker input-field date-field show-cross pl-5',
            'autocomplete': 'off',
        }
    ))

    nationality = forms.ChoiceField(choices=add_empty_choice(COUNTRIES))
    first_license_country = forms.ChoiceField(choices=add_empty_choice(COUNTRIES))

    first_license_age = forms.ChoiceField(choices=LICENSE_AGE_LIST, required=False)
    uae_license_age = forms.ChoiceField(choices=LICENSE_AGE_LIST)

    years_without_claim = forms.ChoiceField(choices=NO_CLAIMS)
    claim_certificate_available = forms.BooleanField(required=False)

    private_car = forms.BooleanField()
    car_unmodified = forms.BooleanField()
    car_gcc_spec = forms.BooleanField()

    custom_car_name = forms.CharField(max_length=255, widget=forms.widgets.TextInput(
        attrs={'placeholder': 'Enter your car\'s model and trim'}
    ))

    user_id = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.data:
            # Set some fields to required False if its a new car
            if self.data.get('lead_type') != LEAD_TYPES_NEW_CAR:
                self.fields['date_of_first_registration'].required = True

            # Set car_model field to required False if custom trim is checked
            if self.data.get('cant_find_car'):
                self.fields['car_model'].required = False
            else:
                self.fields['custom_car_name'].required = False

            # Set first_license_age to required true if first_license_country is not UAE
            if self.data.get('first_license_country') != UAE_COUNTRY_CODE:
                self.fields['first_license_age'].required = True

            # Insurer required if its an own car renewal
            if self.data.get('lead_type') == LEAD_TYPES_OWN_CAR:
                self.fields['current_insurer'].required = True

            # Validating Car's Year, Make & Model
            year, make = self.data.get("car_year"), self.data.get("car_make")

            if year:
                self.fields['car_make'].choices = CarTreeHelper.get_makes_for_year(year)

            if make:
                self.fields['car_model'].choices = CarTreeHelper.get_models_and_trims_for_year_and_make(year, make)

    def clean(self):
        if self.cleaned_data["years_without_claim"] == NO_CLAIMS_CANT_REMEMBER:
            self.cleaned_data["claim_certificate_available"] = False

    def clean_contact_number(self):
        data = self.cleaned_data["contact_number"]

        if data:
            if not is_valid_number(data):
                raise forms.ValidationError("Invalid phone number")

            return normalize_phone_number(data)

        return data
