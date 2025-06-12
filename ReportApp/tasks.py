from celery import shared_task
from .models import ReportPost
from Profiles.models import Post
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import opennsfw2 as n2
import os


@shared_task
def report_posts():
    post_contenttype = ContentType.objects.get_for_model(Post)
    reports = ReportPost.objects.filter(content_type=post_contenttype, disabled=False).values_list('object_id', flat=True)
    posts = Post.objects.filter(id__in=reports, ai_reported=False)

    for post in posts:
        if not post.ai_reported:
            image_path = os.path.join(settings.MEDIA_ROOT, post.image.name)
            try:
                prob = n2.predict_image(image_path)

                if round(prob * 10, 2) > 5:
                    post.ai_reported = True
                    post.save()

            except Exception as e:
                print(f"Error processing post {post.id}: {str(e)}")
                raise

    return f"Task done for {len(reports)} reports"
