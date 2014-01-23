from __future__ import unicode_literals

import collections

from django.utils import six
from django.views.decorators import vary

from .. import core


__all__ = ("VaryOnHeaders", "VaryOnCookie",)


class VaryOnHeaders(core.http.HttpMethodAllow):
    """
    A view behavior that adds values to the response's Vary header during the
    allow phase of the dispatch.
    
    Specify the case-insensitive Vary header value or values to add to response
    in the vary_on_headers attribute. If none are specified, the behavior will
    be disabled.
    
    See the django.views.decorators.vary.vary_on_headers() view decorator
    for details.
    
    """
    vary_on_headers = None
    
    def get_vary_on_headers(self):
        """
        A hook to control the Vary headers.
        
        """
        return self.vary_on_headers
    
    def get_allow_handler(self):
        """
        If Vary headers are specified, wrap the base allow handler in the
        vary_on_headers() decorator.
        
        """
        # Noramlize the Vary header values.
        vary_on_headers = self.get_vary_on_headers()
        if isinstance(vary_on_headers, six.string_types):
            vary_on_headers = (vary_on_headers,)
        
        allow = super(VaryOnHeaders, self).get_allow_handler()
        if vary_on_headers:
            allow = vary.vary_on_headers(*vary_on_headers)(allow)
        return allow


class VaryOnCookie(core.http.HttpMethodAllow):
    """
    A view behavior that adds "Cookie" to the response's Vary header during the
    allow phase of the dispatch.
    
    Set the vary_on_cookie to a falsy value to disable the behavior.
    
    See the django.views.decorators.vary_on_cookie() view decorator
    for details.
    
    """
    vary_on_cookie = True
    
    def get_vary_on_cookie(self):
        """
        A hook to control whether to add "Cookie" to the Vary header.
        
        """
        return self.vary_on_cookie
    
    def get_allow_handler(self):
        """
        If specified, wrap the base allow handler in the
        vary_on_cookie() decorator.
        
        """
        vary_on_cookie = self.get_vary_on_cookie()
        allow = super(VaryOnCookie, self).get_allow_handler()
        if vary_on_cookie:
            allow = vary.vary_on_cookie(allow)
        return allow
