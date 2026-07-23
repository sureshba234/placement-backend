from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Creates a superuser/TPO admin for production'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='suresh1234bathina@gmail.com',
                password='Admin@12345',
                role='tpo_admin',
            )
            self.stdout.write('Superuser created successfully')
        else:
            self.stdout.write('Superuser already exists')
