from rest_framework import serializers
from Profiles.models import *
from django.contrib.contenttypes.models import ContentType
from .models import *

class ContentObjectRelatedField(serializers.RelatedField):
    def to_representation(self, data):
        if isinstance(data, Post):
            return {"type": "Post", "user": data.profile.user.username, "id": data.id}
        elif isinstance(data, Profile):
            return {'type': "Profile", "user": data.user.username, "id": data.id}
        elif isinstance(data, Comment):
            return {'type': "Comment", "user": data.user.username, "id": data.id}
        elif isinstance(data, Reels):
            return {"type": "Reels", "user": data.profile.user.username, "id": data.id}
        elif isinstance(data, ReelComment):
            return {'type': "ReelComment", "user": data.user.username, "id": data.id}

    def to_internal_value(self, data):
        content_type = data.get('content_type', "")
        object_id = data.get('id')

        if content_type == "post":
            try:
                return Post.objects.get(id=object_id)
            except Post.DoesNotExist:
                raise serializers.ValidationError("Post with this id does not exist.")
        elif content_type == "profile":
            try:
                return Profile.objects.get(id=object_id)
            except Profile.DoesNotExist:
                raise serializers.ValidationError("Profile with this id does not exist.")
        elif content_type == "comment":
            try:
                return Comment.objects.get(id=object_id)
            except Comment.DoesNotExist:
                raise serializers.ValidationError("Comment with this id does not exist.")
        elif content_type == "reel":
            try:
                return Reels.objects.get(id=object_id)
            except Reels.DoesNotExist:
                raise serializers.ValidationError("Reel with this id does not exist.")
        elif content_type == "reelcomment":
            try:
                return ReelComment.objects.get(id=object_id)
            except ReelComment.DoesNotExist:
                raise serializers.ValidationError("ReelComment with this id does not exist.")
        else:
            raise serializers.ValidationError("Invalid content type provided.")

class ReportPostSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model'
    )
    content_obj = ContentObjectRelatedField(read_only=True)

    class Meta:
        model = ReportPost
        fields = "__all__"
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['content_obj'] = self.fields['content_obj'].to_representation(instance.content_object)
        return representation

    def create(self, data):
        request = self.context.get('request')
        reported_post, created = ReportPost.objects.get_or_create(
            user=request.user,
            content_type=data['content_type'],
            object_id=data['object_id'],
        )
        if not created:
            reported_post.count += 1
            reported_post.reason = f"{reported_post.reason} \n {data['reason']}"
        else:
            reported_post.reason = data['reason']
            reported_post.count = 1
        reported_post.save()
        return reported_post