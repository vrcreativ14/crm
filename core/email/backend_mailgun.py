import logging

import requests
from django.conf import settings
from requests import HTTPError
from requests.auth import HTTPBasicAuth

from core.email.exceptions import EmailSendingException


class Mailgun:
    def __init__(self, company_settings):
        self.company_settings = company_settings
        self.account_config = settings.EMAIL_CONFIGURATION['mailgun']

    def get_api_key(self):
        return self.company_settings.mailgun_api_key or self.account_config['password']

    def get_api_endpoint(self):
        return self.company_settings.mailgun_api_url or self.account_config['api_url']

    def send_email(self, from_address, to_address, subject, text, html='', attachments=None, cc_addresses=None,
                   bcc_addresses=None, reply_to=None):
        logger = logging.getLogger('api.mailgun')

        auth = HTTPBasicAuth('api', self.get_api_key())
        api_endpoint = self.get_api_endpoint()

        logger.debug('''Sending email using Mailgun.
            API Endpoint: {}
            From: {}
            To: {}
            Subject: {}'''.format(api_endpoint, from_address, to_address, subject))
        files = []

        if attachments:
            for file_tuple in attachments:
                files.append(['attachment', (file_tuple[0], file_tuple[1])])

        if not text:
            text = f'''You have been sent an email from the address {from_address} but your email client is unable
to display the contents of this email.

Kindly check the email in a modern email client to see details of the message.'''

        email_request_body = {'from': from_address, 'to': to_address, 'subject': subject, 'text': text, 'html': html}
        if cc_addresses:
            email_request_body['cc'] = cc_addresses
        if bcc_addresses:
            email_request_body['bcc'] = bcc_addresses
        if reply_to:
            email_request_body['h:Reply-To'] = reply_to

        response = requests.post('{}/messages'.format(api_endpoint), email_request_body, auth=auth, files=files)

        try:
            response.raise_for_status()
            logger.info('Sent email using Mailgun to {} from {} with subject {}.'.format(
                to_address, from_address, subject
            ))
        except HTTPError as e:
            logger.error('Error while sending email using Mailgun to {} from {} with subject {}. Response: {}'.format(
                to_address, from_address, subject, response.text
            ))
            raise EmailSendingException(str(e), from_address=from_address, to_address=to_address, subject=subject)
