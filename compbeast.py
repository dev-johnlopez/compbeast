#from app import app

"""Create an application instance."""
from app import create_app
from app.extensions import security, db

#app = create_app(celery=app.celery)
app = create_app(os.getenv('FLASK_CONFIG') or 'development')
app.app_context().push()

@app.before_first_request
def create_user():
    admin = security.datastore.get_user(app.config['ADMIN_EMAIL'])
    if admin is None:
      security.datastore.create_user(email=app.config['ADMIN_EMAIL'], password=app.config['ADMIN_PASSWORD'])
      db.session.commit()
