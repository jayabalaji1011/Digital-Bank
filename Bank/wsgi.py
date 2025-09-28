"""
WSGI config for Bank project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import sys
import os

project_home = '/home/jayabalaji2k/Digital-Bank'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# set the settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'Bank.settings'

# get the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
