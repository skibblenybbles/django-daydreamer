from __future__ import unicode_literals

from django.conf import settings

from daydreamer.tests.views import generic

from . import client


class TestCase(generic.TestCase):
    """
    Common utilities for testing CSRF view behaviors.
    
    CSRF middleware is disabled by default with the
    csrf_middleware_enabled attribute. CSRF processing during tests is
    enabled by default, and a specialized client for managing CSRF
    cookies is provided.
    
    """
    client_class = client.Client
    csrf_middleware_enabled = False
    enforce_csrf_checks = True
    
    def setUp(self):
        if not self.csrf_middleware_enabled:
            self._csrf_middleware = settings.MIDDLEWARE_CLASSES
            settings.MIDDLEWARE_CLASSES = tuple(
                middleware for middleware in settings.MIDDLEWARE_CLASSES
                if middleware != "django.middleware.csrf.CsrfViewMiddleware")
        super(TestCase, self).setUp()
    
    def tearDown(self):
        super(TestCase, self).tearDown()
        if not self.csrf_middleware_enabled:
            settings.MIDDLEWARE_CLASSES = self._csrf_middleware
            del self._csrf_middleware
