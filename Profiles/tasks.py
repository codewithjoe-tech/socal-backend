from celery import shared_task
from .post_recommendation_utils import data_preprocessing_post,factorize_matrix
from . models import Profile,Recommendation_Posts
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
        
    

