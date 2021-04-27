# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from app.events.models import Event, Team, Player
from app.events.forms import TeamForm, ConfirmPlayerForm
from celery import chain
#from app.tasks import new_team_registration_workflow
#from app.events import EventQuery
#from flask_login import login_required, login_user, logout_user
#from compbeast.extensions import login_manager
#from compbeast.public.forms import LoginForm
#from compbeast.user.models import User
#from compbeast.utils import flash_errors

blueprint = Blueprint("public", __name__, static_folder="../static")

class EventQuery(object):
    @staticmethod
    def get_open_events(limit=None):
        query = Event.query.filter((Event.status == 'Registering') | (Event.status == 'Active')).order_by(Event.start_time)
        if limit is not None:
            query = query.limit(limit)
        return query.all()


@blueprint.route("/", methods=["GET", "POST"])
def home():
    current_app.logger.info("Hello from the home page!")
    events = EventQuery.get_open_events(limit=1)
    if len(events) == 0:
        event = None
    else:
        event = events[0]
    return render_template("public/home.html", event=event)

@blueprint.route('/<event_id>/register', methods=['GET', 'POST'])
def register(event_id):
    event = Event.query.get_or_404(event_id)
    form = TeamForm()
    if form.validate_on_submit():
        team = Team()
        form.populate_obj(team)
        #for player in form.players:
        #    player = Player(name=player.name.data,
        #                    email=player.email.data,
        #                    username=player.username.data)
        #    team.add_player(player)
        event.register_team(team)
        team.save()
        event.save()
        from app.tasks import confirm_player
        [confirm_player.si(player.id, event_id).delay(player_id=player.id, event_id=event_id)
            for player in team.players]
        #new_team_registration_workflow = chain(confirm_team.si(team.id),
                                         # send_confirmation_emails.si(team.id))
        #new_team_registration_workflow.delay(team_id=team.id)
        return redirect(url_for('public.confirm', event_id=event.id))

    # if we get here, either validation failed or we're just loading the page
    # we can use append_entry to add up to the total number we want, if necessary
    print("**** {}".format(form.errors))
    for i in range(len(form.players.entries), event.team_size):
        form.players.append_entry()

    return render_template("public/register.html", form=form)

@blueprint.route('/<event_id>/confirm', methods=['GET', 'POST'])
def confirm(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template("public/confirm.html")

@blueprint.route('/<player_id>/confirm/p', methods=['GET', 'POST'])
def update_player(player_id):
    form = ConfirmPlayerForm()
    event = Event.query.get_or_404(1)
    player = Player.query.get_or_404(player_id)
    if form.validate_on_submit():
        player = Player.query.get_or_404(player_id)
        player.username = form.username.data
        player.save()
        from app.tasks import confirm_player
        confirm_player.si(player.id, player.team.event.id).delay(player_id=player.id, event_id=player.team.event.id)
        return redirect(url_for('public.confirm', event_id=player.team.event.id))
    return render_template("public/update_player.html", form=form)

@blueprint.route('/rules', methods=['GET', 'POST'])
def rules():
    return render_template("public/rules.html")
