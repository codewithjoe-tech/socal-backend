from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="users/profile", null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    isPrivate = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    show_status = models.BooleanField(default=True)
    ai_reported = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} Profile"


class Follow(models.Model):
    follower = models.ForeignKey(Profile, related_name="following", on_delete=models.CASCADE)
    following = models.ForeignKey(Profile, related_name="followers", on_delete=models.CASCADE)
    accepted = models.BooleanField(default=True)
    disabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.user} follows {self.following.user}"


class Post(models.Model):   
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name="posts")
    image = models.ImageField(upload_to='user/posts/', null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    hide_likes = models.BooleanField(default=False)
    hide_comments = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ai_reported = models.BooleanField(default=False)

    def __str__(self):
        return self.content[:50]+f" by {self.profile.user}"

    @property
    def like_count(self):
        return Like.objects.filter(post=self,enabled=True).count()

    @property
    def comment_count(self):
        return self.comments.count()

class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('post', 'profile')
        indexes = [
            models.Index(fields=['post']),
        ]

    def __str__(self):
        return f"{self.profile.user} liked post {self.post.id}"

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)
    reply_parent = models.ForeignKey('self', related_name='reply_to_reply', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ai_reported = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.profile.user} on post {self.post.id}"




class Reels(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="reels")
    video = models.FileField(upload_to='user/reels/')
    description = models.TextField(null=True, blank=True)
    hide_likes = models.BooleanField(default=False)
    hide_comments = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ai_reported = models.BooleanField(default=False)

    def __str__(self):
        return self.description[:50] + f" by {self.profile.user}"

    @property
    def like_count(self):
        return ReelLike.objects.filter(reel=self, enabled=True).count()

    @property
    def comment_count(self):
        return self.comments.count()

class ReelLike(models.Model):
    reel = models.ForeignKey(Reels, related_name='likes', on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('reel', 'profile')
        indexes = [
            models.Index(fields=['reel']),
        ]

    def __str__(self):
        return f"{self.profile.user} liked reel {self.reel.id}"

class ReelComment(models.Model):
    reel = models.ForeignKey(Reels, related_name='comments', on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, null=True, blank=True)
    reply_parent = models.ForeignKey('self', related_name='reply_to_reply', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ai_reported = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.profile.user} on reel {self.reel.id}"



class Recommendation_Posts(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="recommendation_posts",null=True, blank=True)
    recommendation = models.JSONField()

