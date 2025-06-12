from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth import get_user_model
from dotenv import load_dotenv
import os

load_dotenv()

frontend = 'https://friendbook.codewithjoe.in'




def send_verification_email(user):
    print("Sending email")
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verified_link = f"{frontend}/verify-email/{uid}/{token}"
    template_message = render_to_string("verification_email.html",{
        'username':user,
        'verification_link':verified_link
    })
    message = f"""Hello {user.full_name},\n\tClick the following link to verify your account\n{verified_link}"""

    send_mail(
        subject="Email Verification",
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        html_message=template_message
    )




def verify_email(request, uidb64, token):
    User = get_user_model()

    uid = urlsafe_base64_decode(force_str(uidb64)).decode()
    user = User.objects.get(pk=uid)
    if default_token_generator.check_token(user, token):
        user.email_verified = True
        user.save()
        return True
    else:
        
        return False