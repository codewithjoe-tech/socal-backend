import random
from django.core.management.base import BaseCommand, CommandError
from Profiles.models import Profile, Reels, ReelLike

class Command(BaseCommand):
    help = 'Generate a specified number of random likes for each reel'

    def add_arguments(self, parser):
        parser.add_argument('like_count', type=int, help='Number of likes to generate per reel')

    def handle(self, *args, **options):
        like_count = options['like_count']
        profiles = Profile.objects.all()
        reels = Reels.objects.all()

        if like_count > len(profiles):
            raise CommandError(f"Cannot generate {like_count} likes per reel as there are only {len(profiles)} profiles.")

        for reel in reels:
            existing_likes = ReelLike.objects.filter(reel=reel).values_list('profile', flat=True)
            available_profiles = [profile for profile in profiles if profile.id not in existing_likes]
            
            if len(available_profiles) < like_count:
                raise CommandError(f"Not enough available profiles to generate {like_count} unique likes for reel {reel.id}.")

            liked_profiles = random.sample(available_profiles, like_count)

            for profile in liked_profiles:
                ReelLike.objects.create(reel=reel, profile=profile, enabled=True)
                self.stdout.write(self.style.SUCCESS(f'{profile} liked reel {reel.id}'))
