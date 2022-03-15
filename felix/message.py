import logging
import requests

api_logger = logging.getLogger("api.sms")

url = "https://api.omnidigital.ae/v1/messages"

class WhatsappService:
    def send_whatsapp_msg(self, to, message):
        
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
        