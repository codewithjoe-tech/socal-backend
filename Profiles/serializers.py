from rest_framework import serializers
from . models import *
from UserManagement.serializers import UserModelSerializer
from django.utils import timesince





class ProfileSerializer(serializers.ModelSerializer):
    user = UserModelSerializer(read_only=True)
    is_following = serializers.SerializerMethodField(read_only=True)
    followers_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)
 
    posts_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Profile
        fields = "__all__"

    def get_is_following(self, obj):
        request = self.context.get('request')
       
        if request :
            try:
               
                current_user_profile = Profile.objects.get(user=request.user)
                follow = Follow.objects.filter(follower=current_user_profile, following=obj, disabled=False).first()
                return follow is not None
            except Profile.DoesNotExist:
                return False
        
        return False
    def get_followers_count(self,obj):
        follow = Follow.objects.filter(following=obj,disabled=False).count()
        return follow
    
    def get_following_count(self,obj):
        follow = Follow.objects.filter(follower=obj,disabled=False).count()
        return follow


    
    def get_posts_count(self, obj):
        posts = Post.objects.filter(profile=obj).count()
        return posts
    



class PostSerializer(serializers.ModelSerializer):
    time_of_post = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count =serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__' 

    def get_time_of_post(self, obj):
        return obj.updated_at
    
    def get_profile(self,obj):
        request = self.context.get('request')
        profile = obj.profile
        return {
            'full_name':profile.user.full_name or "",
            'username':profile.user.username,
            'id':profile.id,
            "profile_picture":request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else '/user.webp'
        }

    def get_like_count(self,obj):
        return obj.like_count
    
    def get_comment_count(self,obj):
        return obj.comment_count
    
    def get_user_liked(self,obj):
        request = self.context.get('request')
        user = request.user
        likes = Like.objects.filter(post=obj,profile=user.profile,enabled=True).exists()
        if likes:
            return True
        else:
            return False
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')


        if instance.ai_reported:
            representation['image'] = '/ai_reported.png'
            if request.user.is_superuser :
                representation['image'] = request.build_absolute_uri(instance.image.url)
                
        else:
            if instance.image:
                representation['image'] = request.build_absolute_uri(instance.image.url)

            else:
                representation['image'] = None
        return representation
        
class CommentSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    profile_id = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    has_replies = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = "__all__"


    def get_user(self,obj):
        return obj.profile.user.username
    

    def get_profile_pic(self, obj):
        request = self.context.get('request')
        profile = obj.profile
        return request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else '/user.webp'
    
    def get_profile_id(self, obj):
        return obj.profile.id
        
    def get_replies(self, obj):
        reply_status = self.context.get('reply_status', False)
        selected_comment_id = self.context.get('selected_comment_id', None)
        
        if reply_status and selected_comment_id:
            try:
                selected_comment = Comment.objects.get(id=selected_comment_id)

                if selected_comment.parent and selected_comment.parent.id == obj.id:
                    if selected_comment.reply_parent:
                        return [CommentSerializer(selected_comment.reply_parent,context=self.context).data,CommentSerializer(selected_comment,context=self.context).data]
                    return [CommentSerializer(selected_comment,context=self.context).data]

            except Comment.DoesNotExist:
                return [] 

        
        return []

    
    def get_has_replies(self, obj):
        return Comment.objects.filter(parent=obj).exists()

    




class ReelSerializer(serializers.ModelSerializer):
    time_of_post = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count =serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Reels
        fields = '__all__' 

    def get_time_of_post(self, obj):
        return obj.updated_at
    
    def get_profile(self,obj):
        request = self.context.get('request')
        profile = obj.profile
        return {
            'full_name':profile.user.full_name,
            'username':profile.user.username,
            'id':profile.id,
            "profile_picture":request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else '/user.webp'
        }

    def get_like_count(self,obj):
        return obj.like_count
    
    def get_comment_count(self,obj):
        return obj.comment_count
    
    def get_user_liked(self,obj):
        request = self.context.get('request')
        user = request.user
        likes = ReelLike.objects.filter(reel=obj,profile=user.profile,enabled=True).exists()
        if likes:
            return True
        else:
            return False
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')


        if instance.ai_reported:
            representation['video'] = '/ai_reported.png'
            if request.user.is_superuser :
                representation['video'] = request.build_absolute_uri(instance.video.url)
                
        else:
            if instance.video:
                representation['video'] = request.build_absolute_uri(instance.video.url)

            else:
                representation['video'] = None
        return representation