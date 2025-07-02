from django import forms
from django.utils.text import camel_case_to_spaces
from pycountry import countries

from auto_quoter.aman import AmanAutoQuoter, AmanApiAutoQuoter
from auto_quoter.constants import NewIndiaVehicleTypes, TokioMarineVehicleTypes, AmanVehicleTypes, \
    InsuranceHouseVehicleTypes
from auto_quoter.drools_api import DroolsAutoQuoter
from auto_quoter.exceptions import AutoQuoterException
from auto_quoter.insurance_house import InsuranceHouseAutoQuoter
from auto_quoter.new_india import NewIndiaAutoQuoter
from auto_quoter.oic import OICAutoQuoter
from auto_quoter.qic import QICAutoQuoter, mappings
from auto_quoter.tokio_marine import TokioMarineAutoQuoter
from auto_quoter.uic import UICAutoQuoter
from auto_quoter.watania import WataniaAutoQuoter
from motorinsurance.constants import LEAD_TYPES_USED_CAR
from motorinsurance.models import Deal


class AutoQuoteBaseForm(forms.Form):
    auto_quoter = None

    def __init__(self, deal, *args, **kwargs):
        super(AutoQuoteBaseForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

        self._deal = deal

        if hasattr(self, 'deal_specific_setup'):
            self.deal_specific_setup(deal)


class SalamaForm(AutoQuoteBaseForm):
    auto_quoter = DroolsAutoQuoter

    is_suv = forms.BooleanField(required=False, initial=False, label='Is an SUV?')
    is_sports = forms.BooleanField(required=False, initial=False, label='Is Sports?')


class QICForm(AutoQuoteBaseForm):
    template_name = 'motorinsurance/auto_quote_product_forms/qic.djhtml'

    auto_quoter = QICAutoQuoter

    VEHICLE_TYPES = (
        (None, "Select vehicle type"),
        ("1001", "Saloon"),
        ("1002", "4 X 4"),
        ("1003", "Station"),
        ("1004", "Coupe"),
        ("1005", "Bus"),
        ("1006", "Van upto 3 Ton"),
        ("1007", "Pickup upto 2.5 Ton"),
        ("1008", "Pickup > 2.5 Ton"),
        ("1009", "Ambulance"),
        ("1010", "Equipment upto 3 Ton"),
        ("1011", "Sports"),
        ("1012", "Motor Bikes Up to 200 CC"),
        ("1013", "Money Container"),
        ("1014", "Hatchback"),
        ("1015", "Heavy Vehicles upto 3 ton"),
        ("1016", "Heavy Vehicles > 3 ton"),
        ("1017", "Box to Vehicle upto 3 Ton"),
        ("1018", "Box to Vehicle > 3 Ton"),
        ("1019", "Freezer to Vehicle upto 3 Ton"),
        ("1020", "Freezer to Vehicle > 3 Ton"),
        ("1021", "Van > 3 Ton"),
        ("1022", "Equipment > 3 Ton"),
        ("1023", "Motor Bikes > 200 CC"),
    )

    CYLINDERS = (
        (None, "Select number of cylinders"),
        ("1001", "1"),
        ("1002", "2"),
        ("1003", "3"),
        ("1004", "4"),
        ("1005", "5"),
        ("1006", "6"),
        ("1007", "8"),
        ("1008", "10"),
        ("1009", "12"),
        ("1010", "No Cylinders"),
    )

    YES_NO = (
        (None, 'Select an option'),
        ('1', 'Yes'),
        ('0', 'No')
    )

    insured_value = forms.DecimalField(max_digits=10, decimal_places=2)
    vehicle_type = forms.ChoiceField(choices=VEHICLE_TYPES)
    model = forms.ChoiceField()
    cylinders = forms.ChoiceField(choices=CYLINDERS, initial='1004')
    seating_capacity = forms.IntegerField(label='Seating capacity (including driver)', min_value=2, max_value=15,
                                          initial=5)
    previous_insurance_valid = forms.ChoiceField(choices=YES_NO, initial='1')
    total_loss = forms.ChoiceField(choices=YES_NO, initial='0')

    def get_country_mapping_list(self):
        country_map = list()

        for country_code, qic_country_code in mappings.country_mapping.items():
            country_name = countries.get(alpha_2=country_code).name
            country_map.append(
                (qic_country_code, country_name)
            )

        return country_map

    def deal_specific_setup(self, deal):
        models = QICAutoQuoter.deal_to_car_model_choices(deal)
        self.fields['model'].choices = [[None, "Select model"]] + models
        self.fields['insured_value'].initial = deal.vehicle_insured_value

    def customer_nationality_code(self):
        return self.auto_quoter.customer_to_nationality_code(self._deal.customer)

    def customer_no_claims_choice_to_years(self):
        return dict([
            ("unknown", 0),
            ("never", 0),
            ("this year", 0),
            ("last year", 1),
            ("2 years ago", 2),
            ("3 years ago", 3),
            ("4 years ago", 4),
            ("5 years or more", 5),
        ]).get(self._deal.years_without_claim, 0)

    def no_claims(self):
        if self._deal.claim_certificate_available:
            return self.customer_no_claims_choice_to_years()
        else:
            return 0

    def no_claims_self_dec(self):
        if not self._deal.claim_certificate_available:
            return self.customer_no_claims_choice_to_years()
        else:
            return 0

    def gulf_driving_experience(self):
        return {
            "less than 6 months": 0,
            "less than 1 year": 0,
            "less than 2 years": 1,
            "more than 2 years": 2,
        }.get(self._deal.customer.motorinsurancecustomerprofile.uae_license_age, 0)


class OICForm(AutoQuoteBaseForm):
    YES_NO_CHOICES = (
        (None, 'Select an option'),
        ('yes', 'Yes'),
        ('no', 'No'),
    )

    auto_quoter = OICAutoQuoter

    model = forms.ChoiceField()
    specification = forms.ChoiceField()
    vehicle = forms.ChoiceField()
    insured_value = forms.DecimalField(max_digits=10, decimal_places=2)

    mortgaged = forms.ChoiceField(label='Is there a bank loan on this car?', choices=YES_NO_CHOICES)
    currently_in_cover = forms.ChoiceField(label='Is the car currently insured?', choices=YES_NO_CHOICES)

    def clean_boolean_choices(self, choice):
        return choice == 'yes'

    def clean_mortgaged(self):
        return self.clean_boolean_choices(self.cleaned_data['mortgaged'])

    def clean_currently_in_cover(self):
        return self.clean_boolean_choices(self.cleaned_data['currently_in_cover'])

    def __init__(self, deal, *args, **kwargs):
        super(OICForm, self).__init__(deal, *args, **kwargs)

        self.fields['specification'].widget.attrs['disabled'] = "disabled"
        self.fields['vehicle'].widget.attrs['disabled'] = "disabled"

    def deal_specific_setup(self, deal):
        self.fields['insured_value'].initial = deal.vehicle_insured_value

        auto_quoter = self.auto_quoter()
        auto_quoter.setup_for_company(deal.company)

        try:
            models = auto_quoter.get_car_models_for_deal(deal)
            self.fields['model'].choices = [(None, 'Select Model')] + [
                (m['id'], m['description']) for m in models
            ]
        except AutoQuoterException:
            self.fields['model'].choices = [(None, 'No models available for this make')]
            return

        if 'model' in self.data:
            model_id = self.data['model']
            specs = auto_quoter.get_car_specs_for_model(model_id)
            self.fields['specification'].choices = [(None, 'Select Car Spec')] + [
                (s['id'], s['description']) for s in specs
            ]

            if 'specification' in self.data:
                spec_id = self.data['specification']
                vehicles = auto_quoter.get_vehicles_for_spec(spec_id)
                self.fields['vehicle'].choices = [(None, 'Select Car')] + [
                    (v['id'], v['description']) for v in vehicles
                ]


class NewIndiaForm(AutoQuoteBaseForm):
    auto_quoter = NewIndiaAutoQuoter

    VEHICLE_TYPES = (
        (None, 'Please select vehicle type'),
        (NewIndiaVehicleTypes.Sports.value, 'Coupe, 2 Door Vehicle, Sports & High Performance'),
        (NewIndiaVehicleTypes.Saloon.value, 'Saloon, Sedan, Hatchback'),
        (NewIndiaVehicleTypes.FourByFour.value, '4x4, SUV, MPV, Station'),
        (NewIndiaVehicleTypes.Pickups3TonsOrLess.value, 'Pickups, Vans up to 3 tons'),
        (NewIndiaVehicleTypes.Pickups3TonsOrMore.value, 'Pickups, Vans above 3 tons'),
        (NewIndiaVehicleTypes.PrivateBus.value, 'Private Bus'),
        (NewIndiaVehicleTypes.SchoolBus.value, 'School Bus'),
        (NewIndiaVehicleTypes.PassengerTransport.value, 'Passenger Transport'),
    )

    vehicle_type = forms.ChoiceField(choices=VEHICLE_TYPES)
    is_renewal = forms.BooleanField(label='Is this car currently insured with New India?', required=False)
    is_chinese_manufacturer = forms.BooleanField(label='Chinese Manufacturer?', required=False)

    insured_value = forms.IntegerField(min_value=1)

    def deal_specific_setup(self, deal):
        self.fields['insured_value'].initial = deal.vehicle_insured_value

    def clean_vehicle_type(self):
        try:
            return NewIndiaVehicleTypes(self.cleaned_data['vehicle_type'])
        except ValueError:
            raise forms.ValidationError('Unable to map vehicle_type to a correct value')


class TokioMarineForm(AutoQuoteBaseForm):
    auto_quoter = TokioMarineAutoQuoter

    VEHICLE_TYPES = (
        (None, 'Please select vehicle type'),
        (TokioMarineVehicleTypes.Saloon.value, 'Saloon, Sedan, Hatchback'),
        (TokioMarineVehicleTypes.FourByFour.value, '4x4, SUV, MPV, Station'),
        (TokioMarineVehicleTypes.Pickups3TonsOrLess.value, 'Pickups, Vans up to 3 tons'),
        (TokioMarineVehicleTypes.Pickups3TonsOrMore.value, 'Pickups, Vans above 3 tons'),
        (TokioMarineVehicleTypes.Bus.value, 'Buses'),
    )

    vehicle_type = forms.ChoiceField(choices=VEHICLE_TYPES)
    is_renewal = forms.BooleanField(label='Is this car currently insured with Tokio Marine?', required=False)
    insured_value = forms.IntegerField(min_value=1)

    def deal_specific_setup(self, deal):
        self.fields['insured_value'].initial = deal.vehicle_insured_value

    def clean_vehicle_type(self):
        try:
            return TokioMarineVehicleTypes(self.cleaned_data['vehicle_type'])
        except ValueError:
            raise forms.ValidationError('Unable to map vehicle_type to a correct value')


class UICForm(AutoQuoteBaseForm):
    auto_quoter = UICAutoQuoter

    VEHICLE_TYPES = (
        (None, 'Please select vehicle type'),
        ('saloon', 'Saloon'),
        ('station_wagon', 'Station Wagon'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    )

    vehicle_type = forms.ChoiceField(choices=VEHICLE_TYPES)
    insured_value = forms.IntegerField(min_value=1)

    previous_repair_condition_is_agency = forms.BooleanField(
        required=False,
        label='Is previous repair condition "Agency Repair"?'
    )

    def deal_specific_setup(self, deal):
        self.fields['insured_value'].initial = deal.vehicle_insured_value


class InsuranceHouseForm(AutoQuoteBaseForm):
    auto_quoter = InsuranceHouseAutoQuoter

    VEHICLE_TYPES = [
                        (None, 'Please select a vehicle type'),
                    ] + [
                        (type.value, type.value) for type in InsuranceHouseVehicleTypes
                    ]

    vehicle_type = forms.ChoiceField(choices=VEHICLE_TYPES)
    insured_value = forms.IntegerField(min_value=1)

    def deal_specific_setup(self, deal):
        self.fields['insured_value'].initial = deal.vehicle_insured_value

    def clean_vehicle_type(self):
        return InsuranceHouseVehicleTypes(self.cleaned_data['vehicle_type'])


class AmanForm(AutoQuoteBaseForm):
    auto_quoter = AmanAutoQuoter

    vehicle_type = forms.ChoiceField(choices=(
        (AmanVehicleTypes.Saloon.value, 'Saloon'),
        (AmanVehicleTypes.Coupe.value, 'Coupe'),
        (AmanVehicleTypes.Sports.value, 'Sports'),
        (AmanVehicleTypes.FourByFour.value, 'Station, SUV, 4WD'),
        (AmanVehicleTypes.Pickup3TonOrVan.value, 'Pick-up up to 3 Tons and Vans up to 5 seats'),
        (AmanVehicleTypes.Pickup5TonOrTruck.value, 'Pick-up & Truck above 3 Tons'),
        (AmanVehicleTypes.Bus.value, 'Bus'),
    ))
    insured_value = forms.IntegerField(min_value=1)

    previous_year_agency = forms.BooleanField(required=False,
                                              help_text='Only required for renewal/used vehicles.',
                                              label='Is previous repair condition "Agency Repair"?')

    def clean_vehicle_type(self):
        try:
            return AmanVehicleTypes(self.cleaned_data['vehicle_type'])
        except ValueError:
            raise forms.ValidationError('Unable to map vehicle_type to a correct value')

    def deal_specific_setup(self, deal):
        self.fields['insured_value'].initial = deal.vehicle_insured_value


class WataniaForm(AutoQuoteBaseForm):
    auto_quoter = WataniaAutoQuoter

    vehicle_type = forms.ChoiceField(choices=(
        ('SALOON', 'Saloon'),
        ('4WD', '4WD'),
        ('SPORTS', 'Sports'),
        ('COUPE', 'Coupe'),
    ))
    insured_value = forms.IntegerField(min_value=1)

    def deal_specific_setup(self, deal):
        self.fields['insured_value'].initial = deal.vehicle_insured_value


class AmanApiCarDetailsForm(forms.Form):
    chassis_number = forms.CharField(min_length=17, max_length=17)


def enum_to_choices(enum):
    return (('', 'Select an option'),) + tuple(
        (x.value, camel_case_to_spaces(x.name)) for x in enum
    )


class AmanApiForm(AutoQuoteBaseForm):
    template_name = 'motorinsurance/auto_quote_product_forms/aman_api.djhtml'
    auto_quoter = AmanApiAutoQuoter

    sum_insured = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            "v-model": "sumInsured"
        })
    )

    policy_class = forms.ChoiceField(choices=enum_to_choices(AmanApiAutoQuoter.PolicyClass))
    used_vehicle = forms.ChoiceField(
        choices=enum_to_choices(AmanApiAutoQuoter.UsedVehicle), label='Is used vehicle?',
        widget=forms.Select(attrs={
            'v-model': 'usedVehicle',
            "class": "form-control"
        })
    )
    agency_repair = forms.ChoiceField(
        choices=enum_to_choices(AmanApiAutoQuoter.AgencyRepair),
    )
    vehicle_usage = forms.ChoiceField(
        choices=enum_to_choices(AmanApiAutoQuoter.VehicleUsage)
    )

    vehicle_code = forms.CharField(
        widget=forms.TextInput(attrs={
            ":value": "vehicleCode"
        })
    )
    body_code = forms.CharField(
        widget=forms.TextInput(attrs={
            ":value": "bodyCode"
        })
    )
    year_manufactured = forms.CharField(
        widget=forms.TextInput(attrs={
            ":readonly": "hasYearManufactured",
            ":value": "yearManufactured"
        })
    )

    aaa = forms.ChoiceField(
        choices=enum_to_choices(AmanApiAutoQuoter.AAA),
        initial=AmanApiAutoQuoter.AAA.No.value,
        label='Include AAA benefit?'
    )
    pabd = forms.ChoiceField(
        choices=enum_to_choices(AmanApiAutoQuoter.PABD),
        initial=AmanApiAutoQuoter.PABD.Yes.value,
        label='Include PAB driver benefit?'
    )
    pabp = forms.ChoiceField(
        choices=enum_to_choices(AmanApiAutoQuoter.PABP),
        initial=AmanApiAutoQuoter.PABP.Yes.value,
        label='Include PAB passenger benefit?'
    )
    off_road = forms.ChoiceField(
        choices=enum_to_choices(AmanApiAutoQuoter.OffRoad),
        initial=AmanApiAutoQuoter.OffRoad.No.value,
        label='Include off road cover?'
    )
    oman_cover = forms.ChoiceField(
        choices=enum_to_choices(AmanApiAutoQuoter.OmanCover),
        initial=AmanApiAutoQuoter.OmanCover.No.value,
        label='Include coverage in Oman?'
    )
    license_city = forms.ChoiceField(
        choices=enum_to_choices(AmanApiAutoQuoter.Cities)
    )
    license_registration_date = forms.DateField(
        input_formats=['%Y-%m-%d']
    )

    emirate_of_registration = forms.ChoiceField(
        choices=enum_to_choices(AmanApiAutoQuoter.Cities)
    )
    first_registration_date = forms.DateField(
        input_formats=['%Y-%m-%d']
    )
    last_registration_date = forms.DateField(
        input_formats=['%Y-%m-%d']
    )

    seats = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            ":readonly": "hasSeats",
            ":value": "seats"
        })
    )
    weight = forms.FloatField(label='Weight (in tons)')
    cylinders = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            ":readonly": "hasCylinders",
            ":value": "cylinders"
        })
    )

    discount_percentage = forms.CharField(label='Discount Percentage', required=False)

    def deal_specific_setup(self, deal: Deal):
        if deal.lead_type == LEAD_TYPES_USED_CAR:
            self.fields['used_vehicle'].initial = AmanApiAutoQuoter.UsedVehicle.Yes.value

        if deal.private_car:
            self.fields['vehicle_usage'].initial = AmanApiAutoQuoter.VehicleUsage.Private.value
        else:
            self.fields['vehicle_usage'].initial = AmanApiAutoQuoter.VehicleUsage.Commercial.value

        if deal.date_of_first_registration:
            self.fields['first_registration_date'].initial = deal.date_of_first_registration.strftime('%d-%m-%Y')
