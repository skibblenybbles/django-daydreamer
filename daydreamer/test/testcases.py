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
        Returns a unique string (a UUID) that can be useful in tests when
        you don't want to make up a dummy value.
        
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
