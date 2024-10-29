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


class AuthenticatedView(APIView):
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me(request):
    try:
        profile = Profile.objects.get(user = request.user)
        serializer = ProfileSerializer(profile)
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
            
            if not created:
                follow.disabled = not follow.disabled
                follow.save()

            follow_status = 'Unfollowed' if follow.disabled else 'Followed'
            return Response(
                {"message": f"You have {follow_status} {user_profile.user.username}!"},
                status=status.HTTP_200_OK
            )

        except Profile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
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

       
        followers = Profile.objects.filter(following__following=profile, following__disabled=False).distinct().order_by('-id')


      
        serializer = ProfileSerializer(followers, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Profile.DoesNotExist:
        return Response({"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_following(request, id):
    try:

        
        profile = Profile.objects.get(user__username=id)
        
       
        following = Profile.objects.filter(followers__follower=profile, followers__disabled=False).distinct().order_by('-id')


      
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