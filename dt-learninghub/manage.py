#!/usr/bin/env python
"""
Django administration utility.
"""

import os
import sys

PWD = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "learninghub.settings.local")
    sys.path.append(PWD)
    try:
        from django.core.management import (  # pylint: disable=wrong-import-position
            execute_from_command_line,
        )
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django  # noqa F401
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
