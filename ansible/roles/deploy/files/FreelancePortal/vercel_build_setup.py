
# vercel_build_setup.py
import os
import django
from django.core.management import call_command

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FreelancePortal.settings")
django.setup()

# Run migrations
call_command("makemigrations")
call_command("migrate")

print("Vercel build setup completed successfully!")