from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shop_api.settings")

app = Celery("shop_api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "print-hello-every-minute": {
        "task": "myapp.tasks.print_hello",
        "schedule": crontab(minute="*"),
    },
}