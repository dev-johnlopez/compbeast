from flask import render_template, flash, abort, redirect, url_for, session
from app.database import db
from app.events.queries import EventQuery
from app.events.forms import TeamForm
from app.profile import bp
from app.profile.forms import UserForm
from flask_security import login_required, current_user


@bp.route('/activate', methods=["GET", "POST"])
@login_required
def activate():
    form = UserForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.add(current_user)
        db.session.commit()
        flash("Your account has been activated!")
        return redirect(url_for('profile.index'))
    return render_template("profile/activate.html", form=form, current_user=current_user)

@bp.route('/index', methods=["GET", "POST"])
@bp.route('/', methods=["GET", "POST"])
@login_required
def index():
    if current_user.username is None or current_user.platform is None:
        return redirect(url_for('profile.activate'))

    if session.get('next_url'):
        next_url = session.get('next_url')
        session.pop('next_url', None)
        return redirect(next_url)

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

@bp.route('/registrations/<team_id>/join', methods=["GET", "POST"])
def join_team(team_id):
    #force login w/ discord if user isn't logged in.
    if not current_user.is_authenticated:
        session['next_url'] = url_for('public.register', event_id=event_id)
        return redirect(url_for('discord.login'))

    team = Team.query.get_or_404(team_id)
    current_user.add_team(team)
    db.session.add(current_user)
    db.session.commit()
    return redirect(url_for('profile.index'))
