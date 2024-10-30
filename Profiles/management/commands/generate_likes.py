import random
from django.core.management.base import BaseCommand, CommandError
from Profiles.models import Profile, Post, Like

class Command(BaseCommand):
    help = 'Generate a specified number of random likes for each post'

    def add_arguments(self, parser):
        parser.add_argument('like_count', type=int, help='Number of likes to generate per post')

    def handle(self, *args, **options):
        like_count = options['like_count']
        profiles = Profile.objects.all()
        posts = Post.objects.all()

        if like_count > len(profiles):
            raise CommandError(f"Cannot generate {like_count} likes per post as there are only {len(profiles)} profiles.")

        for post in posts:
            existing_likes = Like.objects.filter(post=post).values_list('profile', flat=True)
            available_profiles = [profile for profile in profiles if profile.id not in existing_likes]
            
            if len(available_profiles) < like_count:
                raise CommandError(f"Not enough available profiles to generate {like_count} unique likes for post {post.id}.")
            
            liked_profiles = random.sample(available_profiles, like_count)

            for profile in liked_profiles:
                Like.objects.create(post=post, profile=profile, enabled=True)
                self.stdout.write(self.style.SUCCESS(f'{profile} liked post {post.id}'))
