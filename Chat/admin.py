
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django import forms
from .models import *

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_content_types = ContentType.objects.filter(model__in=['textmessage', 'imagemessage', 'videomessage', 'audiomessage'])
        self.fields['content_type'].queryset = allowed_content_types

class MessageInline(admin.TabularInline):
    model = Message
    form = MessageForm
    extra = 1
    readonly_fields = ('timestamp',)


class ChatroomUsers(admin.TabularInline):
    model = ChatroomUser

class ChatroomAdmin(admin.ModelAdmin):
    inlines = [MessageInline,ChatroomUsers]
    list_display = ('name', 'created_at')

admin.site.register(Chatroom, ChatroomAdmin)
admin.site.register(TextMessage)
admin.site.register(ImageMessage)
admin.site.register(VideoMessage)
admin.site.register(AudioMessage)
admin.site.register(Message)
admin.site.register(ChatRoomDeleted)
admin.site.register(ChatroomUser)
admin.site.register(Notification)
