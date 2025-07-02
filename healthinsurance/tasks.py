import logging
from felix.celery_app import app
from .views.email import StageEmailNotification
from celery import shared_task
import time 

@app.task
def email_notification(deal, email_type, recipient, cc_emails = [], bcc_emails = []):
    logger = logging.getLogger('workers')
    logger.info('Sending an email notification to customer')
    stage_email = StageEmailNotification(deal, email_type, recipient, cc_addresses = cc_emails, bcc_addresses=bcc_emails)
    stage_email.stage_propagation_email()
