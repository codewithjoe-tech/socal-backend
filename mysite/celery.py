from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# If you want to use the django-celery-beat scheduler, include this line
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
