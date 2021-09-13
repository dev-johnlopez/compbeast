import sys
import requests
import json
import datetime
import traceback
from datetime import date
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
def progress_events():
    events = Event.query.filter(Event.status != 'Closed').all()
    print("updating status for events")
    for event in events:
        if event.status == "Registering":
            day_change = datetime.timedelta(days=1)
            next_day = date.today() + day_change
            if event.start_time.date() == next_day:
                event.activate()
                event.save()
        if event.status == "Active":
            day_change = datetime.timedelta(days=1)
            day_after_event = event.end_time.date() + day_change
            print("{} = {} + {}".format(day_after_event, event.end_time.date(), day_change))
            print("{} == {}".format(date.today(), day_after_event))
            if date.today() >= day_after_event:
                event.close()
                event.save()
                next_draft_event = Event.query.filter(Event.status == 'Draft').order_by(Event.start_time).first()
                if next_draft_event is not None:
                    next_draft_event.open_registration()
                    next_draft_event.save()
    print("done updating status")

@celery.task
def confirm_player(player_id, event_id=None, generate_emails=True):
    try:
        player = None
        event = None
        if event_id is not None:
            event = Event.query.get(event_id)
        player = Player.query.get(player_id)
        if player is not None:
            print("**** Updating Player Status for {}".format(player))
            _update_cod_info_for_player(player)
            if generate_emails:
                send_notification_email(player, event, email="register")
    except:
        print("Error!") #print(sys.exec_info())
        #app.logger.error('Unhandled exception', exc_info=sys.exc_info())

@celery.task
def get_player_stats(player_id):
    try:
        player = None
        player = Player.query.get(player_id)
        if player is not None:
            _update_cod_info_for_player(player)
            send_notification_email(player, event, email="register")
    except:
        print("Error!") #print(sys.exec_info())
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
        print("Error!") #print(sys.exec_info())
        #app.logger.error('Unhandled exception', exc_info=sys.exc_info())

@celery.task
def remind_pending_registrations():
    try:
        print("sending remind registration tasks")
        events = Event.query.all()
        print(events)
        events = [event for event in events if event.state == "Registering"]
        for event in events:
            for team in event.teams:
                for player in team.players:
                    if player.is_confirmed() == False:
                        registration_reminder_notification.si(player.id, event.id).delay(player_id=player.id, event_id=event.id)
    except:
        print("Error!") #print(sys.exec_info())
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
        print("Error in generate_leaderboards!") #print(sys.exec_info())
        # printing stack trace
        traceback.print_exc()

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
        print("Error!") #print(sys.exec_info())
        # printing stack trace
        traceback.print_exc()
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
        print("Error in leaderboard_notification!") #print(sys.exec_info())
        # printing stack trace
        traceback.print_exc()
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
        player.avatarUrl = str(data['avatarUrl'])
        print(str(data['profile']['lifetime']['mode']['br']['properties']['kdRatio']))
        # TODO - Test: player.kdr = int(data['kdr'])
        player.save()
    except:
        print("error")
        # printing stack trace
        traceback.print_exc()
        #app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        return
