"""
WSGI config for payment_certificates project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment_certificates.settings')

application = get_wsgi_application()
