from django.urls import path
from . views import *



urlpatterns = [
    path("me",get_me,name="me"),
    path("update/me",UpdateProfileView.as_view()),
    path("get/<id>",get_profile,name="profile"),
    path("search/",search_profile,name="profile"),
    path('follow/<id>' ,  FollowProfileView.as_view()),
    path('upload/post/', PostView.as_view()),
    path('followers/<id>', get_followers, name="followers"),
    path('following/<id>', get_following, name="followers"),
    path('posts/<id>',ListPostView.as_view()),
    path('post/<id>',PostDetailsView.as_view()),
    path('post/delete/<id>',DeletePost.as_view()),
    path('like/<id>',like_post),
    path('comments/<id>',CommentView.as_view()),
    path('comments/reply/<id>',ReplyView.as_view()),
    path('comments/reply-to-reply/<id>',ReplyToReplyView.as_view()),

]