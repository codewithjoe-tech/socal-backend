
from Profiles.models import Reels, ReelLike, Profile
import numpy as np
from sklearn.decomposition import TruncatedSVD

def data_preprocessing_reel():
    profiles = Profile.objects.all()
    reels = Reels.objects.all()
    profile_index = {profile.id: idx for idx, profile in enumerate(profiles)}
    reel_index = {reel.id: idx for idx, reel in enumerate(reels)}
    user_reel_matrix = np.zeros((len(profiles), len(reels)))
    likes = ReelLike.objects.filter(enabled=True).order_by('-updated_at')[:200]
    for like in likes:
        user_idx = profile_index[like.profile.id]
        reel_idx = reel_index[like.reel.id]
        user_reel_matrix[user_idx, reel_idx] = 1
        
    return profile_index, reel_index, user_reel_matrix

def factorize_reel_matrix(user_reel_matrix):
    svd = TruncatedSVD(n_components=2)
    user_factors = svd.fit_transform(user_reel_matrix)
    reel_factors = svd.components_.T
    return user_factors, reel_factors