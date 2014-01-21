from __future__ import unicode_literals

import collections

from django.views.decorators import http

from .. import generic


__all__ = ("RequireGET", "RequirePOST", "RequireSafe", "Condition",)


class RequireGET(generic.View):
    """
    A view decorator mixin that requires an HTTP GET request.
    
    """
    http_method_names = ("get",)


class RequirePOST(generic.View):
    """
    A view decorator mixin that requires an HTTP POST request.
    
    """
    http_method_names = ("post",)


class RequireSafe(generic.View):
    """
    A view decorator mixin that requires an HTTP GET or HEAD request.
    
    """
    http_method_names = ("get", "head",)


class Condition(generic.View):
    """
    A view decorator mixin that provides conditional retrieval or change
    notification for requests.
    
    Define a condition_etag() method to compute the ETag for the requested
    resource and/or define a condition_last_modified() method to compute the
    last modified datetime for the requestd resource. If neither is defined,
    the decorator will be disabled.
    
    See the django.views.decorators.http.condition() view decorator
    for details.
    
    """
    condition_etag = None
    condition_last_modified = None
    
    def dispatch(self, request, *args, **kwargs):
        """
        Wrap the base dispatch in the condition() decorator.
        
        """
        dispatch = super(Condition, self).dispatch
        if (isinstance(self.condition_etag, collections.Callable) or
            isinstance(self.condition_last_modified, collections.Callable)):
            dispatch = http.condition(
                etag_func=self.condition_etag,
                last_modified_func=self.condition_last_modified)(dispatch)
        return dispatch(request, *args, **kwargs)
