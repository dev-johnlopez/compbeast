# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located in app.py."""
from flask import url_for, request, current_app
from flask_admin import Admin
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from flask_admin.base import AdminIndexView, expose

# Create customized index view class that handles login & registration
class AuthView(AdminIndexView):
    @expose('/')
    def index(self):
        next = url_for(request.endpoint, **request.view_args)
        #if not current_user.is_authenticated:
        #    return redirect(url_for('security.login', next=next))
        #if not current_user.is_admin():
        #    return redirect(url_for('security.login', next=next))
        return super(AuthView, self).index()

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return current_app.login_manager.unauthorized()

admin = Admin(name='CompBeast.gg', template_mode='bootstrap3', index_view=AuthView())
db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
security = Security()
moment = Moment()

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
