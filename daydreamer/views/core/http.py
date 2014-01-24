from __future__ import unicode_literals

import collections

from . import base


__all__ = ("HttpMethodAllow", "HttpMethodDeny",)


class HttpMethodAllow(base.Allow):
    """
    Allow the request if the HTTP method name is allowed and implemented.
    
    """
    def http_method_allow_test(self):
        """
        A hook to control when HTTP methods are allowed.
        
        """
        return True
    
    def get_allow_handler(self):
        """
        Allow the request if the test passes, deferring
        to self.http_method_not_allowed.
        
        """
        return (
            self.http_method_allow_test() and
            getattr(self, self.request.method.lower(), None) or
            self.http_method_not_allowed)


class HttpMethodDeny(base.Deny):
    """
    Deny the request if the HTTP method name is not allowed or not implemented.
    
    """
    def get_http_method_names(self):
        """
        A hook to override the allowed HTTP method names.
        
        """
        return self.http_method_names
    
    def http_method_deny_test(self):
        """
        A hook to control when HTTP methods are denied.
        
        """
        method = self.request.method.lower()
        return (
            method in self.get_http_method_names() and
            isinstance(getattr(self, method, None), collections.Callable))
    
    def get_deny_handler(self):
        """
        Deny the request if the test fails, deferring to super().
        
        """
        return (
            not self.http_method_deny_test() and
            self.http_method_not_allowed or
            super(HttpMethodDeny, self).get_deny_handler())
