from enum import Enum

OIC = 'oic'
QIC = 'qic'
UIC = 'uic'
NEW_INDIA = 'new india'
INSURANCE_HOUSE = 'insurance house'
TOKIO_MARINE = 'tokio marine'
TOKIO_MARINE_API = 'tokio marine api'
AMAN = 'aman'
AMAN_API = 'aman api'
ARABIA = 'arabia'
DNIRC = 'dnirc'
ALITTIHAD = 'al ittihad al watani insurace'
WATANIA = 'watania'
AL_AIN_AHLIA = 'al ain ahlia'
AL_SAGR = 'al sagr'

AUTO_QUOTABLE_INSURERS = (
    (OIC, 'Oman Insurance Company'),
    (QIC, 'Qatar Insurance Company'),
    (UIC, 'Union Insurance Company'),
    (NEW_INDIA, 'New India Insurance'),
    (INSURANCE_HOUSE, 'Insurance House'),
    (TOKIO_MARINE, 'Tokio Marine'),
    (TOKIO_MARINE_API, 'Tokio Marine API'),
    (AMAN, 'Aman'),
    (AMAN_API, 'Aman API'),
    (ARABIA, 'Arabia'),
    (DNIRC, 'DNIRC'),
    (ALITTIHAD, 'Al Ittihad Al Watani Insurance'),
    (WATANIA, 'Watania Insurance'),
    (AL_AIN_AHLIA, 'Al Ain Ahlia Insurance Company'),
    (AL_SAGR, 'Al Sagr Insurance')
)


class NewIndiaVehicleTypes(Enum):
    Sports = 'sports like'
    Saloon = 'saloon like'
    FourByFour = '4x4 like'
    Pickups3TonsOrLess = 'pickups less than 3 tons'
    Pickups3TonsOrMore = 'pickups more than 3 tons'
    PrivateBus = 'private bus'
    SchoolBus = 'school bus'
    PassengerTransport = 'passenger transport'


class TokioMarineVehicleTypes(Enum):
    Saloon = 'saloon'
    FourByFour = '4x4'
    Pickups3TonsOrLess = 'pickups less than 3 tons'
    Pickups3TonsOrMore = 'pickups more than 3 tons'
    Bus = 'bus'


class AmanVehicleTypes(Enum):
    Saloon = 'Saloon'
    Coupe = 'Coupe'
    Sports = 'Sports & High performance'
    FourByFour = '4x4/Station/SUV'
    Pickup3TonOrVan = 'Pick up (3 ton) or Van up to 5 seats'
    Pickup5TonOrTruck = 'Pick up or Trucks (above 3 ton)'
    Bus = 'Bus'


class ArabiaVehicleTypes(Enum):
    Saloon = 'Saloon'
    FourByFour = '4WD'
    Sports = 'Sports & High performance'


class InsuranceHouseVehicleTypes(Enum):
    Saloon = 'Saloon'
    FourByFour = '4WD'
    Pickup3TonOrVan = 'Pick up (3 ton) or Van'
    PickupAbove3TonOrTruck = 'Pick up (above 3 ton), Refrigerator, or Trucks'
    Bus = 'Bus'
    SchoolBus = 'School Bus'
    EquipmentOrHeavy = 'Equipment & Heavy Vehicle'
