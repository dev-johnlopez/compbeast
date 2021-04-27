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

class CustomModelView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated

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

def register_admin(app, db):
    admin.init_app(app)
    admin.add_view(EventView(Event, db.session))
    admin.add_view(CustomModelView(Team, db.session))
    admin.add_view(CustomModelView(Player, db.session))
    admin.add_view(CustomModelView(Task, db.session))
    #admin.add_view(rediscli.RedisCli(app.redis))
