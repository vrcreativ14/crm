import re
import csv

import os
from django.core.management import BaseCommand
from motorinsurance_shared.models import CarTrim, CarModel, CarMake
from felix.constants import CAR_YEARS_LIST


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            dest="clear",
            default=False,
            help="Clear models DB before adding new data"
        )
        parser.add_argument(
            '--up-to',
            action='store',
            dest='up_to',
            help='Load cars up to this year'
        )

    def handle(self, *args, **options):
        if options["clear"]:
            if input("Clearing all current data. Press Y to continue [y/N]: ").lower() != "y":
                self.stderr.write("Not taking any action\n")
                return

            self.stderr.write("Deleting all existing car data\n")
            CarTrim.objects.all().delete()
            CarModel.objects.all().delete()
            CarMake.objects.all().delete()

        file_path = os.path.join(os.path.dirname(__file__), 'mmt_tree.csv')
        with open(file_path, encoding="utf-8") as _if:
            reader = csv.reader(_if)
            next(reader)  # Header
            for row in reader:
                try:
                    year, make, model, trim, seats, doors = row
                    make = re.sub(r"\s+", " ", make)
                    model = re.sub(r"\s+", " ", model)
                    trim = re.sub(r"\s+", " ", trim)

                    year = int(year)
                except:
                    self.stderr.write(str(row), ending="\n")
                    raise

                if str(year) not in dict(CAR_YEARS_LIST):
                    self.stdout.write("Year {} not in list. Skipping rest of file".format(year))
                    break

                if 'up_to' in options:
                    if year < int(options['up_to']):
                        self.stdout.write('Year {} less than the up to option. Skipping rest'.format(
                            year
                        ))
                        break

                if CarMake.objects.filter(name=make).exists():
                    car_make = CarMake.objects.get(name=make)
                else:
                    car_make = CarMake(name=make)
                    car_make.save()

                if CarModel.objects.filter(name=model, make=car_make).exists():
                    car_model = CarModel.objects.get(name=model, make=car_make)
                else:
                    car_model = CarModel(name=model, make=car_make)
                    car_model.save()

                if CarTrim.objects.filter(model=car_model, year=year, title=trim).exists():
                    self.stdout.write("Trim already exists. Not adding new one. {} {} {}\n".format(car_model.name,
                                                                                                   trim, year))
                else:
                    car_trim = CarTrim(year=year, model=car_model, title=trim)
                    car_trim.save()

                    self.stdout.write("Car trim added: {}\n".format(car_trim))
