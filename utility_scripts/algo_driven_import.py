import csv

from motorinsurance_shared.models import CarMake, CarModel, CarTrim

algodriven_to_our_make_mapping = {
    'Mercedes-AMG': 'Mercedes-Benz',
}

fname = '/home/ubuntu/ad_cleaned.csv'


disabled_makes = set()


def add_car(row):
    (ag_id, year, make, model, description, variant, series, body, doors, liters, cylinders, hp, transmission, drive,
     fuel, seats) = row

    make = algodriven_to_our_make_mapping.get(make, make)

    if CarMake.objects.filter(name__iexact=make).exists():
        car_make = CarMake.objects.get(name__iexact=make)

        if car_make.pk not in disabled_makes:
            disabled_makes.add(car_make.pk)

            print(f"Disabling existing MMT tree for make {car_make.name}")

            car_make.carmodel_set.update(is_active=False)
            CarTrim.objects.filter(model__in=car_make.carmodel_set.all()).update(is_active=False)
    else:
        car_make = CarMake.objects.create(name=make)

    car_model, created = CarModel.objects.get_or_create(make=car_make, name=model)

    trim_name = f'{variant} {liters}L {doors} Doors {body} - {transmission}'

    car_trim = CarTrim.objects.create(
        year=year, model=car_model, title=trim_name, algo_driven_id=ag_id
    )

    return car_trim


with open(fname) as _if:
    r = csv.reader(_if)
    next(r)

    for row in r:
        trim = add_car(row)
        print(trim)