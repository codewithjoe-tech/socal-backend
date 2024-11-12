from celery import shared_task
from .models import ReportPost
from Profiles.models import Post
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import tempfile
import boto3
import opennsfw2 as n2

s3_client = boto3.client('s3')

@shared_task
def report_posts():
    post_contenttype = ContentType.objects.get_for_model(Post)
    reports = ReportPost.objects.filter(content_type=post_contenttype, disabled=False).values_list('object_id', flat=True)
    posts = Post.objects.filter(id__in=reports, ai_reported=False)
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    for post in posts:
        if not post.ai_reported:
            image_key = post.image.name
            with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_image_file:
                s3_client.download_file(bucket_name, image_key, temp_image_file.name)
                prob = n2.predict_image(temp_image_file.name)
                
                if round(prob * 10, 2) > 5:
                    post.ai_reported = True
                    post.save()

    return f"Task done for {reports}"
