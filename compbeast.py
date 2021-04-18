#from app import app

"""Create an application instance."""
from app import create_app

#app = create_app(celery=app.celery)
app = create_app()
app.app_context().push()
