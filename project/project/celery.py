import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-new-precedents-user-everyday': {
        'task': 'main_app.sample_tasks.send_new_precedents_user',
        'schedule': crontab(minute=0, hour=12),
        'args': None
    }
}