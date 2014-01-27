from __future__ import unicode_literals

from django.conf import settings
from django.middleware import csrf

from daydreamer.test.views import client


class Client(client.Client):
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
