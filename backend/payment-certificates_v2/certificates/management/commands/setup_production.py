from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Setup production environment'

    def handle(self, *args, **options):
        self.stdout.write('Setting up production environment...')
        
        # Run migrations
        call_command('migrate')
        
        # Collect static files
        call_command('collectstatic', '--noinput')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Creating superuser...')
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'  # Change this in production
            )
        
        self.stdout.write(
            self.style.SUCCESS('Production setup completed successfully!')
        )
