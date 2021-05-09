#!/usr/bin/env python
import os
from app import celery, create_app
from celery.schedules import crontab

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()

celery.conf.beat_schedule = {
    "refresh-stats-in-all-events-task": {
        "task": "app.tasks.refresh_event_stats",
        "schedule": crontab(minute='*/1')
    },
    "send-registration-reminders-task": {
        "task": "app.tasks.remind_pending_registrations",
        "schedule": crontab(hour=14)
    }
}
