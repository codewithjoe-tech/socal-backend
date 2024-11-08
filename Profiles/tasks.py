from .reel_recommendation_utils import data_preprocessing_reel, factorize_reel_matrix
from celery import shared_task
from .post_recommendation_utils import data_preprocessing_post,factorize_matrix
from . models import Profile,Recommendation_Posts,Recommendation_Reels,Reels , Follow
import numpy as np
from django.db.models import Count
import os
import ffmpeg
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.contenttypes.models import ContentType 
from . models import Post , Profile , Follow  , Reels ,ReelComment ,ReelLike , Comment , Like
import logging
from django.contrib.auth import get_user_model
from Chat.models import Notification

User = get_user_model()
logger = logging.getLogger(__name__)




        
    
@shared_task
def recommend_posts_for_user(profile_id):
    profile_index, post_index, user_post_matrix = data_preprocessing_post()
    user_factors, post_factors = factorize_matrix(user_post_matrix)
    
    profile = Profile.objects.get(id=profile_id)
    user_idx = profile_index[profile.id]
    user_factor = user_factors[user_idx].reshape(1, -1)
    
    top_n = 200
    scores = np.dot(user_factor, post_factors.T)
    top_post_indices = np.argsort(scores.flatten())[-top_n:][::-1]
    recommended_post_ids = [list(post_index.keys())[idx] for idx in top_post_indices]
    
    following_ids = profile.following.filter(accepted=True).values_list('following_id', flat=True)
    
    filtered_post_ids = Post.objects.filter(
        id__in=recommended_post_ids,
        profile__isPrivate=False
    ).union(
        Post.objects.filter(id__in=recommended_post_ids, profile__id__in=following_ids)
    ).values_list('id', flat=True)
    
    recommendation = Recommendation_Posts(
        recommendation={'profile_id': profile.id, 'recommended_post_ids': list(filtered_post_ids)},
        profile=profile
    )
    
    Recommendation_Posts.objects.filter(profile=profile).delete()
    recommendation.save()
    
    return f'Recommendations generated for profile {profile_id} successfully!'

@shared_task
def recommend_reels_for_user(profile_id):
    print('Working')
    profile_index, reel_index, user_reel_matrix = data_preprocessing_reel()
    if user_reel_matrix.shape[1] < 2:
        return f'Insufficient data for recommendations for profile {profile_id}.'
    user_factors, reel_factors = factorize_reel_matrix(user_reel_matrix)
    profile = Profile.objects.get(id=profile_id)
    user_idx = profile_index[profile.id]
    user_factor = user_factors[user_idx].reshape(1, -1)
    top_n = 60
    scores = np.dot(user_factor, reel_factors.T)
    top_reel_indices = np.argsort(scores.flatten())[-top_n:][::-1]
    recommended_reel_ids = [list(reel_index.keys())[idx] for idx in top_reel_indices]
    following_ids = profile.following.filter(accepted=True).values_list('following_id', flat=True)
    filtered_reel_ids = Reels.objects.filter(
        id__in=recommended_reel_ids,
        profile__isPrivate=False
    ).union(
        Reels.objects.filter(id__in=recommended_reel_ids, profile__id__in=following_ids)
    ).values_list('id', flat=True)
    recommendation = Recommendation_Reels(
        recommendation={'profile_id': profile.id, 'recommended_reel_ids': list(filtered_reel_ids)},
        profile=profile
    )
    Recommendation_Reels.objects.filter(profile=profile).delete()
    recommendation.save()
    return f'Reel recommendations generated for profile {profile_id} successfully!'


@shared_task
def generate_thumbnail_for_reel(reel_id):
    reel = Reels.objects.get(id=reel_id)
    if not reel.video or reel.thumbnail:
        return
    
    video_path = reel.video.path
    thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'user/reels/thumbnails', f'{reel_id}_thumbnail.jpg')
    
    os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)

    try:
        ffmpeg.input(video_path, ss=1).output(
            thumbnail_path, vframes=1, pix_fmt='yuv420p', update=True
        ).run()

        with open(thumbnail_path, 'rb') as f:
            reel.thumbnail.save(f'{reel_id}_thumbnail.jpg', ContentFile(f.read()), save=True)
    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if e.stderr else 'Unknown error'
        print(f'FFmpeg error for reel {reel_id}: {error_message}')
        raise RuntimeError('Thumbnail generation failed')
    finally:
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

@shared_task
def generate_thumbnails():
    reels = Reels.objects.filter(thumbnail__isnull=True)
    for reel in reels:
        generate_thumbnail_for_reel.delay(reel.id)



@shared_task
def create_notification_reels(reel_id):
    try:
        reel = Reels.objects.get(id=reel_id)
        followers = Follow.objects.filter(following=reel.profile).exclude(follower=reel.profile)
        content_type = ContentType.objects.get_for_model(Reels)
        
        for follow_relation in followers:
            follower_user = follow_relation.follower.user
            if follower_user:
                # if follower_user is not reel.profile.user:
                Notification.objects.create(
                    user=follower_user,
                    content_type=content_type,
                    object_id=reel.id,
                    content=f'New reel posted by {reel.profile.user.username}'
                )
        
        return f'Notification task completed for reel {reel_id}'

    except Exception as e:
        print(e)
        logger.error(f'Error creating notifications for reel {reel_id}: {e}')
        return f'Error with reel {reel_id}'




@shared_task
def create_notification_reelLike(reelLikeId):
    reel_like = ReelLike.objects.get(id=reelLikeId)
    if not reel_like.profile == reel_like.reel.profile:
        contenttype = ContentType.objects.get_for_model(ReelLike)
        Notification.objects.create(user = reel_like.reel.profile.user , content_type=contenttype , object_id = reel_like.id, content = f'Your Reel is liked by {reel_like.profile.user} ❤️')
        return f'Notification task completed for reel liking'
    


@shared_task
def delete_notification_reelLike(reelLikeId):
    reel_like = ReelLike.objects.get(reelLikeId)
    contenttype = ContentType.objects.get_for_model(ReelLike)
    Notification.objects.get(user = reel_like.reel.profile.user, content_type = contenttype , object_id = reelLikeId ).delete()
    return f'Notification deleted'


@shared_task
def create_notification_reel(id):
    reelcomment = ReelComment.objects.get(id=id)
    contenttype = ContentType.objects.get_for_model(ReelComment)
    if not reelcomment.parent and not  reelcomment.profile == reelcomment.reel.profile:
        Notification.objects.create(user= reelcomment.reel.profile.user , content_type = contenttype ,object_id = id, content=f'{reelcomment.profile.user.username} commented : "{reelcomment.content if len(reelcomment.content) < 15 else reelcomment.content[:15]+"..."}" on your reel'   )
    elif reelcomment.parent and not reelcomment.reply_parent and not  reelcomment.profile == reelcomment.parent.profile:
        Notification.objects.create(user = reelcomment.parent.profile.user,content_type =contenttype,object_id =id,content=f'{reelcomment.profile.user.username} replied : "{reelcomment.content if len(reelcomment.content) < 15 else reelcomment.content[:15]+"..."}" to your comment')
    elif reelcomment.reply_parent and not  reelcomment.profile == reelcomment.reply_parent.profile:
        Notification.objects.create(user=reelcomment.reply_parent.profile.user, content_type = contenttype, object_id=id ,content=f'{reelcomment.profile.user.username} replied : "{reelcomment.content if len(reelcomment.content) < 15 else reelcomment.content[:15]+"..."}" to your comment')










# Posts





@shared_task
def create_notification_posts(id):
    try:
        post = Post.objects.get(id=id)
        followers = Follow.objects.filter(following=post.profile).exclude(follower=post.profile)
        content_type = ContentType.objects.get_for_model(Post)
        
        for follow_relation in followers:
            follower_user = follow_relation.follower.user
            if follower_user:
                # if follower_user is not reel.profile.user:
                Notification.objects.create(
                    user=follower_user,
                    content_type=content_type,
                    object_id=post.id,
                    content=f'New post posted by {post.profile.user.username}'
                )
        
        return f'Notification task completed for post {id}'

    except Exception as e:
        print(e)
        logger.error(f'Error creating notifications for post {id}: {e}')
        return f'Error with post {id}'




@shared_task
def create_notification_postLike(id):
    post_like = Like.objects.get(id=id)
    if not post_like.profile == post_like.post.profile:
        contenttype = ContentType.objects.get_for_model(Like)
        Notification.objects.create(user = post_like.post.profile.user , content_type=contenttype , object_id = post_like.id, content = f'Your Post is liked by {post_like.profile.user} ❤️')
        return f'Notification task completed for post liking'
    


@shared_task
def delete_notification_postLike(id):
    post_like = Like.objects.get(id=id)
    contenttype = ContentType.objects.get_for_model(Like)
    Notification.objects.get(user = post_like.post.profile.user, content_type = contenttype , object_id = id ).delete()
    return f'Notification deleted'


@shared_task
def create_notification_post_comment(id):
    post_comment = Comment.objects.get(id=id)
    contenttype = ContentType.objects.get_for_model(Comment)
    if not post_comment.parent and not  post_comment.profile == post_comment.post.profile:
        Notification.objects.create(user= post_comment.post.profile.user , content_type = contenttype ,object_id = id, content=f'{post_comment.profile.user.username} commented : "{post_comment.content if len(post_comment.content) < 15 else post_comment.content[:15]+"..."}" on your post'   )
    elif post_comment.parent and not post_comment.reply_parent and not  post_comment.profile == post_comment.parent.profile:
        Notification.objects.create(user = post_comment.parent.profile.user,content_type =contenttype,object_id =id,content=f'{post_comment.profile.user.username} replied : "{post_comment.content if len(post_comment.content) < 15 else post_comment.content[:15]+"..."}" to your comment')
    elif post_comment.reply_parent and not  post_comment.profile == post_comment.reply_parent.profile:
        Notification.objects.create(user=post_comment.reply_parent.profile.user, content_type = contenttype, object_id=id ,content=f'{post_comment.profile.user.username} replied : "{post_comment.content if len(post_comment.content) < 15 else post_comment.content[:15]+"..."}"   to your comment')




@shared_task
def create_notification_follow(id):
    follow = Follow.objects.get(id=id)
    contenttype = ContentType.objects.get_for_model(Follow)
    if not follow.accepted:
        Notification.objects.create(user=follow.following.user, content_type=contenttype, object_id=follow.id, content=f'You have a follow request from: {follow.follower}')
    elif follow.accepted:
        Notification.objects.create(user=follow.following.user,content_type=contenttype, object_id=follow.id, content=f'You have a new follower {follow.follower}')
    
    return f'Notification task completed for follow {id}'



@shared_task
def delete_notification_follow(id):
    contenttype = ContentType.objects.get_for_model(Follow)
    Notification.objects.get(content_type = contenttype , object_id=id).delete()
    return f"Notification deleted"
