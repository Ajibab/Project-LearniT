from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from django.apps import apps, AppConfig

##-- To set the default Django settings module for Celery--##
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')

app = Celery('core')

class CeleryConfig(AppConfig):
    name = 'core'
    verbose_name = 'Celery Config'

    def ready(self):
        app.config_from_object('django.conf:settings',namespace='CELERY')
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(installed_apps,force=True)

    