from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser , PermissionsMixin
from . manager import CustomUserManager


class User(AbstractBaseUser , PermissionsMixin):
    username = models.CharField(max_length=50 , unique=True)
    full_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=255 , unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    email_verified = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)
    objects = CustomUserManager()


    
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["full_name" , "email"]
    

    def __str__(self):
        return self.username
    


