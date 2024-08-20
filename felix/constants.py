import pycountry
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from felix.storages import PublicAzureStorage
from datetime import datetime

COUNTRIES = list(
    (country.alpha_2, country.name) for country in pycountry.countries
)

CURRENCIES = (
    ('AED', 'Dhs'),
    ('GBP', '£'),
    ('USD', '$'),
)

UAE_COUNTRY_CODE = 'AE'

GENDER_MALE = 'm'
GENDER_FEMALE = 'f'
GENDER_CHOICES = (
    (GENDER_MALE, 'Male'),
    (GENDER_FEMALE, 'Female'),
)

SORTING_CHOICES = (
    ('', 'Created on (desc)'),
    ('created_on_asc', 'Created on (asc)'),
    ('updated_on_desc', 'Updated on (desc)'),
    ('updated_on_asc', 'Updated on (asc)'),
)

EMIRATE_DUBAI = "DU"
EMIRATE_ABU_DHABI = "AD"
EMIRATE_SHARJAH = "SJ"
EMIRATE_AJMAN = "AJ"
EMIRATE_RAS_AL_KHAIMAH = "RK"
EMIRATE_FUJAIRAH = "FJ"
EMIRATE_UMM_AL_QUWAIN = "UQ"

EMIRATES_LIST = (
    (EMIRATE_DUBAI, "Dubai"),
    (EMIRATE_ABU_DHABI, "Abu Dhabi"),
    (EMIRATE_SHARJAH, "Sharjah"),
    (EMIRATE_AJMAN, "Ajman"),
    (EMIRATE_RAS_AL_KHAIMAH, "Ras Al Khaimah"),
    (EMIRATE_FUJAIRAH, "Fujairah"),
    (EMIRATE_UMM_AL_QUWAIN, "Umm Al Quwain"),
)

MARITAL_STATUS_MARRIED = 'married'
MARITAL_STATUS_SINGLE = 'single'
MARITAL_STATUS_LIST = (
    (MARITAL_STATUS_MARRIED, "Married"),
    (MARITAL_STATUS_SINGLE, "Unmarried"),
)

USER_ROLES = (
    ('admin', 'Admin User'),
    ('user', 'Regular User'),
    ('producer', 'Producer')
)

if settings.USE_AZURE:
    PUBLIC_STORAGE = PublicAzureStorage()
else:
    PUBLIC_STORAGE = FileSystemStorage()

INVITATION_EXPIRE_DAYS = 7
INVITATION_SECRET_KEY = 'key.felix.insure'

FIELD_LENGTHS = {
    'email': 250,
    'phone': 25,
    'name': 500,
    'address': 1000,
    'website': 250,
    'email_subject': 1000,
    'meta': 1000,
    'title': 1000,

    'api_keys': 100,

    'char_choices': 50,  # So we get meaningful choice values instead of codes in the DB,
    'reference_numbers': 50,

    'file': 1000,

    'emirate': 2,

    'workspace': 2,
}

CAR_YEARS_LIST = [
    (str(year), year) for year in range(datetime.now().year + 1, 1993, -1)
]

AGE_YEARS = [(str(x), str(x)) for x in range(18, 71)] + [('71', '70+')]

ITEMS_PER_PAGE = 30  # Default pagination option

EXPIRED_QUOTE_EXTENSION_DAYS = 15

DEFAULT_TIMESLOT = '10:00'
TIMESLOTS_CHOICES = (
    ('00:00', '00:00 AM'),
    ('00:15', '00:15 AM'),
    ('00:30', '00:30 AM'),
    ('00:45', '00:45 AM'),
    ('01:00', '01:00 AM'),
    ('01:15', '01:15 AM'),
    ('01:30', '01:30 AM'),
    ('01:45', '01:45 AM'),
    ('02:00', '02:00 AM'),
    ('02:15', '02:15 AM'),
    ('02:30', '02:30 AM'),
    ('02:45', '02:45 AM'),
    ('03:00', '03:00 AM'),
    ('03:15', '03:15 AM'),
    ('03:30', '03:30 AM'),
    ('03:45', '03:45 AM'),
    ('04:00', '04:00 AM'),
    ('04:15', '04:15 AM'),
    ('04:30', '04:30 AM'),
    ('04:45', '04:45 AM'),
    ('05:00', '05:00 AM'),
    ('05:15', '05:15 AM'),
    ('05:30', '05:30 AM'),
    ('05:45', '05:45 AM'),
    ('06:00', '06:00 AM'),
    ('06:15', '06:15 AM'),
    ('06:30', '06:30 AM'),
    ('06:45', '06:45 AM'),
    ('07:00', '07:00 AM'),
    ('07:15', '07:15 AM'),
    ('07:30', '07:30 AM'),
    ('07:45', '07:45 AM'),
    ('08:00', '08:00 AM'),
    ('08:15', '08:15 AM'),
    ('08:30', '08:30 AM'),
    ('08:45', '08:45 AM'),
    ('09:00', '09:00 AM'),
    ('09:15', '09:15 AM'),
    ('09:30', '09:30 AM'),
    ('09:45', '09:45 AM'),
    ('10:00', '10:00 AM'),
    ('10:15', '10:15 AM'),
    ('10:30', '10:30 AM'),
    ('10:45', '10:45 AM'),
    ('11:00', '11:00 AM'),
    ('11:15', '11:15 AM'),
    ('11:30', '11:30 AM'),
    ('11:45', '11:45 AM'),
    ('12:00', '12:00 PM'),
    ('12:15', '12:15 PM'),
    ('12:30', '12:30 PM'),
    ('12:45', '12:45 PM'),
    ('13:00', '01:00 PM'),
    ('13:15', '01:15 PM'),
    ('13:30', '01:30 PM'),
    ('13:45', '01:45 PM'),
    ('14:00', '02:00 PM'),
    ('14:15', '02:15 PM'),
    ('14:30', '02:30 PM'),
    ('14:45', '02:45 PM'),
    ('15:00', '03:00 PM'),
    ('15:15', '03:15 PM'),
    ('15:30', '03:30 PM'),
    ('15:45', '03:45 PM'),
    ('16:00', '04:00 PM'),
    ('16:15', '04:15 PM'),
    ('16:30', '04:30 PM'),
    ('16:45', '04:45 PM'),
    ('17:00', '05:00 PM'),
    ('17:15', '05:15 PM'),
    ('17:30', '05:30 PM'),
    ('17:45', '05:45 PM'),
    ('18:00', '06:00 PM'),
    ('18:15', '06:15 PM'),
    ('18:30', '06:30 PM'),
    ('18:45', '06:45 PM'),
    ('19:00', '07:00 PM'),
    ('19:15', '07:15 PM'),
    ('19:30', '07:30 PM'),
    ('19:45', '07:45 PM'),
    ('20:00', '08:00 PM'),
    ('20:15', '08:15 PM'),
    ('20:30', '08:30 PM'),
    ('20:45', '08:45 PM'),
    ('21:00', '09:00 PM'),
    ('21:15', '09:15 PM'),
    ('21:30', '09:30 PM'),
    ('21:45', '09:45 PM'),
    ('22:00', '10:00 PM'),
    ('22:15', '10:15 PM'),
    ('22:30', '10:30 PM'),
    ('22:45', '10:45 PM'),
    ('23:00', '11:00 PM'),
    ('23:15', '11:15 PM'),
    ('23:30', '11:30 PM'),
    ('23:45', '11:45 PM'),
)

WORKSPACE_MOTOR = 'MT'
WORKSPACE_MORTGAGE = 'MG'
WORKSPACE_HEALTH_INSURANCE = 'HI'

WORKSPACES = (
    (WORKSPACE_MOTOR, 'Motor'),
    (WORKSPACE_MORTGAGE, 'Mortgage'),
    (WORKSPACE_HEALTH_INSURANCE, 'Health'),
)

ALGODRIVEN_FREE_EVALUATIONS = 20

PAYMENT_LINK = "payment_link"
BANK_DETAILS = "bank_details"
MULTIPLE_MODES = "multiple"

PAYMENT_MODES = (
    (PAYMENT_LINK, 'Payment Link'),
    (BANK_DETAILS, 'Bank Details'),
    (MULTIPLE_MODES, 'Multiple'),
)
