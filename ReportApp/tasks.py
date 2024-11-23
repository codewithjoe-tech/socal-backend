from celery import shared_task
from .models import ReportPost
from Profiles.models import Post
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
import tempfile
from azure.storage.blob import BlobServiceClient
import opennsfw2 as n2


@shared_task
def report_posts():
    post_contenttype = ContentType.objects.get_for_model(Post)
    reports = ReportPost.objects.filter(content_type=post_contenttype, disabled=False).values_list('object_id', flat=True)
    posts = Post.objects.filter(id__in=reports, ai_reported=False)

    connection_string = settings.AZURE_CONNECTION_STRING
    container_name = settings.AZURE_MEDIA_CONTAINER

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    for post in posts:
        if not post.ai_reported:
            blob_name = post.image.name
            try:
                with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_image_file:
                    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                    with open(temp_image_file.name, "wb") as image_file:
                        image_file.write(blob_client.download_blob().readall())

                    prob = n2.predict_image(temp_image_file.name)

                    if round(prob * 10, 2) > 5:
                        post.ai_reported = True
                        post.save()

            except Exception as e:
                print(f"Error processing post {post.id}: {str(e)}")
                raise

    return f"Task done for {len(reports)} reports"
