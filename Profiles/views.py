from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from . models import *
from . serializers import *
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from django.db.models import Q
from .pagination import *
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from itertools import chain
from Chat.models import Notification
from . tasks import create_notification_accepting_req

class AuthenticatedView(APIView):
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me(request):
    try:
        profile = Profile.objects.get(user = request.user)
        serializer = ProfileSerializer(profile,context={"request":request})
        response_data = {
            'username':request.user.username,
            'profile':serializer.data
        }
        return Response(response_data,status=status.HTTP_200_OK)
    except Profile.DoesNotExist:
        return Response({"message":"Profile not found"},status=status.HTTP_404_NOT_FOUND)
    

class UpdateProfileView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return  Profile.objects.get(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request,id):
    try:
        profile = Profile.objects.get(user__username=id)
        serializer = ProfileSerializer(profile,context={'request':request})
        return Response(serializer.data,status=status.HTTP_200_OK)                      
    except Profile.DoesNotExist:
        return Response({"message":"Profile not found"},status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_profile(request) :
    try:
        search_query = request.GET.get('q')
        if not search_query:
            return Response({"message":"Please enter a search query"},status=status.HTTP_400_BAD_REQUEST)
        if len(search_query)>0:
            profiles = Profile.objects.filter(
                Q(user__username__icontains=search_query) |
                Q(user__full_name__startswith=search_query)
                
            ).distinct()

        
            serializer = ProfileSerializer(profiles[:10], many=True, context={'request': request})

            return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FollowProfileView(AuthenticatedView):
    def get(self, request, id):
        try:
            current_user_profile = Profile.objects.get(user=request.user)
            user_profile = Profile.objects.get(user__username=id)
            
            follow, created = Follow.objects.get_or_create(
                follower=current_user_profile,
                following=user_profile
            )
            
            if created:
                follow.accepted = not user_profile.isPrivate
            else:
                if follow.disabled:
                    follow.disabled = False
                    follow.accepted = not user_profile.isPrivate
                else:
                    follow.disabled = True
                    follow.accepted = False  

            follow.save()

            follow_status_text = 'Unfollowed' if follow.disabled else ('Requested to' if not follow.accepted else 'Followed')
            follow_status_code = 'n' if follow.disabled else ('r' if not follow.accepted else 'f')
            
            return Response(
                {
                    "message": f"You have {follow_status_text} {user_profile.user.username}!",
                    "follow_status": follow_status_code
                },
                status=status.HTTP_200_OK
            )

        except Profile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_followers(request, id):
    try:
        
        profile = Profile.objects.get(user__username=id)

       
        followers = Profile.objects.filter(following__following=profile, following__disabled=False , following__accepted=True).distinct().order_by('-id')


      
        serializer = ProfileSerializer(followers, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Profile.DoesNotExist:
        return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def FollowAcceptView(request,id,nid):
    follow = Follow.objects.get(id=id)
    if request.user.profile == follow.following:
        follow.accepted=True
        follow.save()
        create_notification_accepting_req.delay(id)
        # Notification.objects.get(id=nid).delete()
        return Response({'message':True},status=status.HTTP_200_OK)
    return Response({'message':False},status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def FollowDisableView(request, id,nid):
    follow = Follow.objects.get(id=id)
    if request.user.profile == follow.following:
        follow.disabled=True
        follow.save()
        # Notification.objects.get(id=nid).delete()
        
        return Response({'message':True},status=status.HTTP_200_OK)
    return Response({'message':False},status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_following(request, id):
    try:

        
        profile = Profile.objects.get(user__username=id)
        
       
        following = Profile.objects.filter(followers__follower=profile, followers__disabled=False,followers__accepted=True, ).distinct().order_by('-id')


      
        serializer = ProfileSerializer(following, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Profile.DoesNotExist:
        return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    

class ListPostView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, id):
        try:
            posts = Post.objects.filter(profile__user__username = id).order_by('-id')
            serailizer = PostSerializer(posts,many=True,context={'request':request})
            
            return Response(serailizer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'details':str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    
class PostDetailsView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'id'


class DeletePost(APIView):
    def delete(self, request, id):
        post = Post.objects.get(id=id)
        if post.profile.user.id == request.user.id:
            post.delete()
            return Response({"message":"Post deleted successfully"},status=status.HTTP_200_OK)
        
        return Response({"message":"Unauthorized action"},status=status.HTTP_401_UNAUTHORIZED)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def like_post(request , id):
    post = Post.objects.get(id=id)
    obj , created = Like.objects.get_or_create(post=post,profile=request.user.profile)
    obj.enabled = not obj.enabled
    obj.save()
    
    return Response({'message': ("Likes" if obj.enabled else "Unliked") + " Successfully"}, status=status.HTTP_200_OK)


class CommentView(APIView):
    def get(self, request, id):
        try:
            selected_comment_id = request.GET.get("selected_comment")
            reply_status = request.GET.get("reply_status") == "true"
            print(selected_comment_id, reply_status)
            
            current_user = request.user.profile
            followed_profiles = Follow.objects.filter(follower=current_user, accepted=True).values_list('following', flat=True)

            comments = Comment.objects.filter(post__id=id, parent__isnull=True).annotate(
                is_followed=Q(profile__in=followed_profiles)
            ).order_by('-is_followed', '-created_at')

            selected_comment = None

            if selected_comment_id:
                selected_comment = Comment.objects.filter(id=selected_comment_id, post__id=id).first()

                if selected_comment:
                    if reply_status and selected_comment.parent:
                        selected_comment = selected_comment.parent

                    comments = comments.exclude(id=selected_comment.id)  
                    comments = [selected_comment] + list(comments)  
            
            paginator = CommentPagination()
            paginated_comments = paginator.paginate_queryset(comments, request)

            serializer_context = {
                'request': request,
            }
            if reply_status:
                serializer_context['reply_status'] = reply_status
                serializer_context['selected_comment_id'] = selected_comment_id

            serializer = CommentSerializer(paginated_comments, many=True, context=serializer_context)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            print(e)
            return Response({"message": "Some error occurred"}, status=status.HTTP_400_BAD_REQUEST)

        
    def post(self,request,id):

        try:
            request.data['post'] = id
            request.data['profile'] = request.user.profile.id
            serializer = CommentSerializer(data=request.data,context={'request':request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({"message":"Some Error occured"},status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request,id):
        try:
            
            comment = Comment.objects.get(id=id)
            if not comment.profile == request.user.profile:
                return Response({"message":"You don't have permission to delete this comment"},status=status.HTTP_403_FORBIDDEN)
            comment.delete()
            return Response({"message":"Comment deleted successfully"},status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({"message":"Comment not found"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message":"Some Error occured"},status=status.HTTP_400_BAD_REQUEST)
        


class ReplyView(APIView):


    def get(self, request, id):
        try:
            current_user = request.user.profile

            followed_profiles = Follow.objects.filter(follower=current_user, accepted=True).values_list('following',flat=True)

            replies = Comment.objects.filter(parent__id=id).annotate(
                is_followed=Q(profile__in=followed_profiles)
            ).order_by('-is_followed', '-created_at') 
            paginator = CommentPagination()
            paginated_replies = paginator.paginate_queryset(replies,request)

            serializer = CommentSerializer(paginated_replies,many=True,context={'request':request})
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            print(e)
            return Response({"message":"Some Error occured"},status=status.HTTP_400_BAD_REQUEST)
        

    def post(self,request,id):
        try:
            request.data['parent'] = id
            request.data['profile'] = request.user.profile.id
            request.data['post'] = Comment.objects.get(id=id).post.id
            print(request.data)
            serializer = CommentSerializer(data=request.data,context={'request':request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({"message":"Some Error occured"},status=status.HTTP_400_BAD_REQUEST)
        

class ReplyToReplyView(APIView):
    def post(self, request, id):
        try:
           reply_parent = Comment.objects.get(id=id)


        except:
            return Response({"message":"Reply not found"},status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['parent'] = reply_parent.parent.id
        data['reply_parent'] = reply_parent.id
        data['profile'] = request.user.profile.id
        data['post'] = reply_parent.post.id

        serializer = CommentSerializer(data=data,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    





class PostRecommendationView(APIView):
    def get(self, request):
        try:
            profile = request.user.profile
            recommendation = Recommendation_Posts.objects.filter(profile=profile).order_by('-id').first()
            liked_post_ids = Like.objects.filter(profile=profile, enabled=True).values_list('post_id', flat=True)
            
            following_ids = profile.following.filter(accepted=True).values_list('following_id', flat=True)
            time_threshold = timezone.now() - timedelta(days=1)
            
            recent_posts_from_following = Post.objects.filter(
                profile__id__in=following_ids,
                created_at__gte=time_threshold
            ).exclude(
                Q(ai_reported=True) |
                Q(id__in=liked_post_ids) |
                Q(profile__user__full_name__isnull=True)
            ).annotate(likes_count=Count('likes')).order_by('-created_at', '-likes_count')
            
            recommended_posts = []
            if recommendation:
                recommended_post_ids = recommendation.recommendation.get("recommended_post_ids", [])
                recommended_posts = Post.objects.filter(id__in=recommended_post_ids).exclude(
                    Q(ai_reported=True) |
                    Q(id__in=liked_post_ids) |
                    Q(profile__user__full_name__isnull=True)
                ).annotate(likes_count=Count('likes')).order_by('-likes_count')

            if not following_ids or not recent_posts_from_following:
                trending_posts = Post.objects.exclude(
                    Q(ai_reported=True) |
                    Q(id__in=liked_post_ids) |
                    Q(profile__user__full_name__isnull=True)
                ).annotate(likes_count=Count('likes')).order_by('-likes_count')[:50]  

                posts = list(chain(recent_posts_from_following, recommended_posts, trending_posts))
            else:
                posts = list(chain(recent_posts_from_following, recommended_posts))
            
            paginator = PostPagination()
            paginated_posts = paginator.paginate_queryset(posts, request)
            serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            print(e)
            return Response({"message": "Some Error occurred"}, status=status.HTTP_400_BAD_REQUEST)



class ReelView(generics.CreateAPIView):
    serializer_class = ReelSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)


class ListReelView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, id):
        try:
            posts = Reels.objects.filter(profile__user__username = id).order_by('-id')
            serailizer = ReelSerializer(posts,many=True,context={'request':request})
            
            return Response(serailizer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'details':str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    
class ReelsDetailsView(generics.RetrieveAPIView):
    queryset = Reels.objects.all()
    serializer_class = ReelSerializer
    lookup_field = 'id'


class DeleteReel(APIView):
    def delete(self, request, id):
        reel = Reels.objects.get(id=id)
        if reel.profile.user.id == request.user.id:
            reel.delete()
            return Response({"message":"Reel deleted successfully"},status=status.HTTP_200_OK)
        
        return Response({"message":"Unauthorized action"},status=status.HTTP_401_UNAUTHORIZED)
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def like_reel(request , id):
    reel = Reels.objects.get(id=id)
    obj , created = ReelLike.objects.get_or_create(reel=reel,profile=request.user.profile)
    obj.enabled = not obj.enabled
    obj.save()
    
    return Response({'message': ("Likes" if obj.enabled else "Unliked") + " Successfully"}, status=status.HTTP_200_OK)



class ReelCommentView(APIView):
    def get(self, request, id):
        try:
            selected_comment_id = request.GET.get("selected_comment")
            reply_status = request.GET.get("reply_status") == "true"
            
            current_user = request.user.profile
            followed_profiles = Follow.objects.filter(follower=current_user, accepted=True).values_list('following', flat=True)

            comments = ReelComment.objects.filter(reel__id=id, parent__isnull=True).annotate(
                is_followed=Q(profile__in=followed_profiles)
            ).order_by('-is_followed', '-created_at')

            selected_comment = None

            if selected_comment_id:
                selected_comment = ReelComment.objects.filter(id=selected_comment_id, reel__id=id).first()
                if selected_comment:
                    if reply_status and selected_comment.parent:
                        selected_comment = selected_comment.parent
                    comments = comments.exclude(id=selected_comment.id)
                    comments = [selected_comment] + list(comments)
            
            paginator = CommentPagination()
            paginated_comments = paginator.paginate_queryset(comments, request)

            serializer_context = {'request': request}
            if reply_status:
                serializer_context['reply_status'] = reply_status
                serializer_context['selected_comment_id'] = selected_comment_id

            serializer = ReelCommentSerializer(paginated_comments, many=True, context=serializer_context)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            print(e)
            return Response({"message": "Some error occurred"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, id):
        try:
            request.data['reel'] = id
            request.data['profile'] = request.user.profile.id
            serializer = ReelCommentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({"message": "Some Error occurred"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            comment = ReelComment.objects.get(id=id)
            if not comment.profile == request.user.profile:
                return Response({"message": "You don't have permission to delete this comment"}, status=status.HTTP_403_FORBIDDEN)
            comment.delete()
            return Response({"message": "Comment deleted successfully"}, status=status.HTTP_200_OK)
        except ReelComment.DoesNotExist:
            return Response({"message": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": "Some Error occurred"}, status=status.HTTP_400_BAD_REQUEST)


class ReelReplyView(APIView):
    def get(self, request, id):
        try:
            current_user = request.user.profile
            followed_profiles = Follow.objects.filter(follower=current_user, accepted=True).values_list('following', flat=True)
            replies = ReelComment.objects.filter(parent__id=id).annotate(
                is_followed=Q(profile__in=followed_profiles)
            ).order_by('-is_followed', '-created_at') 
            paginator = CommentPagination()
            paginated_replies = paginator.paginate_queryset(replies, request)

            serializer = ReelCommentSerializer(paginated_replies, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            print(e)
            return Response({"message": "Some Error occurred"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, id):
        try:
            request.data['parent'] = id
            request.data['profile'] = request.user.profile.id
            request.data['reel'] = ReelComment.objects.get(id=id).reel.id
            serializer = ReelCommentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({"message": "Some Error occurred"}, status=status.HTTP_400_BAD_REQUEST)


class ReelReplyToReplyView(APIView):
    def post(self, request, id):
        try:
            reply_parent = ReelComment.objects.get(id=id)
        except:
            return Response({"message": "Reply not found"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['parent'] = reply_parent.parent.id
        data['reply_parent'] = reply_parent.id
        data['profile'] = request.user.profile.id
        data['reel'] = reply_parent.reel.id

        serializer = ReelCommentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReelRecommendationView(APIView):
    def get(self, request):
        try:
            recommendation = Recommendation_Reels.objects.filter(profile=request.user.profile).order_by('-id').first()
            liked_reel_ids = ReelLike.objects.filter(profile=request.user.profile, enabled=True).values_list('reel_id', flat=True)

            if recommendation and recommendation.recommendation.get("recommended_reel_ids"):
                recommended_reel_ids = recommendation.recommendation.get("recommended_reel_ids", [])
                reels = Reels.objects.filter(id__in=recommended_reel_ids).exclude(
                    Q(ai_reported=True) |
                    Q(id__in=liked_reel_ids) |
                    Q(profile__user__full_name__isnull=True)
                ).annotate(likes_count=Count('likes')).order_by('-likes_count')
            else:
                reels = Reels.objects.exclude(
                    Q(ai_reported=True) |
                    Q(id__in=liked_reel_ids) |
                    Q(profile__user__full_name__isnull=True)
                ).annotate(likes_count=Count('likes')).order_by('-likes_count')

            paginator = ReelPagination()
            paginated_reels = paginator.paginate_queryset(reels, request)
            serializer = ReelSerializer(paginated_reels, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            print(e)
            return Response({"message": "Some Error occurred"}, status=status.HTTP_400_BAD_REQUEST)
