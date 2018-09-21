import wargame_web.settings.base as base

# Overwrite the DEBUG variable
base.DEBUG = False

# Import all variables from the base settings
from .base import *

SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = ['wargame.sch.bme.hu']
