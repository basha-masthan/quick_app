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

# For Vercel, we need to handle the ASGI application as well
from django.core.asgi import get_asgi_application
asgi_app = get_asgi_application()

# Ensure database is ready for Vercel deployment
from django.core.management import execute_from_command_line
try:
    from django.db import connection
    connection.ensure_connection()
except Exception as e:
    print(f"Database connection error: {e}")
    # For Vercel, we might need to run migrations if database is empty
    try:
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
    except:
        pass