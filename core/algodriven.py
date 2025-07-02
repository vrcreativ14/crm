"""AlgoDriven Pricing API"""
import requests

from django.conf import settings


class AlgoDriven:
    FREE_EVALUATIONS = 20

    def __init__(self):
        self.api_url = 'https://algodriven.io/v1/gccpriceguide'
        self.api_key = settings.ALGODRIVEN['API_KEY']

    def get_pricing(self, adcode, nonGCC=0, km=None):
        headers = {
            'Authorization': self.api_key,
            'content-type': 'application/x-www-form-urlencoded'
        }

        data = {
            'adcode': adcode,
            'nonGCC': nonGCC,
            'market': 'UAE'
        }

        if km:
            data['km'] = km

        return requests.post(self.api_url, data=data, headers=headers)
