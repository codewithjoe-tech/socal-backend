from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
import base64
from django.utils.crypto import get_random_string

User = get_user_model()




class Chatroom(models.Model):
    CHATROOM_TYPES = [
        ('dm', 'Direct Message'),
        ('group', 'Group Chat'),
    ]

    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    chat_type = models.CharField(max_length=10, choices=CHATROOM_TYPES, default='dm')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_chatrooms")

    def __str__(self):
        return self.name or f"Chatroom {self.id}"



    


class ChatroomUser(models.Model):
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE, related_name='chatroom_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatroom_memberships')
    in_chat = models.BooleanField(default =False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chatroom', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.chatroom.name or 'Chatroom ' + str(self.chatroom.id)}"

    def save(self, *args, **kwargs):
        if not self.pk: 
            if self.chatroom.chat_type == 'dm' and self.chatroom.chatroom_users.count() >= 2:
                raise ValidationError("This chatroom is a Direct Message and already has 2 users. No more users can join.")
        
        super().save(*args, **kwargs)


class Message(models.Model):
    chatroom = models.ForeignKey(Chatroom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    ALLOWED_MODELS = ['textmessage', 'imagemessage', 'videomessage', 'audiomessage']

    def clean(self):
        if self.content_type.model not in self.ALLOWED_MODELS:
            raise ValidationError(f"Invalid content type: {self.content_type.model}. Allowed content types are: {', '.join(self.ALLOWED_MODELS)}")
        
        deleted_entry = ChatRoomDeleted.objects.filter(chatroom=self.chatroom).first()
        if deleted_entry:
            deleted_entry.disabled = True
            deleted_entry.save()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message by {self.sender.username} in {self.chatroom.name}"




class TextMessage(models.Model):
    text = models.TextField()

    def __str__(self):
        return f"Text: {self.text[:30]}"



class ImageMessage(models.Model):
    image = models.ImageField(upload_to='chat-images/') 

    def __str__(self):
        return f"Image Message: {self.image.name}"
    


class VideoMessage(models.Model):
    video = models.FileField(upload_to='chat-videos/')  

    def __str__(self):
        return f"Video Message: {self.video.name}"


class AudioMessage(models.Model):
    audio = models.FileField(upload_to='chat-audio/')  

    def __str__(self):
        return f"Audio Message: {self.audio.name}"



class ChatRoomDeleted(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    chatroom = models.ForeignKey(Chatroom, blank=True, null=True, on_delete=models.SET_NULL)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return f"Deleted chatroom by {self.user.username} - Chatroom {self.chatroom.name or self.chatroom.id}"
