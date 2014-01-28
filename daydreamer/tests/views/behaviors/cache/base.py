from __future__ import unicode_literals

from django.core.cache import cache

from daydreamer.tests.views.core import http


class TestCase(http.TestCase):
    """
    Common utilities for testing cache view behaviors.
    
    """
    def setUp(self):
        cache.clear()
        super(TestCase, self).setUp()
    
    def tearDown(self):
        super(TestCase, self).tearDown()
        cache.clear()
