from felix.constants import CAR_YEARS_LIST
from motorinsurance_shared.models import CarTrim, CarMake


class CarTreeHelper:
    @classmethod
    def get_years_list(cls):
        return [
                   ("", ""),
               ] + CAR_YEARS_LIST

    @classmethod
    def get_makes_for_year(cls, year):
        """Returns a list of car makes that are available for the given year.

        Previously we used to only return the list of makes for car that were available in the given year. However
        we now break that link so the clients have more flexibility. This will let us increase the list of years
        available without needing to have cars available in those years. The clients can select a car model and
        use any custom car name."""
        return list(CarMake.objects.order_by('name').values_list('id', 'name'))

    @classmethod
    def get_models_and_trims_for_year_and_make(cls, year, make):
        available_trims = (
            CarTrim.objects.filter(year=year, model__make_id=make, is_active=True).select_related("model").order_by(
                "model__name", "title"
            ).distinct("model__name", "title")
        )

        return [
            (trim.pk, "{} {}".format(trim.model.name, trim.title))
            for trim in available_trims
        ]


def is_license_age_more_than(license_age_choice, months_to_compare):
    if not license_age_choice:
        return False

    age_choice_to_comp = {
        "less than 6 months": lambda x: 6 > x,
        "less than 1 year": lambda x: 12 > x,
        "less than 2 years": lambda x: 24 > x,
        "more than 2 years": lambda x: True  # We assume a license more than 2 years fulfills all conditions for Lic age
    }

    comp_func = age_choice_to_comp[license_age_choice]
    return comp_func(months_to_compare)


def add_two_license_ages(age1, age2):
    age_choice_to_months = {
        "less than 6 months": 0,
        "less than 1 year": 6,
        "less than 2 years": 12,
        "more than 2 years": 24
    }

    months_to_age_choice = (
        (lambda x: 6 > x, "less than 6 months"),
        (lambda x: 12 > x, "less than 1 year"),
        (lambda x: 24 > x, "less than 2 years"),
        (lambda x: True, "more than 2 years")
    )

    total_age = age_choice_to_months.get(age1, 0) + age_choice_to_months.get(age2, 0)

    for comp, age_choice in months_to_age_choice:
        if comp(total_age):
            return age_choice


def is_ncd_more_than(ncd_choice, years_to_compare):
    if not ncd_choice:
        return False

    ncd_choice_to_comp = {
        "unknown": lambda x: False,
        "never": lambda x: False,
        "this year": lambda x: x < 1,
        "last year": lambda x: x < 2,
        "2 years ago": lambda x: x < 3,
        "3 years ago": lambda x: x < 4,
        "4 years ago": lambda x: x < 5,
        "5 years or more": lambda x: True,  # Assume this is the same as never having had an accident
    }

    return ncd_choice_to_comp[ncd_choice](years_to_compare)
