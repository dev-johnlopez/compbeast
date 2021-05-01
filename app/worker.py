#!/usr/bin/env python
import os
from app import celery, create_app

from app.tasks import remind_pending_registrations, refresh_event_stats

app = create_app()
app.app_context().push()

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour=14),
                             remind_pending_registrations.s(),
                             name='Send Registration Reminders')

    sender.add_periodic_task(crontab(minute='*/15'),
                             refresh_event_stats.s(),
                             name='Refresh Event Stats')

    # Executes every Monday morning at 7:30 a.m.
    #sender.add_periodic_task(
    #    crontab(hour=7, minute=30, day_of_week=1),
    #    test.s('Happy Mondays!'),
