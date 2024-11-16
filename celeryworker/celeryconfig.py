CELERY_BROKER_URL = 'redis://myrediscluster.ojibst.ng.0001.aps1.cache.amazonaws.com:6379/0'
CELERY_RESULT_BACKEND = 'redis://myrediscluster.ojibst.ng.0001.aps1.cache.amazonaws.com:6379/1'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
