import os
from celery.app import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'felix.settings')

app = Celery('felix')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
