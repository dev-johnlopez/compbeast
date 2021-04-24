# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
import os
from celery.schedules import crontab

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = os.getenv("DEBUG")
FLASK_DEBUG = os.getenv("FLASK_DEBUG")
uri = os.getenv("DATABASE_URL")
if uri is not None and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
SQLALCHEMY_DATABASE_URI = uri or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
SECRET_KEY = os.environ.get('SECRET_KEY') or 'asdfl;kh35128udafasdfasdf123'
BCRYPT_LOG_ROUNDS = os.getenv("BCRYPT_LOG_ROUNDS")
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = DEBUG
CACHE_TYPE = os.getenv("CACHE_TYPE")
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
OAUTHLIB_INSECURE_TRANSPORT = os.getenv("OAUTHLIB_INSECURE_TRANSPORT")
REDIS_URL=os.getenv("REDIS_URL")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
MAIL_DEBUG = os.environ.get('MAIL_DEBUG') or 0
SERVER_NAME = os.getenv('SERVER_NAME')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
SECURE_PROXY_SSL_HEADER = os.getenv("SECURE_PROXY_SSL_HEADER")
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT")

#CELERYBEAT_SCHEDULE = {
#    'registration-reminder': {
#        'task': 'app.tasks.test.print_hello',
#        # Every minute
#        'schedule': crontab(minute="*"),
#    }
#}
