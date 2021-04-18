from app import celery
from app.events.models import Task, Event
from flask import current_app
from celery import signature
from rq import get_current_job
import sys
import requests
import json

from app import create_app

@celery.task
def confirm_team(team_id):
    try:
        print("confirming team")
        team = Event.query.get(team_id)
        for player in team.players:
            print("confirming player")
            _update_cod_info_for_player(player)
    except:
        print(sys.exc_info())
        #app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)

@celery.task
def send_confirmation_emails(team_id):
    try:
        print("confirmation emails sent!")
        pass
    except:
        pass
    finally:
        pass

def seed_teams(event_id):
    try:
        print("*** TASK RUNNING")
        event = Event.query.get(event_id)
        players = []
        for team in event.teams:
            print("***** Stats for {}".format(team.name))
            for player in team.players:
                print("***** Stats for player {} on team {}".format(player.username, team.name))
                _update_cod_info_for_player(player)
        sorted_teams = sorted(event.teams, key=lambda team: team.rating, reverse=True)
        current_division = 0
        for i, team in enumerate(sorted_teams):
            if i % event.teams_per_division == 0:
                current_division += 1
            team.division = current_division
            print("Team {} is in Division #{}".format(team.name, team.division))
        num_divisions = current_division
        print("Num Divisions: {}".format(num_divisions))
    except:
        print("error")
        #app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)

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

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())

        if progress >= 100:
            task.complete = True
        task.save()

new_team_registration_workflow = (confirm_team.s(),
                                  send_confirmation_emails.s())
