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





@shared_task
def recommend_posts():
    profile_index, post_index, user_post_matrix = data_preprocessing_post()
    user_factors, post_factors = factorize_matrix(user_post_matrix)
    
    top_n = 100
    recommendations = [] 

    for profile in Profile.objects.annotate(like_count=Count('like')).filter(like_count__gt=30):
        user_idx = profile_index[profile.id]
        user_factor = user_factors[user_idx].reshape(1, -1)
        
        scores = np.dot(user_factor, post_factors.T)
        
        top_post_indices = np.argsort(scores.flatten())[-top_n:][::-1]
        recommended_post_ids = [list(post_index.keys())[idx] for idx in top_post_indices]
        
        recommendations.append(
            Recommendation_Posts(
                recommendation={'profile_id': profile.id, 'recommended_post_ids': recommended_post_ids},
                profile=profile,
            )
        )
    
    Recommendation_Posts.objects.bulk_create(recommendations)
    return "Recommendations generated successfully!"
        
    




@shared_task
def recommend_reels():
    profile_index, reel_index, user_reel_matrix = data_preprocessing_reel()
    user_factors, reel_factors = factorize_reel_matrix(user_reel_matrix)
    
    top_n = 60
    recommendations = []

    for profile in Profile.objects.annotate(like_count=Count('reellike')):
        user_idx = profile_index[profile.id]
        user_factor = user_factors[user_idx].reshape(1, -1)
        
        scores = np.dot(user_factor, reel_factors.T)
        
        top_reel_indices = np.argsort(scores.flatten())[-top_n:][::-1]
        recommended_reel_ids = [list(reel_index.keys())[idx] for idx in top_reel_indices]
        
        recommendations.append(
            Recommendation_Reels(
                recommendation={'profile_id': profile.id, 'recommended_reel_ids': recommended_reel_ids},
                profile=profile,
            )
        )
    
    Recommendation_Reels.objects.bulk_create(recommendations)
    return "Reel recommendations generated successfully!"




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
            thumbnail_path, vframes=1, pix_fmt="yuv420p", update=True
        ).run()

        with open(thumbnail_path, 'rb') as f:
            reel.thumbnail.save(f'{reel_id}_thumbnail.jpg', ContentFile(f.read()), save=True)
    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if e.stderr else "Unknown error"
        print(f"FFmpeg error for reel {reel_id}: {error_message}")
        raise RuntimeError("Thumbnail generation failed")
    finally:
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

@shared_task
def generate_thumbnails():
    reels = Reels.objects.filter(thumbnail__isnull=True)
    for reel in reels:
        generate_thumbnail_for_reel.delay(reel.id)


@shared_task
def create_notification( model ):
    if isinstance(model, Reels):
        contenttype = ContentType.objects.get_for_model(Reels)
        followers = Follow.objects.filter(following=model.user).values_list('following')
        