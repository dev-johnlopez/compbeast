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
        "schedule": crontab(minute=0, hour=14)
    },
    "send-this-weeks-tournaments-email-task": {
        "task": "app.tasks.send_this_weeks_tournaments_email",
        "schedule": crontab(minute='*/1')
        #"schedule": crontab(minute=0, hour=8, day_of_week='sun')
    }
}
