web: flask db upgrade; gunicorn compbeast:app
worker: celery -A celery_worker.celery worker -E -B --loglevel=INFO
beat: celery -A celery_worker.celery beat -E -B --loglevel=INFO
