#!/usr/bin/env python
# encoding: utf-8
"""
config.py

Created by Mike Babineau on 2010-02-05.
Copyright (c) 2010 Bizo. All rights reserved.
"""

from datetime import datetime, timedelta
from operator import itemgetter

# Uncomment and set to your Amazon credentials:
#AWS_ACCESS_KEY_ID = ""
#AWS_SECRET_ACCESS_KEY = ""

# Default values to use if a given parameter is not passed
DEFAULTS = {'calc_rate': False,
            'period': 60,
            'start_time': datetime.now() - timedelta(days=1),
            'end_time': datetime.now()}
