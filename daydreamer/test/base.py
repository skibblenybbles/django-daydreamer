from __future__ import unicode_literals

import uuid

from django import test
from django.utils import encoding

from daydreamer.core import urlresolvers


class TestCase(test.TestCase):
    """
    A test case that provides common utilities.
    
    """
    def unique(self):
        """
        Returns a unique string (a UUID), useful for dummy values in tests.
        Helps to guarantee that functions or methods are not returning
        hardcoded values that coincidentally match a test's dummy value.
        
        """
        return encoding.force_text(uuid.uuid4())
    
    def assertRedirects(self, response, expected_url, query=None,
            *args, **kwargs):
        """
        Asserts that the response was redirected as expected. If provided,
        the query dictionary is added to the expected URL's query string.
        
        """
        return super(TestCase, self).assertRedirects(
            response, urlresolvers.update_query(
                expected_url, query),
            *args, **kwargs)
