from django.shortcuts import render
from Profiles.models import Post
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from . models import *
from django.contrib.contenttypes.models import ContentType
from . serializers import *


from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ReportPost
from .serializers import ReportPostSerializer

class ReportPostView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self,request):
        print(request.data)
        request.data['user']=request.user.id
        serializer = ReportPostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Reported Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    