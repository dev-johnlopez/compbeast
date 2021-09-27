#!/usr/bin/env python
import os
from app import celery, create_app
from celery.schedules import crontab

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.app_context().push()

celery.conf.beat_schedule = {
    "refresh-stats-in-all-events-task": {
        "task": "app.tasks.refresh_event_stats",
        "schedule": crontab(minute='*/15')
    },
    "progress_all_events": {
        "task": "app.tasks.progress_events",
        "schedule": crontab(minute=0, hour=19)
    },
    "send-registration-reminders-task": {
        "task": "app.tasks.remind_pending_registrations",
        "schedule": crontab(minute=0, '*/1')
    }
}
