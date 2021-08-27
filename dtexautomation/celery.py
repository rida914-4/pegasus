""""""

from __future__ import absolute_import

__author__ = "Ridah Naseem"
__credits__ = [""]
__version__ = "1.0.1"
__maintainer__ = "Ridah Naseem"
__email__ = "ridah.naseem@pegasussystems.com"
__status__ = "Development"

import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pegasusautomation.settings')
app = Celery('pegasusautomation')


# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    """"""
    logger.debug('Request: {0!r}'.format(self.request))
