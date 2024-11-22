import os
import random
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from Profiles.models import Profile, Post, Like

class Command(BaseCommand):
    help = 'Generate categorized posts from dataset images and assign likes from users within the same category'

    def handle(self, *args, **options):
        categories = ['bike', 'cars', 'cats', 'dogs', 'flowers', 'horses', 'human']
        data_folder = settings.DATASET_DIR

        profiles = Profile.objects.all()
        if len(profiles) < len(categories):
            self.stdout.write(self.style.ERROR("Not enough profiles to assign to all categories."))
            return
        
        categorized_profiles = self.categorize_profiles(profiles, categories)

        posts_to_create = []
        likes_to_create = []

        for category, profile_list in categorized_profiles.items():
            folder_path = os.path.join(data_folder, category)
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                        file_path = os.path.join(folder_path, filename)
                        profile = random.choice(profile_list)
                        posts_to_create.append(
                            Post(
                                profile=profile,
                                image=File(open(file_path, 'rb'), name=filename),
                                content=f"Random post from {category}"
                            )
                        )

        created_posts = Post.objects.bulk_create(posts_to_create)
        self.stdout.write(self.style.SUCCESS(f'Created {len(created_posts)} posts.'))

        for post in created_posts:
            category = self.get_post_category(post.image.name, categories)
            if category and category in categorized_profiles:
                available_profiles = categorized_profiles[category]
                num_likes = random.randint(5, 15)
                like_profiles = random.sample(available_profiles, min(len(available_profiles), num_likes))

                for profile in like_profiles:
                    likes_to_create.append(Like(post=post, profile=profile, enabled=True))

        if likes_to_create:
            Like.objects.bulk_create(likes_to_create)
            self.stdout.write(self.style.SUCCESS(f'Successfully created {len(likes_to_create)} likes.'))
        else:
            self.stdout.write(self.style.WARNING('No likes were created.'))

    def categorize_profiles(self, profiles, categories):
        
        categorized_profiles = {category: [] for category in categories}
        profiles = list(profiles)
        random.shuffle(profiles)

        for i, profile in enumerate(profiles):
            category = categories[i % len(categories)] 
            categorized_profiles[category].append(profile)

        return categorized_profiles

    def get_post_category(self, filename, categories):
        """
        Infer the category of a post based on its file name.
        """
        for category in categories:
            if category in filename.lower():
                return category
        return None
