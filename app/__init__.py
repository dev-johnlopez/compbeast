# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import asyncio
import sys
import os

from flask import Flask, render_template
from redis import Redis
from celery import Celery

#from app import commands, public, user, event
from app import events
from app.extensions import (
    db,
    migrate,
    mail,
    moment,
    security
)

from app.admin import register_admin
from app.email import *
#from app.tasks import make_celery
from config import config, Config

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
#scheduler.add_job(job1, 'interval', seconds=1)

def create_app(config_name="development", **kwargs):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    celery = make_celery(app)
    celery.conf.update(app.config)

    #if kwargs.get("celery"):
    #    init_celery(kwargs.get("celery"), app)
    #app.task_queue = rq.Queue('compbeast-tasks', connection=app.redis)
    register_extensions(app)
    register_admin(app, db)
    register_blueprints(app)
#    register_errorhandlers(app)
    register_shellcontext(app)
#    register_commands(app)
    configure_logger(app)
    return app

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

#def make_celery(app_name=__name__):
    #redis_uri='redis://127.0.0.1:6379'
    #return Celery(app_name, backend=redis_uri, broker=redis_uri, include=['app.tasks'])

def register_extensions(app):
    """Register Flask extensions."""

    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    moment.init_app(app)

    from flask_security import SQLAlchemyUserDatastore
    from app.auth.models import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app=app, datastore=user_datastore)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    from app.events.views import blueprint as events
    from app.public.views import blueprint as public
    app.register_blueprint(events)
    app.register_blueprint(public)
    return None


#def register_errorhandlers(app):
#    """Register error handlers."""

#    def render_error(error):
#        """Render error template."""
#        # If a HTTPException, pull the `code` attribute; default to 500
#        error_code = getattr(error, "code", 500)
#        return render_template(f"{error_code}.html"), error_code

#    for errcode in [401, 404, 500]:
#        app.errorhandler(errcode)(render_error)
#    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {
            "db": db#,
            #"User": user.models.User,
            #"Event": events.models.Event
        }

#    app.shell_context_processor(shell_context)


#def register_commands(app):
#    """Register Click commands."""
#    app.cli.add_command(commands.test)
#    app.cli.add_command(commands.lint)


def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)

from app.tasks import *
