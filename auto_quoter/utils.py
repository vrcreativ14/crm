def passes_common_auto_quoting_checks(deal, form_data):
    if deal.date_of_first_registration:
        year_of_manufacture = int(deal.car_year)
        date_of_registration_year = deal.date_of_first_registration.year

        if abs(year_of_manufacture - date_of_registration_year) > 2:
            return (
                False,
                'The difference between the year of manufacture and the date of registration is greater than 2 years.'
            )

    return True, ''


class AutoQuoterResponse:
    def __init__(self, ok, message, premium=None, deductible=None, extra=None):
        self.ok = ok
        self.message = message
        self.extra = extra

        try:
            self.premium = float(premium)
        except (ValueError, TypeError):
            self.premium = 0.0
        try:
            self.deductible = float(deductible)
        except (ValueError, TypeError):
            self.deductible = 0.0
