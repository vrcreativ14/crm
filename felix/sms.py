import logging

# from django.conf import settings
# from twilio.rest import Client
# from twilio.rest import TwilioException
#
# from core.utils import is_valid_number, normalize_phone_number

api_logger = logging.getLogger("api.sms")


class SMSService:
    def send_sms(self, to, message):
        api_logger.info('SMS sending disabled. Not sending sms to {}. SMS Body: {}'.format(to, message))
        return

        # if settings.DEBUG:
        #     api_logger.info('Not sending sms to {} in debug mode. SMS Body: {}'.format(to, message))
        #     return
        #
        # if is_valid_number(to):
        #     to = normalize_phone_number(to)
        #
        #     api_logger.info('Sending SMS to {} with message "{}"'.format(to, message))
        #
        #     client = Client(
        #         settings.TWILIO_SID,
        #         settings.TWILIO_TOKEN,
        #     )
        #     try:
        #         response = client.messages.create(to=to, from_=settings.TWILIO_NUMBER, body=message)
        #     except TwilioException as e:
        #         api_logger.error('Exception while trying to send SMS to %s. Error: %s', to, e)
        #         return
        #
        #     if response.status == 'failed':
        #         api_logger.error(
        #             "Got status failed while sending an sms. \nError code: {}\nError: {}".format(response.error_code,
        #                                                                                          response.error_message)
        #         )
        #         return
        #
        #     return response
        #
        # else:
        #     api_logger.error(
        #         "Can't send sms to {}. Number not valid".format(to)
        #     )
        #     return
