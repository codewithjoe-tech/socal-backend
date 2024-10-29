from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth import get_user_model
from Profiles.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = "Generate dummy users"

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of users to be created')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        fake = Faker()

        for _ in range(total):
            user = User.objects.create_user(
                full_name=fake.name(),
                email=fake.email(),
                username=fake.user_name(), 
                password="password123",  
                is_staff=False,
                is_superuser=False,
                email_verified=True
            )
            profile = Profile.objects.create(user=user)
            profile.save()
            user.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully created {total} users'))
