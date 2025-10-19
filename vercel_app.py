import os
import sys
import django
from django.conf import settings
from django.core.wsgi import get_wsgi_application

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Setup Django
django.setup()

# Create the WSGI application
app = get_wsgi_application()

# Vercel expects the app to be named 'app'
application = app