from django.core.handlers import wsgi

from . import base


class WSGIHandler(wsgi.WSGIHandler, base.Handler):
    """
    A WSGI handler, enhanced with object-oriented hooks for response generation
    from daydreamer.core.handlers.base.Handler.
    
    """
    pass
