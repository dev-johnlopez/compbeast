web: flask db upgrade; gunicorn compbeast:app
worker: celery -A celery_worker.celery worker
beat: celery -A celery_worker.celery beat
