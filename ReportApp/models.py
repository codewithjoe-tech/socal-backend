from django.db import models
from django.contrib.auth import get_user_model
from Profiles.models import Post
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import  GenericForeignKey


# Create your models here.

User = get_user_model()

class ReportPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True,blank=True)
    content_object = GenericForeignKey('content_type','object_id')
    count = models.PositiveIntegerField(default=0)
    reason = models.TextField(null=True,blank=True)
    disabled = models.BooleanField(default=False)
    




    def __str__(self):
        return f"{self.user} reported {self.content_type} - {self.object_id}"
    
    @property
    def get_count(self):
        return ReportPost.objects.filter(content_type=self.content_type,object_id=self.object_id,).count()
        
