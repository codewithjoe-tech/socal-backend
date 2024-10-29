from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import *
from rest_framework import status
from .utils import send_email
from ReportApp.models import ReportPost
from ReportApp.serializers import ReportPostSerializer
from django.contrib.contenttypes.models import ContentType
from Profiles.models import Post,Comment,Profile
from . serializers import ReportSerializer


User = get_user_model()

class PublicApi(APIView):
    permission_classes = (IsAdminUser,)
    
class UsersView(PublicApi):
    def get(self, request):
        try:
            users = User.objects.all()
            serializer = GetUsersSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
            user.delete()
            users = User.objects.all()
            serializer = GetUsersSerializer(users, many=True)
            send_email(
                "Account Deleted",
                f"Dear {user.full_name}, your account has been deleted by the admin.",
                [user.email]
            )
            return Response({"message": "User deleted successfully", "users": serializer.data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, id):
        try:
            user = User.objects.get(id=id)
            user.banned = not user.banned
            user.save()
            users = User.objects.all()
            serializer = GetUsersSerializer(users, many=True)
            status_message = "banned" if user.banned else "unbanned"
            send_email(
                f"Account {status_message.capitalize()}",
                f"Dear {user.full_name}, your account has been {status_message} by the admin.",
                [user.email]
            )
            return Response({"message": "User status updated successfully", "users": serializer.data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 

class Reported(PublicApi):
    def get(self, request, type):
        try:
            model_map = {
                "post": Post,
                "comment": Comment,
                "profile": Profile
            }
            
            model_class = model_map.get(type.lower())
            
            if model_class is None:
                return Response({"error": f"Invalid type '{type}' provided"}, status=status.HTTP_400_BAD_REQUEST)

            content_type = ContentType.objects.get_for_model(model_class)
            
            reports = ReportPost.objects.filter(content_type=content_type,disabled=False).values_list('object_id', flat=True)

            if type.lower() == "post":
                posts = Post.objects.filter(id__in=reports)
                serializer = PostSerializer(posts, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif type.lower() == "comment":
                comments = Comment.objects.filter(id__in=reports)
                serializer = CommentSerializer(comments, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif type.lower() == "profile":
                profiles = Profile.objects.filter(id__in=reports)
                serializer = ProfileSerializer(profiles, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def delete(self,request, id):
        select_value = request.GET.get('selected_value')
        try:

            content_type = None
            if select_value == "post":
                content_type = ContentType.objects.get_for_model(Post)
            elif select_value == "comment":
                content_type = ContentType.objects.get_for_model(Comment)
            elif select_value == "profile":
                content_type = ContentType.objects.get_for_model(Profile)

            
            print(content_type)

            report = ReportPost.objects.filter(content_type=content_type, object_id=id, disabled=False)
            print(report)
            if report.exists():
                report.update(disabled=True)
                return Response({"message": "Reports successfully disabled"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No active reports found"}, status=status.HTTP_404_NOT_FOUND)


        except ReportPost.DoesNotExist:
            return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class ReportedReason(PublicApi):
    def get(self,request,id):
        print("Working")
        select_value = request.GET.get('selected_value')
        print(select_value)
        try:

            content_type = None
            if select_value == "post":
                content_type = ContentType.objects.get_for_model(Post)
            elif select_value == "comment":
                content_type = ContentType.objects.get_for_model(Comment)
            elif select_value == "profile":
                content_type = ContentType.objects.get_for_model(Profile)

            reports = ReportPost.objects.filter(content_type=content_type,object_id=id,disabled=False)
            serializer = ReportSerializer(reports, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReportPost.DoesNotExist:
            return Response({"error": "Report not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        select_value = request.GET.get('selected_value')
        try:
            content_type = None
            model = None
            
            if select_value == "post":
                content_type = ContentType.objects.get_for_model(Post)
                model = Post
            elif select_value == "comment":
                content_type = ContentType.objects.get_for_model(Comment)
                model = Comment
            elif select_value == "profile":
                content_type = ContentType.objects.get_for_model(Profile)
                model = Profile

            reports = ReportPost.objects.filter(content_type=content_type, object_id=id, disabled=False)
            if reports.exists():
                reports.delete()
                obj = model.objects.get(id=id)
                obj.delete()

                return Response({"message": f"{select_value.capitalize()} and reports successfully deleted"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No active reports found"}, status=status.HTTP_404_NOT_FOUND)

        except model.DoesNotExist:
            return Response({"error": f"{select_value.capitalize()} not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
