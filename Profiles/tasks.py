from .reel_recommendation_utils import data_preprocessing_reel, factorize_reel_matrix
from celery import shared_task
from .post_recommendation_utils import data_preprocessing_post,factorize_matrix
from . models import Profile,Recommendation_Posts,Recommendation_Reels
import numpy as np
from django.db.models import Count




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
