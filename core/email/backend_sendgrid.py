import base64
import logging

import requests
from django.conf import settings
from sendgrid import FileContent, Mail, ReplyTo, Attachment, FileName, Disposition, SendGridAPIClient, Content, MimeType

from core.email.exceptions import EmailSendingException
from core.utils import clean_and_validate_email_addresses


class Sendgrid:
    def __init__(self, company_settings):
        self.company_settings = company_settings
        self.account_config = settings.EMAIL_CONFIGURATION['sendgrid']

    def send_email(self, from_address, to_address, subject, text, html='', attachments=None, cc_addresses=None,
                   bcc_addresses=None, reply_to=None):
        logger = logging.getLogger('api.sendgrid')
        logger.debug('''Sending email using Sendgrid.
        From: {}
        To: {}
        Subject: {}'''.format(from_address, to_address, subject))

        if not text:
            text = f'''You have been sent an email from the address {from_address} but your email client is unable
to display the contents of this email.

Kindly check the email in a modern email client to see details of the message.'''

        message = Mail(from_address, to_address, subject)

        contents = []
        if text:
            contents.append(Content(MimeType.text, text))
        if html:
            contents.append(Content(MimeType.html, html))

        message.content = contents

        if cc_addresses:
            for address in clean_and_validate_email_addresses(cc_addresses).split('; '):
                message.add_cc(address)

        if bcc_addresses:
            for address in clean_and_validate_email_addresses(bcc_addresses).split('; '):
                message.add_bcc(address)

        if reply_to:
            message.reply_to = ReplyTo(reply_to)

        if attachments:
            for attachment_name, attachment_file in attachments:
                file_content = attachment_file.read()
                message.add_attachment(Attachment(
                    FileContent(base64.b64encode(file_content).decode('utf-8')),
                    FileName(attachment_name),
                    disposition=Disposition('attachment')
                ))

        client = SendGridAPIClient(self.account_config['api_key'])
        try:
            response = client.send(message)
            logger.info(f'Email sent via SendGrid. Response code: {response.status_code}')
        except Exception as e:
            logger.error(f'Unable to send email via SendGrid. Error: {str(e)}')
            raise EmailSendingException(str(e), from_address=from_address, to_address=to_address, subject=subject)
