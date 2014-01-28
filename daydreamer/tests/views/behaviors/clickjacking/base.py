from __future__ import unicode_literals

from django.conf import settings

from daydreamer.tests.views import generic


class TestCase(generic.TestCase):
    """
    Common utilities for testing clickjacking view behaviors.
    
    Clickjacking middleware is disabled by default with the
    clickjacking_middleware_enabled attribute.
    
    """
    clickjacking_middleware_enabled = False
    
    def setUp(self):
        if not self.clickjacking_middleware_enabled:
            self._clickjacking_middleware = settings.MIDDLEWARE_CLASSES
            settings.MIDDLEWARE_CLASSES = tuple(
                middleware for middleware in settings.MIDDLEWARE_CLASSES
                if middleware !=
                    "django.middleware.clickjacking.XFrameOptionsMiddleware")
        super(TestCase, self).setUp()
    
    def tearDown(self):
        super(TestCase, self).tearDown()
        if not self.clickjacking_middleware_enabled:
            settings.MIDDLEWARE_CLASSES = self._clickjacking_middleware
            del self._clickjacking_middleware
