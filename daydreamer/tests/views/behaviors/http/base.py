from __future__ import unicode_literals

import calendar
import datetime

from django.utils import http

from daydreamer.tests.views import core


class TestCase(core.TestCase):
    """
    Common utilities for testing HTTP view behaviors.
    
    """
    # Utilities.
    def format_etag(self, etag):
        """
        Quote the given ETag for use in an HTTP header.
        
        """
        return http.quote_etag(etag)
    
    def format_datetime(self, dt):
        """
        Format a datetime for use in an HTTP header.
        
        """
        return http.http_date(calendar.timegm(dt.utctimetuple()))
