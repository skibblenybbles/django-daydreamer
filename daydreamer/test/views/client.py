from __future__ import unicode_literals

import weakref

from daydreamer.core import lang

from .. import client
from . import handler


class ClientBaseImplementation(object):
    """
    A context manager that defers to the Client instance's base handler
    and methods.
    
    """
    deferred_methods = (
        "get", "post", "head", "options", "put", "patch", "delete",)
    
    def __init__(self, client, base_handler):
        self.client = weakref.ref(client)
        self.base_handler = base_handler
        self.handler = client.handler
        
        for method in self.deferred_methods:
            setattr(self, method, getattr(client, method))
    
    def __enter__(self):
        client = self.client()
        if client:
            client.handler = self.base_handler
            for method in self.deferred_methods:
                setattr(client, method, getattr(super(Client, client), method))
        return client
    
    def __exit__(self, exc_type, exc_value, traceback):
        client = self.client()
        if client:
            client.handler = self.handler
            for method in self.deferred_methods:
                setattr(client, method, getattr(self, method))


class Client(client.Client):
    """
    A test client that uses a customized request handler to directly test 
    a specified view with arguments and keyword arguments.
    
    """
    def __init__(self, enforce_csrf_checks=False, **defaults):
        """
        Replace the default handler with the customized request handler
        and set up a context manager for deffering to the base's handler
        and methods when desired.
        
        """
        super(Client, self).__init__(
            enforce_csrf_checks=enforce_csrf_checks, **defaults)
        
        # Replace the handler and set up the context manager.
        base_handler = self.handler
        self.handler = handler.ClientHandler(enforce_csrf_checks)
        self.base_implementation = ClientBaseImplementation(self, base_handler)
    
    def _view_request(self, view, view_args, view_kwargs):
        return {
            "django.view": view,
            "django.view_args": view_args or (),
            "django.view_kwargs": view_kwargs or {}}
    
    def get(self, view, view_args=None, view_kwargs=None, path="/", data={},
            follow=False, **extra):
        """
        Runs the given view with a GET request.
        
        """
        extra.pop("follow", None)
        return super(Client, self).get(path, data=data, follow=follow,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def post(self, view, view_args=None, view_kwargs=None, path="/", data={},
            content_type=client.MULTIPART_CONTENT, follow=False, **extra):
        """
        Runs the given view with a POST request.
        
        """
        return super(Client, self).post(path, data=data,
            content_type=content_type, follow=follow,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def head(self, view, view_args=None, view_kwargs=None, path="/", data={},
            follow=False, **extra):
        """
        Runs the given view with a HEAD request.
        
        """
        return super(Client, self).head(path, data=data, follow=follow,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def options(self, view, view_args=None, view_kwargs=None, path="/", data="",
            content_type="application/octet-stream", follow=False, **extra):
        """
        Runs the given view with an OPTIONS request.
        
        """
        return super(Client, self).options(path, data=data,
            content_type=content_type, follow=follow,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def put(self, view, view_args=None, view_kwargs=None, path="/", data="",
            content_type="application/octet-stream", follow=False, **extra):
        """
        Runs the given view with a PUT request.
        
        """
        return super(Client, self).put(path, data=data,
            content_type=content_type, follow=follow,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def patch(self, view, view_args=None, view_kwargs=None, path="/", data="",
            content_type="application/octet-stream", follow=False, **extra):
        """
        Runs the given view with a PATCH request.
        
        """
        extra.pop("follow", None)
        return super(Client, self).patch(path, data=data,
            content_type=content_type, follow=follow,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def delete(self, view, view_args=None, view_kwargs=None, path="/", data="",
            content_type="application/octet-stream", follow=False, **extra):
        """
        Runs the given view with a DELETE request.
        
        """
        return super(Client, self).delete(path, data=data,
            content_type=content_type, follow=follow,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def _handle_redirects(self, *args, **kwargs):
        """
        Patches redirect handling to ensure that the base class' get() method
        and the original request handler are used.
        
        """
        with self.base_implementation:
            return super(Client, self)._handle_redirects(*args, **kwargs)
