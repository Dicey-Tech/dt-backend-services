import os

from learninghub.settings.base import *

# IN-MEMORY TEST DATABASE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}
# END IN-MEMORY TEST DATABASE

# Make some loggers less noisy (useful during test failure)
import logging

for logger_to_silence in ["faker", "jwkest", "edx_rest_framework_extensions"]:
    logging.getLogger(logger_to_silence).setLevel(logging.WARNING)
# Specifically silence license manager event_utils warnings
logging.getLogger("event_utils").setLevel(logging.ERROR)
