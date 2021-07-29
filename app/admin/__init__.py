import datetime
from app.extensions import admin, db, security
from app.events.models import Event, Team, Player, Task
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader
from flask import flash, current_app
from flask_admin.model.template import EndpointLinkRowAction, TemplateLinkRowAction
from flask_admin.base import expose, BaseView
from flask import request, redirect, url_for
from flask_admin.contrib import rediscli
from flask_security import current_user
import json
import requests
#from app.tasks import _update_cod_info_for_player

class CustomModelView(ModelView):

    def is_accessible(self):
        return True#current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return current_app.login_manager.unauthorized()

class EventView(CustomModelView):
    list_template = "admin/my_list.html"  # Override the default template
    form_ajax_refs = {
        'team': QueryAjaxModelLoader('team', db.session, Team, fields=['name'], page_size=10)
    }
    column_extra_row_actions = [  # Add a new action button
        TemplateLinkRowAction("custom_row_actions.activate_row", "Activate Record"),
    ]

    @expose('/action/copy_row', methods=('POST',))
    def copy_row(self, *args, **kwargs):
        event_id = request.form['rowid']
        #event_id = request.args.get('id')
        try:
            event = Event.query.get(event_id)
            new_event = Event()
            new_event.name = event.name
            new_event.team_size = event.team_size
            new_event.teams_per_division = event.teams_per_division
            new_event.num_games = event.num_games
            new_event.start_time = event.start_time + datetime.timedelta(days=7)
            new_event.end_time = event.end_time + datetime.timedelta(days=7)
            new_event.state = 'Draft'
            new_event.save()

        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash('Failed to copy event. %(error)s', 'error')

        return redirect(self.get_save_return_url(Event))

    @expose('/action/register_row', methods=('POST',))
    def register_row(self, *args, **kwargs):
        event_id = request.form['rowid']
        #event_id = request.args.get('id')
        try:
            event = Event.query.get(event_id)
            if event.open_registration():
                event.save()

        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash('Failed to progress event. %(error)s', 'error')

        return redirect(self.get_save_return_url(Event))

    @expose('/action/activate_row', methods=('POST',))
    def activate_row(self, *args, **kwargs):
        event_id = request.form['rowid']
        #event_id = request.args.get('id')
        try:
            event = Event.query.get(event_id)
            if event.activate():
                event.save()

        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash('Failed to progress event. %(error)s', 'error')

        return redirect(self.get_save_return_url(Event))

    @expose('/action/close_row', methods=('POST',))
    def close_row(self, *args, **kwargs):
        event_id = request.form['rowid']
        #event_id = request.args.get('id')
        try:
            event = Event.query.get(event_id)
            if event.close():
                event.save()

        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash('Failed to progress event. %(error)s', 'error')

        return redirect(self.get_save_return_url(Event))

    @action('open_registration', 'Open Registration', 'Are you sure you want to start the registration process for the selected rows?')
    def action_open_registration(self, ids):
        try:
            query = Event.query.filter(Event.id.in_(ids))

            count = 0
            events = query.all()
            for event in events:
                if event.open_registration():
                    event.save()
                    count += 1
            flash('{} of {} event(s) were progressed to \"Registering\" status.'.format(count, len(ids)))
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash('Failed to progress event. %(error)s', 'error')

    @action('activate', 'Close Registration', 'Are you sure you want to close the registration process for the selected rows?')
    def action_activate(self, ids):
        try:
            query = Event.query.filter(Event.id.in_(ids))

            count = 0
            events = query.all()
            for event in events:
                if event.activate():
                    event.save()
                    count += 1
            flash('{} of {} event(s) were progressed to \"Active\" status.'.format(count, len(ids)))
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash('Failed to progress event. %(error)s', 'error')

    @action('close', 'Close Event', 'Are you sure you want to close the event?')
    def action_activate(self, ids):
        try:
            query = Event.query.filter(Event.id.in_(ids))

            count = 0
            events = query.all()
            for event in events:
                if event.close():
                    event.save()
                    count += 1
            flash('{} of {} event(s) were progressed to \"Closed\" status.'.format(count, len(ids)))
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash('Failed to progress event. %(error)s', 'error')

class TeamView(CustomModelView):
    list_template = "admin/my_list.html"  # Override the default template

    @expose('/action/refresh_row', methods=('POST',))
    def close_row(self, *args, **kwargs):
        team_id = request.form['rowid']
        #event_id = request.args.get('id')
        try:
            team = Team.query.get(team_id)
            team.refresh_stats(team.event)
            team.save()

        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash('Failed to progress event. %(error)s', 'error')

        return redirect(self.get_save_return_url(Event))

    @action('refresh', 'Refresh stats', 'Are you sure you want to refresh stats?')
    def action_refresh(self, ids):
        try:
            query = Team.query.filter(Team.id.in_(ids))

            count = 0
            teams = query.all()
            for team in teams:
                team.refresh_stats(team.event)
                team.save()
                count += 1
            flash('{} of {} teams(s) were had their stats refreshed'.format(count, len(ids)))
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash('Failed to refresh stats. %(error)s', 'error')

class PlayerView(CustomModelView):
    list_template = "admin/my_list.html"  # Override the default template

    @expose('/action/refresh_row', methods=('POST',))
    def close_row(self, *args, **kwargs):
        player_id = request.form['rowid']
        #event_id = request.args.get('id')
        try:
            player = Player.query.get(player_id)
            #_update_cod_info_for_player(player)
            player.save()

        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash('Failed to progress event. %(error)s', 'error')

        return redirect(self.get_save_return_url(Event))

    @action('refresh', 'Refresh ID', 'Are you sure you want to refresh Activision ID?')
    def action_refresh(self, ids):
        try:
            query = Player.query.filter(Player.id.in_(ids))

            count = 0
            players = query.all()
            for player in players:
                _update_cod_info_for_player(player)
                player.save()
                count += 1
            flash('{} of {} players(s) were had their ID refreshed'.format(count, len(ids)))
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash('Failed to refresh stats. %(error)s', 'error')

def register_admin(app, db):
    admin.init_app(app)
    admin.add_view(EventView(Event, db.session))
    admin.add_view(TeamView(Team, db.session))
    admin.add_view(PlayerView(Player, db.session))
    admin.add_view(CustomModelView(Task, db.session))
    #admin.add_view(rediscli.RedisCli(app.redis))

def _update_cod_info_for_player(player):
    try:
        r = requests.get('https://frozen-island-36052.herokuapp.com/player_details?username={}'.format(player.username.replace("#", "%23")))
        print("sent request")
        data = json.loads(r.text)
        print("got data")
        player.external_id = str(data['player'])
        print("got external id - " + player.external_id)
        print(str(data['profile']['lifetime']['mode']['br']['properties']['kdRatio']))
        player.kdr =  data['profile']['lifetime']['mode']['br']['properties']['kdRatio']
        # TODO - Test: player.kdr = int(data['kdr'])
        player.save()
    except:
        print("error!!!! ")
        #app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        return
