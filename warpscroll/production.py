from warpscroll.settings import *
from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

import dj_database_url

db_from_env = dj_database_url.config()
DATABASES['default'].update(db_from_env)

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
