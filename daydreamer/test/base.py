from __future__ import unicode_literals

import uuid

from django import test
from django.utils import encoding

from daydreamer.core import urlresolvers


class TestCase(test.TestCase):
    """
    A test case that enhances Django's base test case with common utilities.
    
    To turn on Django's CSRF framework during testing, set the
    enforce_csrf_checks attribute to True.
    
    """
    enforce_csrf_checks = False
    
    # Setup.
    def _pre_setup(self):
        """
        Replaces the default test client, providing a hook to specify whether
        to use Django's CSRF framework during testing.
        
        """
        super(TestCase, self)._pre_setup()
        self.client = self.client_class(
            enforce_csrf_checks=self.enforce_csrf_checks)
    
    # Utilities.
    def unique(self):
        """
        Returns a unique string (a UUID), useful for dummy values in tests.
        Helps to guarantee that functions or methods are not returning
        hardcoded values that coincidentally match a dummy value used in
        a test.
        
        """
        return encoding.force_text(uuid.uuid4())
    
    # Assertions.
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
