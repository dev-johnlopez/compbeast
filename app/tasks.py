import sys
import requests
import json
from app import celery, create_app
from app.email import send_notification_email
from app.events.models import Team, Player, Event

@celery.task
def refresh_event_stats():
    events = Event.query.filter_by(status='Active').all()
    print("refreshing status for events")
    for event in events:
        print("refreshing stats for event id: {}".format(event.id))
        event.refresh_stats()
        event.save()

@celery.task
def confirm_player(player_id, event_id=None):
    try:
        player = None
        event = None
        if event_id is not None:
            event = Event.query.get(event_id)
        player = Player.query.get(player_id)
        if player is not None:
            _update_cod_info_for_player(player)
            send_notification_email(player, event, email="register")
    except:
        print(sys.exc_info())
        #app.logger.error('Unhandled exception', exc_info=sys.exc_info())

@celery.task
def new_event_notification(player_id, event_id=None):
    try:
        player = None
        event = None
        if event_id is not None:
            event = Event.query.get(event_id)
        player = Player.query.get(player_id)
        if player is not None:
            send_notification_email(player, event, email="new_event")
    except:
        print(sys.exc_info())
        #app.logger.error('Unhandled exception', exc_info=sys.exc_info())

@celery.task
def remind_pending_registrations():
    try:
        events = Event.query.all()
        print(events)
        events = [event for event in events if event.state == "Registering"]
        for event in events:
            for team in event.teams:
                for player in team.players:
                    if player.is_confirmed() == False:
                        registration_reminder_notification.si(player.id, event.id).delay(player_id=player.id, event_id=event.id)
    except:
        print(sys.exc_info())
        #app.logger.error('Unhandled exception', exc_info=sys.exc_info())

@celery.task
def generate_leaderboards(event_id):
    try:
        print(event_id)
        event = Event.query.get(event_id)
        for team in event.teams:
            for player in team.players:
                print("success!")
                leaderboard_notification.si(player_id=player.id, event_id=event.id).delay(player_id=player.id, event_id=event.id)
    except:
        print(sys.exec_info())

@celery.task
def registration_reminder_notification(player_id, event_id=None):
    try:
        player = None
        event = None
        if event_id is not None:
            event = Event.query.get(event_id)
        player = Player.query.get(player_id)
        if player is not None:
            send_notification_email(player, event, email="reminder")
    except:
        print(sys.exc_info())
        #app.logger.error('Unhandled exception', exc_info=sys.exc_info())

@celery.task
def leaderboard_notification(player_id, event_id=None):
    try:
        player = None
        event = None
        if event_id is not None:
            event = Event.query.get(event_id)
        player = Player.query.get(player_id)
        if player is not None:
            send_notification_email(player, event, email="leaderboard")
    except:
        print(sys.exc_info())
        #app.logger.error('Unhandled exception', exc_info=sys.exc_info())

@celery.task
def send_async_email(email_data):
    """Background task to send an email with Flask-Mail."""
    msg = Message(email_data['subject'],
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email_data['to']])
    msg.body = email_data['body']
    with app.app_context():
        mail.send(msg)

def _update_cod_info_for_player(player):
    try:
        r = requests.get('https://frozen-island-36052.herokuapp.com/player_details?username={}'.format(player.username.replace("#", "%23")))
        data = json.loads(r.text)
        player.external_id = str(data['player'])
        player.save()
    except:
        print("error")
        #app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        return
