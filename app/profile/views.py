from flask import render_template, flash, abort, redirect, url_for
from app.database import db
from app.events.queries import EventQuery
from app.events.forms import TeamForm
from app.profile import bp
from app.profile.forms import UserForm
from flask_security import login_required, current_user



@bp.route('/index', methods=["GET", "POST"])
@bp.route('/', methods=["GET", "POST"])
@login_required
def index():
    form = UserForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.add(current_user)
        db.session.commit()
        flash("Success!")
    return render_template("profile/index.html", form=form, current_user=current_user)

@bp.route('/tournaments', methods=["GET", "POST"])
@login_required
def tournaments():
    events = EventQuery.get_open_events()
    return render_template("profile/tournaments.html", events=events)

@bp.route('/teams', methods=["GET", "POST"])
@login_required
def teams():
    #teams = current_user.teams
    return render_template("profile/teams.html")

@bp.route('/registrations', methods=["GET", "POST"])
@login_required
def registrations():
    #teams = current_user.teams
    return render_template("profile/registrations.html", teams=current_user.teams)

@bp.route('/registrations/<team_id>/edit', methods=["GET", "POST"])
@login_required
def edit_registration(team_id):
    edit_team = None
    for team in current_user.teams:
        print("{} == {}".format(team.id, team_id))
        if int(team.id) == int(team_id):
            print("Setting team: {}".format(team))
            edit_team = team
    if edit_team is None:
        abort(404)

    form = TeamForm(obj=edit_team)
    if form.validate_on_submit():
        form.populate_obj(team)
        team.save()
        return redirect(url_for('profile.registrations'))
    #teams = current_user.teams
    return render_template("public/register.html", event=team.event, form=form)
