# -*- coding: utf-8 -*-
"""
Client for communicating with the Enterprise API.
"""
# TODO Document the decision to use API client
# https://github.com/edx/edx-platform/blob/master/openedx/features/enterprise_support/api.py
# https://github.com/edx/edx-enterprise/blob/master/enterprise/api_client/enterprise.py
import datetime
import logging
from functools import wraps
from time import time
