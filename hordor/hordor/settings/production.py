import os
from hordor.settings.common import *

SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False

# SECURITY WARNING: update this when you have the production host
ALLOWED_HOSTS = ['0.0.0.0', 'localhost']
