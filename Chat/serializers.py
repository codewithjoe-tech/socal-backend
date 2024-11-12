from rest_framework import serializers
from . models import *
from Profiles.models import *
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType




class ChatRoomSerializer(serializers.ModelSerializer):
    has_unread = serializers.SerializerMethodField(read_only=True)
    other_user = serializers.SerializerMethodField(read_only=True)
    last_message = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Chatroom
        fields = ["name","has_unread","other_user","last_message","id"]


    def get_has_unread(self, obj):
        request = self.context.get('request')
        current_user = request.user
      
        messages = Message.objects.filter(chatroom=obj,seen=False).exclude(sender=current_user).count()
        return messages
    
    def get_other_user(self,obj):
        request = self.context.get('request')
        current_user = request.user
        other_user = ChatroomUser.objects.filter(chatroom=obj).exclude(user=current_user).first().user
        profile = Profile.objects.get(user=other_user)
        data=  {
            "username": profile.user.username,
            
            "full_name": profile.user.full_name
        
        }

        if profile.profile_picture:
           data[ "profile_picture"]=   profile.profile_picture.url 
        else :
            data["profile_picture"]= "/user.png"

        return data
    def get_last_message(self, obj):
        last_message = Message.objects.filter(chatroom=obj).order_by('-timestamp').first()

        if not last_message:
            return None

        if isinstance(last_message.content_object, TextMessage):
            return last_message.content_object.text  
        elif isinstance(last_message.content_object, ImageMessage):
            return "Image"  
        elif isinstance(last_message.content_object, VideoMessage):
            return "Video" 
        elif isinstance(last_message.content_object, AudioMessage):
            return "Audio"

        return "Unknown Message Type" 




class TextMessageSerializer(serializers.ModelSerializer):




    class Meta:
        model = TextMessage
        fields = ['text']
class ImageMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageMessage
        fields = ['image']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = f"{instance.image.url}"  
        return representation


class VideoMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoMessage
        fields = ['video']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['video'] = f"{instance.video.url}"  
        return representation
    
    # def validate(self,data):
    #     from moviepy.editor import VideoFileClip
    #     video = data.get('video')
    #     if video:
    #         clip = VideoFileClip(video)
    #         duration = clip.duration
    #         if duration>60:
    #             raise ValidationError("The video should be of the length 2 minutes")
    #     return data


class AudioMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioMessage
        fields = ['audio']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['audio'] = f"{instance.audio.url}"  
        return representation



class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField() 
    content_type = serializers.SlugRelatedField(
        slug_field='model', queryset=ContentType.objects.all())  
    content_object = serializers.SerializerMethodField()  
    profile_picture = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Message
        fields = ['id', 'chatroom', 'sender', 'content_type', 'content_object', 'timestamp', 'seen',"profile_picture"]

    def get_content_object(self, obj):
        if isinstance(obj.content_object, TextMessage):
            return TextMessageSerializer(obj.content_object).data
        elif isinstance(obj.content_object, ImageMessage):
            return ImageMessageSerializer(obj.content_object).data
        elif isinstance(obj.content_object, VideoMessage):
            return VideoMessageSerializer(obj.content_object).data
        elif isinstance(obj.content_object, AudioMessage):
            return AudioMessageSerializer(obj.content_object).data
        return None  
    def validate(self, data):
        content_type = data['content_type'].model
        allowed_models = Message.ALLOWED_MODELS
        if content_type not in allowed_models:
            raise serializers.ValidationError(f"Invalid content type '{content_type}'. Allowed types are: {', '.join(allowed_models)}")
        return data


    def get_profile_picture(self, obj):
        if obj.sender.profile.profile_picture:
            
            return f"{obj.sender.profile.profile_picture.url}"
        else:
            return '/user.png'  





class NotificationSerilaizer(serializers.ModelSerializer):
    content_object = serializers.SerializerMethodField()
    content_type = serializers.CharField(source ="content_type.model",read_only=True)
    class Meta:
        model = Notification
        fields= ['user', 'content_type', 'object_id', 'content', 'content_object','created_at', 'id']

    def get_content_object(self,obj):
        content_type = obj.content_type
        model_class = content_type.model_class()
        try:
        # Attempt to get the related object instance
            instance = model_class.objects.get(pk=obj.object_id)
        except model_class.DoesNotExist:
            # If the related object doesn't exist, return None or a custom response
            return None  # or {'error': 'Original content has been deleted'}
        
        if isinstance(instance, Reels):
            return {
                'username': instance.profile.user.username,
                "profile_picture":  instance.profile.profile_picture.url if instance.profile.profile_picture else None,
                "ReelId": instance.id,
                "thumbnail":  instance.thumbnail.url
            }
        elif isinstance(instance, ReelLike):
            return {
                'username': instance.profile.user.username,
                "profile_picture":  instance.profile.profile_picture.url if instance.profile.profile_picture else None,
                "ReelId": instance.reel.id,
                "thumbnail":  instance.reel.thumbnail.url
            }
        elif isinstance(instance, ReelComment):
            return {
                "username": instance.profile.user.username,
                "profile_picture":  instance.profile.profile_picture.url if instance.profile.profile_picture else None,
                "ReelId": instance.reel.id,
                "thumbnail":  instance.reel.thumbnail.url,
                "reply": True if instance.parent else False,
                'id': instance.id
            }
        elif isinstance(instance, Post):
            return {
                'username': instance.profile.user.username,
                "profile_picture":  instance.profile.profile_picture.url if instance.profile.profile_picture else None,
                "postId": instance.id,
                "image":  instance.image.url
            }
        elif isinstance(instance, Like):
            return {
                'username': instance.profile.user.username,
                "profile_picture":  instance.profile.profile_picture.url if instance.profile.profile_picture else None,
                "postId": instance.post.id,
                "image":  instance.post.image.url
            }
        elif isinstance(instance, Comment):
            
            return {
                "username": instance.profile.user.username,
                "profile_picture":  instance.profile.profile_picture.url if instance.profile.profile_picture else None,
                "postId": instance.post.id,
                "image":  instance.post.image.url,
                "reply": True if instance.parent else False,
                'id': instance.id
            }
        elif isinstance(instance, Follow):
            return {
                'username': instance.follower.user.username,
                'profile_picture':  instance.follower.profile_picture.url if instance.follower.profile_picture else None,
                "id": instance.id,
                'accepted': instance.accepted
            }
