"""Amplitude events"""
import json
import uuid

import requests
from django.conf import settings


class Amplitude:
    EVENTS = {
        'motor_deal_created': 'motor deal created',
        'motor_deal_won': 'motor deal won',
        'motor_quote_created': 'motor quote created',
        'motor_quote_email_sent': 'motor quote email sent',
        'motor_product_quoted': 'motor product quoted',
        'pdf_quote_downloaded': 'pdf quote downloaded',
        'motor_order_created': 'motor order created',
        'motor_policy_saved': 'motor policy saved',
        'policy_text_extracted': 'policy text extracted'
    }

    def __init__(self, request):
        self.api_url = 'https://api.amplitude.com/httpapi'
        self.api_key = settings.AMPLITUDE['API_KEY']
        self.request = request

    def log_event(self, event_type='', properties={}):
        properties['company_id'] = self.request.company.pk
        properties['company_name'] = self.request.company.name

        event = {
            'user_id': uuid.uuid4().hex,
            'device_id': None,
            'event_type': event_type,
            'event_properties': properties
        }

        if self.request.user.pk:
            event['user_id'] = self.request.user.pk

        response = requests.post(
            self.api_url,
            data=[
                ('api_key', self.api_key),
                ('event', json.dumps([event])),
            ],
            timeout=5)

        return response
