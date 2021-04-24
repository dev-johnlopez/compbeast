# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
import os
from celery.schedules import crontab

basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = 1
uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
SQLALCHEMY_DATABASE_URI = uri or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
SECRET_KEY = os.environ.get('SECRET_KEY') or 'asdfl;kh35128udafasdfasdf123'
BCRYPT_LOG_ROUNDS = 13
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = False
CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
SQLALCHEMY_TRACK_MODIFICATIONS = False
OAUTHLIB_INSECURE_TRANSPORT = 1
REDIS_URL='redis://127.0.0.1:6379'
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
MAIL_SERVER = 'mail.privateemail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'admin@compbeast.gg'
MAIL_PASSWORD = 'Saintviator1??'
MAIL_DEFAULT_SENDER = 'admin@compbeast.gg'
MAIL_DEBUG = os.environ.get('MAIL_DEBUG') or 1
SERVER_NAME = 'compbeast.herokuapp.com'
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True

#CELERYBEAT_SCHEDULE = {
#    'registration-reminder': {
#        'task': 'app.tasks.test.print_hello',
#        # Every minute
#        'schedule': crontab(minute="*"),
#    }
#}
