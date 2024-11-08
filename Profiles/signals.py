
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Reels,Like,ReelLike,ReelComment,Comment,Post
from .tasks import *

@receiver(post_save, sender=Reels)
def create_thumbnail_on_save(sender, instance, created, **kwargs):
    if created and not instance.thumbnail:
        generate_thumbnail_for_reel.delay(instance.id)


@receiver(post_save , sender=Like)
def generate_recommendation(sender,instance ,created, **kwargs):
    if created:
        recommend_posts_for_user(instance.profile.id)

@receiver(post_save , sender=ReelLike)
def generate_reel_recommendatoin(sender,instance,created , **kwargs):
    if created:
     
        recommend_posts_for_user(instance.profile.id)


@receiver(post_save,sender=Reels)
def create_notification_for_followers_on_reel_upload(sender,instance,created, **kwargs):
    if created:
        print("working")
        create_notification_reels.delay(instance.id)


@receiver(post_save , sender=ReelLike)
def create_notification_for_reels_like(sender, instance, created, **kwargs):
    if created:
        if instance.enabled:
            create_notification_reelLike.delay(instance.id)
    else :
        if not instance.enabled:
            delete_notification_reelLike.delay(instance.id)
        elif instance.enabled:
            create_notification_reelLike.delay(instance.id)


@receiver(post_save , sender=ReelComment)
def create_notification_for_reel_comment(sender,instance, created, **kwargs):
    if created:
        create_notification_reel.delay(instance.id)



# Post



@receiver(post_save,sender=Post)
def create_notification_for_followers_on_post_upload(sender,instance,created, **kwargs):
    if created:
        print("working")
        create_notification_posts.delay(instance.id)




@receiver(post_save , sender=Like)
def create_notification_for_post_like(sender, instance, created, **kwargs):
    if created:
        if instance.enabled:
            create_notification_postLike.delay(instance.id)
    else :
        if not instance.enabled:
            delete_notification_postLike.delay(instance.id)
        elif instance.enabled:
            create_notification_postLike.delay(instance.id)


@receiver(post_save , sender=Comment)
def create_notification_for_post_comment(sender,instance, created, **kwargs):
    if created:
        create_notification_post_comment.delay(instance.id)


@receiver(post_save , sender=Follow)
def follow_notification(sender, instance , created , **kwargs):
    if not instance.disabled:
        create_notification_follow.delay(instance.id)

    else:
        delete_notification_follow(instance.id)
    
    if instance.accepted:
        delete_notification_follow(instance.id)
