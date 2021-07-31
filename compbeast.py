#from app import app
import os
"""Create an application instance."""
from app import create_app
from app.extensions import security, db
from datetime import datetime, timedelta

#app = create_app(celery=app.celery)
app = create_app(os.getenv('FLASK_CONFIG'))
app.app_context().push()

@app.before_first_request
def create_user():
    admin = security.datastore.get_user(app.config['ADMIN_EMAIL'])
    if admin is None:
      security.datastore.create_user(email=app.config['ADMIN_EMAIL'], password=app.config['ADMIN_PASSWORD'])
      db.session.commit()

@app.template_filter('to_cst')
def to_cst(datetime):
    """Convert a datetime in UTC to CT."""
    new_date_time = datetime - timedelta(hours=5)
    return new_date_time

@app.template_filter('format_datetime')
def format_datetime(datetime, format=None, timedelta_hours=None):
    """Formats a datetime."""
    if timedelta_hours is not None:
        datetime += timedelta(hours=timedelta_hours)
    return datetime.strftime(format)

@app.template_filter('timedelta')
def timediference(start_datetime, end_datetime):
    """Formats a datetime."""
    td = end_datetime - start_datetime
    hours = td.seconds // 3600
    seconds = (td.seconds//60)%60
    return "{}H:{}M".format(hours, seconds)
