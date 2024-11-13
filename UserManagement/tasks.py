from celery import shared_task
from .utils import send_verification_email
from django.contrib.auth import get_user_model


@shared_task
def send_mails_to_users(user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    send_verification_email(user)
    return "Done"



