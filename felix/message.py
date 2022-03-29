import logging
import requests

api_logger = logging.getLogger("api.sms")

url = "https://api.omnidigital.ae/v1/messages"

class WhatsappService:
    def send_whatsapp_msg(self, to, message, **kwargs):
        app_name = kwargs.get('app_name',None)
        token = ''
        if app_name == 'mortgage':
            token = 'ef54c9d79ec8fc5b0da514ce04e7dd617783965e27271dca47725995fe59c8a017b1a50246a8b227'
        else:
            token = '6479e9c54e58b868088a3c8219bf5aeb114b0d4abf48911487ecbd5a69a38eda9ecb3f6290116a1a'
        payload = {
            "phone": to,
            "message": message,
            "actions": [
                    {
                      "action": "chat:resolve"
                    }
                ]
            }
        headers = {
            "Content-Type": "application/json",
            "Token": token
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        api_logger.info('Sending Whatsapp message to {}. Response received: {}'.format(to,response.text))
        