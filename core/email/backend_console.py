import logging


class Console:
    def send_email(self, from_address, to_address, subject, text, html='', attachments=None, cc_addresses=None,
                   bcc_addresses=None, reply_to=None):
        logger = logging.getLogger('console')
        logger.debug(f'''Sending email to {to_address} from {from_address} with subject "{subject}". Text:
{text}

HTML:
{html}''')
