from flask import Blueprint, url_for, redirect, render_template, abort, flash, Markup
from app.events.models import Event, Team, Player, Match
from app.events.forms import TeamForm, PlayerForm, MatchForm, PlayerStatForm
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

class EventQuery(object):
    @staticmethod
    def get_open_events(limit=None):
        query = Event.query.filter((Event.status == 'Registering') | (Event.status == 'Active')).order_by(Event.start_time)
        if limit is not None:
            query = query.limit(limit)
        return query.all()


@blueprint.route("/", methods=["GET", "POST"])
def index():
    events = EventQuery.get_open_events()
    return render_template("events/index.html", events=events)

@blueprint.route("/<event_id>/<team_id>/edit", methods=["GET", "POST"])
def team(event_id, team_id):
    event = Event.query.get_or_404(event_id)
    team = Team.query.get_or_404(team_id)
    if team.event != event:
        abort(404)
    form = TeamForm(obj=team)
    if form.validate_on_submit():
        form.populate_obj(team)
        team.save()
    return render_template("events/team.html", event=event, team=team, form=form)

@blueprint.route("/<event_id>/<team_id>/report", methods=["GET", "POST"])
def report(event_id, team_id):
    event = Event.query.get_or_404(event_id)
    team = Team.query.get_or_404(team_id)
    if team.event != event:
        abort(404)
    form = MatchForm()
    if form.validate_on_submit():
        match = Match()
        form.populate_obj(match)
        team.add_match(match)
        team.save()
        flash(Markup('Your match was reported. Scores have been taking into account and leaderboards are updated <a href=\"{}\" class="text-dark">here</a>.'.format(url_for('events.leaderboard', event_id=event.id))))
        return redirect(url_for('.report', event_id=event.id, team_id=team.id))
    if len(form.player_stats) != event.team_size:
        for i in range(event.team_size - len(form.player_stats)):
            player_stat = PlayerStatForm()
            form.player_stats.append_entry(player_stat)
    return render_template("events/report.html", event=event, team=team, form=form)
