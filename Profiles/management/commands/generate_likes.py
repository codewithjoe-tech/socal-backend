import random
from django.core.management.base import BaseCommand, CommandError
from Profiles.models import Profile, Post, Like


class Command(BaseCommand):
    help = 'Generate a specified number of random likes for each post, ensuring no duplicate likes'

    def add_arguments(self, parser):
        parser.add_argument(
            'like_count', 
            type=int, 
            help='Number of likes to generate per post'
        )

    def handle(self, *args, **options):
        like_count = options['like_count']
        profiles = Profile.objects.all()
        posts = Post.objects.all()

        # Check if there are enough profiles to generate the required likes
        if like_count > len(profiles):
            raise CommandError(
                f"Cannot generate {like_count} likes per post as there are only {len(profiles)} profiles."
            )

        likes_to_create = []

        for post in posts:
            # Get profiles that have already liked the post
            existing_likes = Like.objects.filter(post=post).values_list('profile', flat=True)
            # Exclude profiles that have already liked the post
            available_profiles = [profile for profile in profiles if profile.id not in existing_likes]

            # Ensure enough profiles are available for this post
            if len(available_profiles) < like_count:
                raise CommandError(
                    f"Not enough available profiles to generate {like_count} unique likes for post {post.id}."
                )

            # Randomly select profiles to like this post
            liked_profiles = random.sample(available_profiles, like_count)

            # Create Like objects
            for profile in liked_profiles:
                likes_to_create.append(Like(post=post, profile=profile, enabled=True))

                # Print the profile ID and post ID when adding to likes_to_create
                self.stdout.write(self.style.SUCCESS(f"Adding Like: Profile ID = {profile.id}, Post ID = {post.id}"))

        # Bulk create all likes at once
        if likes_to_create:
            Like.objects.bulk_create(likes_to_create)
            self.stdout.write(self.style.SUCCESS(f'Successfully created {len(likes_to_create)} likes.'))
        else:
            self.stdout.write(self.style.SUCCESS('No new likes were created.'))
