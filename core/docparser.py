"""Doc Parser"""
import time
import requests

from django.conf import settings


class DOCParser:
    PARSER_MAPPINGS = {
        'rsa': 'omacjevlkfux',
        'oman': 'ujcsoevktpzc',
        'tokio marine': 'gaumncptvlru',
    }

    def __init__(self):
        self.api_url = 'https://api.docparser.com/v1'
        self.headers = {'api_key': settings.DOC_PARSER['API_KEY']}

    @classmethod
    def get_allowed_insurers_message(cls):
        return 'Text extraction is available for RSA, Oman Insurance and Tokio Marine policy documents only.'

    def get_parser_id_for_insurer(self, parser_name):
        return self.PARSER_MAPPINGS.get(parser_name, None)

    def upload_document(self, parser_id, file):
        return requests.post(f'{self.api_url}/document/upload/{parser_id}',
                             files={'file': file},
                             headers=self.headers)

    def get_document(self, parser_id, document_id):
        return requests.get(f'{self.api_url}/results/{parser_id}/{document_id}', headers=self.headers)
