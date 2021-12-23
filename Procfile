web: flask db upgrade; gunicorn compbeast:app
upgrade : flask db upgrade;
worker: celery -A celery_worker.celery worker -l debug
beat: celery -A celery_worker.celery beat -l debug
