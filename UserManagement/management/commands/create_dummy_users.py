from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth import get_user_model
from Profiles.models import Profile
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = "Generate dummy users"

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Number of users to create')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        fake = Faker()

        fake.unique.clear()  # Clear any previously generated unique data
        users_to_create = []
        profiles_to_create = []  # Changed to list

        usernames = set()  # To ensure unique usernames in-memory

        try:
            with transaction.atomic():  # Start a transaction
                for _ in range(total):
                    # Generate a unique username
                    username = fake.user_name()

                    while username in usernames or User.objects.filter(username=username).exists():
                        username = fake.user_name()  # Regenerate if exists

                    usernames.add(username)

                    # Create the user
                    user = User(
                        full_name=fake.name(),
                        email=fake.unique.email(),
                        username=username,
                        password=User.objects.make_random_password(),  # Generate a hashed password
                        is_staff=False,
                        is_superuser=False,
                        email_verified=True
                    )
                    users_to_create.append(user)

                    self.stdout.write(self.style.SUCCESS(
                        f"Creating user: Username: {username}, Email: {user.email}, Full Name: {user.full_name}"
                    ))

     
                User.objects.bulk_create(users_to_create)

               
                for user in users_to_create:
                    profiles_to_create.append(Profile(user=user))  # Append to list

                # Bulk create profiles
                Profile.objects.bulk_create(profiles_to_create)

                self.stdout.write(self.style.SUCCESS(f'Successfully created {total} users and profiles'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
