from django.db.models import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

from felix.constants import CAR_YEARS_LIST, COUNTRIES, FIELD_LENGTHS, EMIRATES_LIST
from motorinsurance.constants import LEAD_TYPES, TOP_TIER_INSURERS, INSURANCE_TYPES, LICENSE_AGE_LIST, NO_CLAIMS
from motorinsurance_shared.models import CarMake, CarTrim


class Lead(models.Model):
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE)

    name = models.CharField(max_length=FIELD_LENGTHS['name'])
    email = models.EmailField(max_length=FIELD_LENGTHS['email'])
    contact_number = models.CharField(max_length=FIELD_LENGTHS['email'], blank=True)

    lead_type = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=LEAD_TYPES)

    car_year = models.CharField(max_length=4, choices=CAR_YEARS_LIST)
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    car_trim = models.ForeignKey(CarTrim, null=True, on_delete=models.SET_NULL)

    current_insurer = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=TOP_TIER_INSURERS)
    current_insurance_type = models.CharField(
        max_length=FIELD_LENGTHS['char_choices'], choices=INSURANCE_TYPES, blank=True)

    date_of_first_registration = models.DateField(null=True)
    place_of_registration = models.CharField(max_length=2, choices=EMIRATES_LIST)

    vehicle_insured_value = models.DecimalField(max_digits=10, decimal_places=2)

    dob = models.DateField()
    nationality = models.CharField(max_length=2, choices=COUNTRIES)

    first_license_country = models.CharField(max_length=2, choices=COUNTRIES)
    first_license_age = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=LICENSE_AGE_LIST)
    uae_license_age = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=LICENSE_AGE_LIST)

    years_without_claim = models.CharField(max_length=FIELD_LENGTHS['char_choices'], choices=NO_CLAIMS)
    claim_certificate_available = models.BooleanField(default=False)

    # Car details
    private_car = models.BooleanField(default=True)
    car_unmodified = models.BooleanField(default=True)
    car_gcc_spec = models.BooleanField(default=True)

    custom_car_name = models.CharField(max_length=FIELD_LENGTHS['name'], blank=True)

    created_on = models.DateField(auto_now_add=True)
    updated_on = models.DateField(auto_now=True)

    meta_info = JSONField(default=list, encoder=DjangoJSONEncoder)

    def get_car_title(self):
        if self.custom_car_name and self.car_trim is None:
            car_title = "{} - {} - {}".format(self.car_make.name, self.custom_car_name, self.car_year)
        else:
            car_title = str(self.car_trim)

        return car_title

    def get_title(self):
        name = self.name
        return "{} - {}".format(name, self.get_car_title())

    def __str__(self):
        return "[{}: {}]".format(self.id, self.name)
