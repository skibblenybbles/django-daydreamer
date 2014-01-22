from __future__ import unicode_literals

from django.conf import settings
from django.middleware import csrf

from daydreamer.test import views as test_views
from daydreamer.tests.views import core


class Client(test_views.Client):
    """
    A specialized test client that can set a CSRF cookie.
    
    """
    def set_csrf_cookie(self):
        """
        Sets a unique CSRF cookie for subsequent requests to use. Returns
        the new cookie's value.
        
        """
        self.cookies[settings.CSRF_COOKIE_NAME] = csrf._get_new_csrf_key()
        self.cookies[settings.CSRF_COOKIE_NAME].update({
            "max_age": 60 * 60 * 24 * 7 * 52,
            "domain": settings.CSRF_COOKIE_DOMAIN,
            "path": settings.CSRF_COOKIE_PATH,
            "secure": settings.CSRF_COOKIE_SECURE,
            "httponly": settings.CSRF_COOKIE_HTTPONLY})
        return self.cookies.get(settings.CSRF_COOKIE_NAME).value
    
    def get_csrf_cookie(self, set_missing=True):
        """
        Returns the current CSRF cookie value. If set_missing is True,
        sets and returns the CSRF cookie value when it's missing.
        
        """
        cookie = self.cookies.get(settings.CSRF_COOKIE_NAME)
        if cookie:
            return cookie.value
        elif set_missing:
            return self.set_csrf_cookie()
        return None


class TestCase(core.TestCase):
    """
    Common utilities for testing CSRF view behaviors.
    
    CSRF middleware is disabled by default with the
    csrf_middleware_enabled attribute. CSRF processing during tests is
    enabled by default, and a specialized client for managing CSRF
    cookies is provided.
    
    """
    client_class = Client
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
