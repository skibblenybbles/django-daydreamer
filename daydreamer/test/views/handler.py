from __future__ import unicode_literals

from .. import handler


class ClientHandler(handler.ClientHandler):
    """
    A customized test client handler that skips over the URL resolution system
    and runs a view specified in the request's META data under the keys
    "django.view", "django.view_args" and "django.view_kwargs".
    
    """
    def get_resolver_match(self, request, resolver):
        """
        Resolves the view from META data set on the request. Returns a
        triple containing the view, its args and its kwargs.
        
        """
        return (
            request.META.get("django.view"),
            request.META.get("django.view_args", ()),
            request.META.get("django.view_kwargs", {}),)
