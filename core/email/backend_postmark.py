import logging

from postmarker.core import PostmarkClient
from postmarker.exceptions import ClientError
from postmarker.models.emails import Email
from requests import HTTPError

from core.email.exceptions import EmailSendingException


class Postmark:
    def __init__(self, company_settings):
        self.company_settings = company_settings

    def get_api_key(self):
        return self.company_settings.postmark_api_key

    def send_email(self, from_address, to_address, subject, text, html='', attachments=None, cc_addresses=None,
                   bcc_addresses=None, reply_to=None):
        logger = logging.getLogger('api.postmark')

        if not text:
            text = f'''You have been sent an email from the address {from_address} but your email client is unable to 
display the contents of this email. 

Kindly check the email in a modern email client to see details of the message.'''

        client = PostmarkClient(server_token=self.get_api_key())
        email: Email = client.emails.Email(
            From=from_address,
            To=to_address,
            Cc=cc_addresses,
            Bcc=bcc_addresses,

            Subject=subject,
            HtmlBody=html,
            TextBody=text,
            ReplyTo=reply_to
        )

        if attachments:
            for file_tuple in attachments:
                email.attach_binary(file_tuple[1].read(), file_tuple[0])

        logger.debug('''Sending email using Postmark.
From: {}
To: {}
Subject: {}'''.format(from_address, to_address, subject))

        try:
            email.send()
            logger.info('Sent email using Postmark to {} from {} with subject {}.'.format(
                to_address, from_address, subject
            ))
        except (ClientError, HTTPError) as e:
            logger.error('Error while sending email using Postmark to {} from {} with subject {}. Error: {}'.format(
                to_address, from_address, subject, e
            ))
            raise EmailSendingException(str(e), from_address=from_address, to_address=to_address, subject=subject)
