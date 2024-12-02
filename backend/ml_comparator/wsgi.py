"""
WSGI config for ml_comparator project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ml_comparator.settings')

application = get_wsgi_application() 