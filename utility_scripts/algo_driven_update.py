import csv

from motorinsurance_shared.models import CarTrim, CarMake, CarModel

algodriven_to_our_make_mapping = {
    'Mercedes-AMG': 'Mercedes-Benz',
    'Seat': 'SEAT'
}

with open('/home/ubuntu/ADData-202008-01.csv') as f:
    r = csv.DictReader(f)
    next(r)
    for row in r:
        ag_id = row['AlgoDriven Code']
        year = row['Year']
        make = row['Make']
        model = row['Model']
        description = row['Description']
        variant = row['Variant']
        series = row['Series']
        body = row['Body']
        doors = row['Doors']
        liters = row['Litres']
        cylinders = row['Cylinders']
        hp = row['HP']
        transmission = row['Transmission']
        drive = row['Drive']
        fuel = row['Fuel']
        seats = row['Seats']

        make = make.strip()
        model = model.strip()

        make = algodriven_to_our_make_mapping.get(make, make)

        try:
            car_make = CarMake.objects.get(name=make)
        except CarMake.DoesNotExist:
            create = input(f"Car make {make} does not exist. Should I create a new one?")
            if create == "yes":
                car_make = CarMake.objects.create(name=make)
            else:
                raise

        car_model, created = CarModel.objects.get_or_create(make=car_make, name=model)
        if created:
            print(f"Created a new model: {make} {model}")

        if CarTrim.objects.filter(algo_driven_id=ag_id):
            car_trim = CarTrim.objects.get(algo_driven_id=ag_id)
        else:
            trim_name = f'{variant} {liters}L {doors} Doors {body} - {transmission}'

            car_trim = CarTrim(
                year=year,
                model=car_model,
                title=trim_name,
                algo_driven_id=ag_id
            )

            print(f"Created a new trim: {year} {make} {model}")

        car_trim.algo_driven_data = {
            'variant': variant,
            'body': body,
            'doors': doors,
            'liters': liters,
            'cylinders': cylinders,
            'horse_power': hp,
            'transmission': transmission,
            'drive': drive,
            'fuel': fuel,
            'seats': seats
        }
        car_trim.save()