import logging

# from django.conf import settings
# from twilio.rest import Client
# from twilio.rest import TwilioException
#
# from core.utils import is_valid_number, normalize_phone_number
import requests

api_logger = logging.getLogger("api.sms")

url = "https://api.omnidigital.ae/v1/messages"

class SMSService:
    def send_sms(self, to, message):
        #api_logger.info('SMS sending disabled. Not sending sms to {}. SMS Body: {}'.format(to, message))
        payload = {
            "phone": to,
            "message": message
            }
        headers = {
            "Content-Type": "application/json",
            "Token": "6479e9c54e58b868088a3c8219bf5aeb114b0d4abf48911487ecbd5a69a38eda9ecb3f6290116a1a"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        api_logger.info('Sending Whatsapp message to {}. Response received: {}'.format(to,response.text))
        print(response.text)
        

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
