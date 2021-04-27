# -*- coding: utf-8 -*-
"""Application configuration.

Most configuration is set via environment variables.

For local development, use a .env file to set
environment variables.
"""
import os
from celery.schedules import crontab
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

DEBUG = os.environ.get("DEBUG")
FLASK_DEBUG = os.environ.get("FLASK_DEBUG")
uri = os.environ.get("DATABASE_URL")
if uri is not None and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
SQLALCHEMY_DATABASE_URI = uri or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
SECRET_KEY = os.environ.get('SECRET_KEY')
BCRYPT_LOG_ROUNDS = os.environ.get("BCRYPT_LOG_ROUNDS")
DEBUG_TB_ENABLED = DEBUG
DEBUG_TB_INTERCEPT_REDIRECTS = DEBUG
CACHE_TYPE = os.environ.get("CACHE_TYPE")
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
OAUTHLIB_INSECURE_TRANSPORT = os.environ.get("OAUTHLIB_INSECURE_TRANSPORT")
REDIS_URL='redis://:p7b38ec131c292ac5ffd37d7b6a9444f92bee8e9d11b1f4b3d78e8e9afab6ff67@ec2-54-204-251-101.compute-1.amazonaws.com:6979'
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
MAIL_SERVER = os.environ.get("MAIL_SERVER")
MAIL_PORT = os.environ.get("MAIL_PORT")
MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS")
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
MAIL_DEBUG = os.environ.get('MAIL_DEBUG') or 0
#SERVER_NAME = os.getenv('SERVER_NAME')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')
SECURE_PROXY_SSL_HEADER = os.environ.get("SECURE_PROXY_SSL_HEADER")
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT")

#CELERYBEAT_SCHEDULE = {
#    'registration-reminder': {
#        'task': 'app.tasks.test.print_hello',
#        # Every minute
#        'schedule': crontab(minute="*"),
#    }
#}
