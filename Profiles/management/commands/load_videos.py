import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from Profiles.models import Profile
from Profiles.models import Reels

class Command(BaseCommand):
    help = 'Generate reels from videos in Reel Data folder'

    def handle(self, *args, **options):
        video_folder = os.path.join(settings.BASE_DIR, 'Reel Videos')  
        profiles = Profile.objects.all()

        if os.path.exists(video_folder):
            for filename in os.listdir(video_folder):
                if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    file_path = os.path.join(video_folder, filename)
                    profile = random.choice(profiles)
                    with open(file_path, 'rb') as video_file:
                        reel = Reels(
                            profile=profile,
                            video=File(video_file, name=filename),
                            description=f"Random reel from {filename}"
                        )
                        reel.save()
                        self.stdout.write(self.style.SUCCESS(f'Created reel for {filename} by {profile.user}'))
        else:
            self.stdout.write(self.style.ERROR(f'Video folder not found: {video_folder}'))
