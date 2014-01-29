from __future__ import unicode_literals

import collections

from django.views.decorators import http

from .. import core


__all__ = ("RequireGET", "RequirePOST", "RequireSafe", "Condition",)


class RequireGET(core.http.HttpMethodDeny):
    """
    A view behavior that requires an HTTP GET request.
    
    """
    http_method_names = ("get",)


class RequirePOST(core.http.HttpMethodDeny):
    """
    A view behavior that requires an HTTP POST request.
    
    """
    http_method_names = ("post",)


class RequireSafe(core.http.HttpMethodDeny):
    """
    A view behavior that requires an HTTP GET or HEAD request.
    
    """
    http_method_names = ("get", "head",)


class Condition(core.http.HttpMethodAllow):
    """
    A view behavior that provides conditional retrieval or change
    notification during the allow phase of the dispatch.
    
    Define a condition_etag() method to compute the ETag for the requested
    resource and/or define a condition_last_modified() method to compute the
    last modified datetime for the requestd resource. Both methods should
    take the request, arguments and keyword arguments from the URL dispatcher,
    i.e. (self, request, *args, **kwargs). If neither method is defined,
    the behavior will be disabled.
    
    See the django.views.decorators.http.condition() view decorator
    for details.
    
    """
    condition_etag = None
    condition_last_modified = None
    
    def get_allow_handler(self):
        """
        If either of condition_etag or condition_last_modified is defined, wrap
        the base allow handler in the condition() decorator.
        
        """
        allow = super(Condition, self).get_allow_handler()
        if (isinstance(self.condition_etag, collections.Callable) or
            isinstance(self.condition_last_modified, collections.Callable)):
            allow = http.condition(
                etag_func=self.condition_etag,
                last_modified_func=self.condition_last_modified)(allow)
        return allow
