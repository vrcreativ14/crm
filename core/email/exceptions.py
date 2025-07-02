from requests import HTTPError


class EmailSendingException(HTTPError):
    def __init__(self, *args, **kwargs):
        self.from_address = kwargs.pop('from_address')
        self.to_address = kwargs.pop('to_address')
        self.subject = kwargs.pop('subject')

        super(EmailSendingException, self).__init__(*args, **kwargs)
