import os
from celery import Celery

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'unakovskaya_bot.settings')

app = Celery('unakovskaya_bot')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
