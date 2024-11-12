from rest_framework import serializers
from django.contrib.auth import get_user_model
from Profiles.models import Profile,Post,Comment
from ReportApp.models import ReportPost




User = get_user_model()
 



class GetUsersSerializer(serializers.ModelSerializer):
    profile_id = serializers.SerializerMethodField(read_only=True)
    user_status = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name','profile_id','user_status','banned']

    def get_profile_id(self,obj):
        if obj.profile:
            return obj.profile.id
        return None
    
    def get_user_status(self, obj):
        if obj.is_superuser:
            return 'admin'
        elif obj.is_staff:
            return 'staff'
        else:
            return "normal"
        



class PostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['username','id','ai_reported']

    def get_username(self,obj):
        return obj.profile.user.username

    

    def get_ai_reported(self,obj):
        return obj.ai_reported

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    post_id = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['username','id','ai_reported','post_id','reply']

    def get_username(self,obj):
        return obj.profile.user.username
    
    def get_post_id(self,obj):
        return obj.post.id
    
    def get_reply(self,obj):
        if obj.parent:
            return True
        return False




class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['username','id','ai_reported']

    def get_username(self,obj):
        return obj.user.username

    

class ReportSerializer(serializers.ModelSerializer):

    username = serializers.SerializerMethodField()
    class Meta:
        model = ReportPost
        fields = ['username','reason','id']


    def get_username(self,obj):
        try:

            return obj.profile.user.username
        except:
            return obj.user.username
        


from rest_framework import serializers
from Profiles.models import Reels, ReelComment

class ReelsSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()

    class Meta:
        model = Reels
        fields = ['username', 'id', 'description', 'like_count', 'comment_count', 'ai_reported', 'created_at']

    def get_username(self, obj):
        return obj.profile.user.username


class ReelCommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    reel_id = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField()

    class Meta:
        model = ReelComment
        fields = ['username', 'id', 'content', 'reel_id', 'ai_reported', 'reply', 'created_at']

    def get_username(self, obj):
        return obj.profile.user.username

    def get_reel_id(self, obj):
        return obj.reel.id

    def get_reply(self, obj):
        return obj.parent is not None
