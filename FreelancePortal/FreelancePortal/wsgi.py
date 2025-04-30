"""
WSGI config for FreelancePortal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FreelancePortal.settings')

application = get_wsgi_application()

# Add this for Vercel deployment
app = application  # Vercel looks for a variable named 'app'

# Alternatively, you can use this:
# handler = application  # Vercel also accepts a variable named 'handler'