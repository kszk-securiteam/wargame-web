import wargame_web.settings.base as base

# Overwrite the DEBUG variable
base.DEBUG = True

# Import all variables from the base settings
from .base import *

SECRET_KEY = 'j0s5#e@upiqv=anz8brrdwp&*1&s&z@i-usvdwo=m$kk!t3j8!'

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = ['127.0.0.1']
