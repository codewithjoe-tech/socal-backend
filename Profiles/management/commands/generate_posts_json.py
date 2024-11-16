import json
import random
from django.core.management.base import BaseCommand
from Profiles.models import Post, Profile


class Command(BaseCommand):
    help = "Bulk create posts from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', 
            type=str, 
            required=True, 
            help='Path to the JSON file containing post data.'
        )

    def handle(self, *args, **kwargs):
        json_file_path = kwargs['file']

        # Load profiles
        all_profiles = list(Profile.objects.all())
        if not all_profiles:
            self.stdout.write(self.style.ERROR("No profiles found. Please create profiles before running this command."))
            return

        # Load JSON data
        try:
            with open(json_file_path, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {json_file_path}"))
            return
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Invalid JSON file format."))
            return

        # Prepare posts for bulk creation
        posts_to_create = []
        for item in data:
            model = item.get("model")
            fields = item.get("fields", {})

            if model == "Profiles.post":
                image_url = fields.get("image")
                content = fields.get("content")
                hide_likes = fields.get("hide_likes", False)
                hide_comments = fields.get("hide_comments", False)
                created_at = fields.get("created_at")
                updated_at = fields.get("updated_at")
                ai_reported = fields.get("ai_reported", False)

                # Assign a random profile
                random_profile = random.choice(all_profiles)

                # Create a Post instance
                post = Post(
                    profile=random_profile,
                    image=image_url,
                    content=content,
                    hide_likes=hide_likes,
                    hide_comments=hide_comments,
                    created_at=created_at,
                    updated_at=updated_at,
                    ai_reported=ai_reported
                )
                posts_to_create.append(post)

        # Perform bulk creation
        Post.objects.bulk_create(posts_to_create)

        self.stdout.write(self.style.SUCCESS(f"Successfully created {len(posts_to_create)} posts."))
