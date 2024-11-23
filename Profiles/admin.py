from django.contrib import admin
from django.contrib import messages
from .models import Profile, Follow, Post, Like, Comment, Recommendation_Posts, Reels, ReelLike, ReelComment, Recommendation_Reels

def delete_all_posts(modeladmin, request, queryset):
    Post.objects.all().delete()
    messages.success(request, "All posts have been deleted.")


def delete_profiles_with_no_user(modeladmin, request, queryset):
    profiles_to_delete = Profile.objects.filter(user=None)
    count = profiles_to_delete.count() 
    profiles_to_delete.delete()
    messages.success(request, f"{count} profiles with no associated user have been deleted.")




def delete_all_reels(modeladmin, request, queryset):
    Reels.objects.all().delete()
    messages.success(request, "All reels have been deleted.")

def delete_all_reel_suggestion(modeladmin , request ,queryset):
    Recommendation_Reels.objects.all().delete()
    messages.success(request,"All Reel recommendation deleted.")

def delete_all_post_suggestion(modeladmin , request ,queryset):
    Recommendation_Posts.objects.all().delete()
    messages.success(request,"All Reel recommendation deleted.")

def delete_all_reelLikes(modeladmin,request,queryset):
    ReelLike.objects.all().delete()




@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    actions = [delete_profiles_with_no_user]

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    actions = [delete_all_posts] 

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass

@admin.register(Recommendation_Posts)
class RecommendationPostsAdmin(admin.ModelAdmin):
    actions = [delete_all_post_suggestion]

@admin.register(Reels)
class ReelsAdmin(admin.ModelAdmin):
    actions = [delete_all_reels] 

@admin.register(ReelLike)
class ReelLikeAdmin(admin.ModelAdmin):
    actions = [delete_all_reelLikes]
@admin.register(ReelComment)
class ReelCommentAdmin(admin.ModelAdmin):
    pass

@admin.register(Recommendation_Reels)
class RecommendationReelsAdmin(admin.ModelAdmin):
    actions = [delete_all_reel_suggestion]
