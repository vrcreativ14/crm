import logging
import requests

api_logger = logging.getLogger("api.sms")

url = "https://api.omnidigital.ae/v1/messages"

class WhatsappService:
    def send_whatsapp_msg(self, to, message, **kwargs):
        app_name = kwargs.get('app_name',None)
        token = ''
        payload = {}
        
        if app_name == 'mortgage':
            token = 'ef54c9d79ec8fc5b0da514ce04e7dd617783965e27271dca47725995fe59c8a017b1a50246a8b227'
            payload = {
            "phone": to,             
            "message": message,
            "actions": [
                    {
                      "action": "chat:resolve"
                    }
                ]
            }
        else:
            token = '6479e9c54e58b868088a3c8219bf5aeb114b0d4abf48911487ecbd5a69a38eda9ecb3f6290116a1a'
            motor_agent_id = '62382cb386070b68c50f4c93'
            payload = {
            "phone": to,
            "agent": motor_agent_id,
            "message": message,
            "status": "resolved",
            "actions": [
                    {
                      "action": "chat:assign"
                    }
                ]
            }
        
        headers = {
            "Content-Type": "application/json",
            "Token": token
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        api_logger.info('Sending Whatsapp message to {}. Response received: {}'.format(to,response.text))
        