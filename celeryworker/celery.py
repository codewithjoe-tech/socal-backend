from celery import Celery


app = Celery('mysite')
app.config_from_object('celeryconfig')