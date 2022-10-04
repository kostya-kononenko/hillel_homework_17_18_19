import os

from celery import Celery


from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'send-email-to-admin': {
        "task": 'accounts.tasks.send_mail_to_admin',
        "schedule": crontab(minute='*/10'),

    }
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')