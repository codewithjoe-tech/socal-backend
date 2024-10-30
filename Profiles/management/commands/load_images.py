import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from Profiles.models import Profile, Post

class Command(BaseCommand):
    help = 'Generate posts from dataset images'

    def handle(self, *args, **options):
        data_folder = settings.DATASET_DIR
        categories = ['bike', 'cars', 'cats', 'dogs', 'flowers', 'horses', 'human']
        profiles = Profile.objects.all()

        for category in categories:
            folder_path = os.path.join(data_folder, category)
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                        file_path = os.path.join(folder_path, filename)
                        profile = random.choice(profiles)
                        with open(file_path, 'rb') as img_file:
                            post = Post(
                                profile=profile,
                                image=File(img_file, name=filename),
                                content=f"Random post from {category}"
                            )
                            post.save()
                            self.stdout.write(self.style.SUCCESS(f'Created post for {filename} by {profile.user}'))
