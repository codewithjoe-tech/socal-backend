from Profiles.models import Post, Like, Profile
import numpy as np
from sklearn.decomposition import TruncatedSVD




# from django.utils import timezone
# from datetime import timedelta

# time_threshold = timezone.now() - timedelta(days=1)

# recently_updated_likes = Like.objects.filter(enabled=True, updated_at__gte=time_threshold).order_by('-updated_at')
# for like in recently_updated_likes:
#     user_idx = profile_index[like.profile.id]
#     post_idx = post_index[like.post.id]
#     user_post_matrix[user_idx, post_idx] = 1

def data_preprocessing_post():
    profiles = Profile.objects.all()
    posts = Post.objects.all()
    profile_index = {profile.id: idx for idx, profile in enumerate(profiles)}
    post_index = {post.id: idx for idx, post in enumerate(posts)}
    user_post_matrix = np.zeros((len(profiles), len(posts)))
    likes = Like.objects.filter(enabled=True).order_by('-updated_at')[:200]
    for like in likes:
        user_idx = profile_index[like.profile.id]
        post_idx = post_index[like.post.id]
        user_post_matrix[user_idx,post_idx] = 1

    return profile_index , post_index , user_post_matrix

def factorize_matrix(user_post_matrix):
    svd = TruncatedSVD(n_components=10)
    user_factors = svd.fit_transform(user_post_matrix)
    post_factors = svd.components_.T
    return user_factors, post_factors