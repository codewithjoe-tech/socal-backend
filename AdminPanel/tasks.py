from celery import shared_task
from . utils import send_email



@shared_task
def send_mail_to_users_deleted(fullname , email):
    send_email(
                "Account Deleted",
                f"Dear {fullname}, your account has been deleted by the admin.",
                [email]
            )
    
@shared_task
def send_mail_users_banned_or_unbanned(fullname , message, email):
    send_email(
                f"Account {message.capitalize()}",
                f"Dear {fullname}, your account has been {message} by the admin.",
                [email]
            )