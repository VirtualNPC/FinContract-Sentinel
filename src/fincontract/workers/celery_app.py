from celery import Celery

from fincontract.core.config import settings

celery_app = Celery("fincontract", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_routes = {"fincontract.workers.tasks.*": {"queue": "audit"}}
