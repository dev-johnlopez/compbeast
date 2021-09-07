import os
import tempfile

import pytest
from datetime import datetime

from app import create_app, db
from app.events.models import *

@pytest.fixture
def client():
    #app = create_app(celery=app.celery)
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        #seed_db()
        yield app.test_client()

    os.remove("./app/test_app.db")


@pytest.fixture
def runner(client):
    return app.test_cli_runner()

# Put this in your conftest.py
@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'amqp://',
        'result_backend': 'redis://'
    }

@pytest.fixture(scope='session')
def celery_app(client):
    from run import celery
    # for use celery_worker fixture
    from celery.contrib.testing import tasks  # NOQA
    return celery

@pytest.fixture
def events(celery_config):
    events = []

    #Draft event
    draft_event = Event(start_time=datetime.now(),
                        end_time=datetime.now(),
                        team_size=2,
                        status='Draft')
    draft_event.save()
    events.append(draft_event)

    #Register Event
    register_event = Event(start_time=datetime.now(),
                           end_time=datetime.now(),
                           team_size=2,
                           status='Registering')
    add_teams(register_event, 10)
    register_event.save()
    events.append(register_event)

    #Active Event
    active_event = Event(start_time=datetime.now(),
                           end_time=datetime.now(),
                           team_size=2,
                           status='Registering')
    active_event.activate()
    add_teams(register_event, 50)
    active_event.save()
    events.append(active_event)

    #Closed event
    closed_event = Event(start_time=datetime.now(),
                           end_time=datetime.now(),
                           team_size=2,
                           status='Closed')
    add_teams(register_event, 50)
    closed_event.save()
    events.append(closed_event)
    yield events

def add_teams(event, num_teams):
    for i in range(num_teams):
        team = Team(name="Team {}".format(i))
        add_players(team, event.team_size)

def add_players(team, num_players):
    for i in range(num_players):
        player = Player(name="Player {}".format(i),
                        email="test_{}_email@test.com".format(i),
                        external_id="{}_{}#{}".format(team.name, i, i))
        team.add_player(player)
