"""Intercom API"""
import requests

from django.conf import settings


class Intercom:
    def __init__(self):
        self.base_url = 'https://api.intercom.io/'
        self.headers = {
            'Authorization': 'Bearer {}'.format(settings.INTERCOM['ACCESS_TOKEN']),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_contact_by_email_and_id(self, email, user_id):
        query = {
            "query": {
                "operator": "AND",
                "value": [{
                    "field": "external_id",
                    "operator": "=",
                    "value": str(user_id)
                }, {
                    "field": "email",
                    "operator": "=",
                    "value": email
                }]
            }
        }

        data = requests.post(self.base_url + 'contacts/search', headers=self.headers, json=query)
        json_data = data.json()

        if json_data['type'] == 'list' and json_data['total_count']:
            return json_data['data'][0]

        return None

    def update_contact(self, user_id, user_data):
        res = requests.put('{}contacts/{}'.format(self.base_url, user_id), headers=self.headers, json=user_data)

        if res.status_code == 200:
            return res.json()

        return None
