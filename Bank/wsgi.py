"""
WSGI config for Bank project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import sys
import os

# set the settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'Bank.settings'

# get the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
