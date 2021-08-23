import csv

from motorinsurance_shared.models import CarTrim

with open('/home/ubuntu/ad_cleaned.csv') as f:
    r = csv.reader(f)
    next(f)

    for row in r:
        ad_id, year, make, model, description, variant, series, body, doors, liters, cylinders, hp, transmission, drive, fuel, seats = row

        try:
            car_trim = CarTrim.objects.get(algo_driven_id=ad_id)
        except CarTrim.DoesNotExist:
            print("CarTrim not found for AD ID {}".format(ad_id))
            continue

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