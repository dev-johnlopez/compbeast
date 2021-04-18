from flask import Blueprint, url_for, redirect, render_template
from app.events.models import Event, Team, Player
from app.events.forms import TeamForm, PlayerForm
from collections import namedtuple

blueprint = Blueprint('events', __name__, url_prefix="/events")

@blueprint.route('/<event_id>/leaderboard')
def leaderboard(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template("public/leaderboard.html", event=event)

@blueprint.route('/<event_id>/<division_num>/leaderboard')
def division_leaderboard(event_id, division_num):
    event = Event.query.get_or_404(event_id)
    teams = [team for team in event.teams if team.division == division_num]
    #for team in event.teams:
    #    if
    return '{}'.format(event.state)
