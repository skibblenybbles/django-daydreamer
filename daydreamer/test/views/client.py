from __future__ import unicode_literals

from django.http import request
from django.test import client

from daydreamer.core import lang

from . import handler


class Client(client.Client):
    """
    A test client that uses a customized request handler to directly test 
    a specified view with arguments and keyword arguments.
    
    To avoid a bug encountered during implementation, all HTTP methods
    hardcode follow=True.
    
    """
    def __init__(self, enforce_csrf_checks=False, **defaults):
        """
        Replace the default handler with the customized request handler.
        
        """
        super(Client, self).__init__(
            enforce_csrf_checks=enforce_csrf_checks, **defaults)
        self._base_handler = self.handler
        self.handler = handler.ClientHandler(enforce_csrf_checks)
    
    def _view_request(self, view, view_args, view_kwargs):
        return {
            "django.view": view,
            "django.view_args": view_args or (),
            "django.view_kwargs": view_kwargs or {}}
    
    def get(self, view, view_args=None, view_kwargs=None, path="/", data={},
            **extra):
        """
        Runs the given view with a GET request.
        
        """
        extra.pop("follow", None)
        return super(Client, self).get(path, data=data, follow=True,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def post(self, view, view_args=None, view_kwargs=None, path="/", data={},
            content_type=client.MULTIPART_CONTENT, **extra):
        """
        Runs the given view with a POST request.
        
        """
        extra.pop("follow", None)
        return super(Client, self).post(path, data=data,
            content_type=content_type, follow=True,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def head(self, view, view_args=None, view_kwargs=None, path="/", data={},
            **extra):
        """
        Runs the given view with a HEAD request.
        
        """
        extra.pop("follow", None)
        return super(Client, self).head(path, data=data, follow=True,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def options(self, view, view_args=None, view_kwargs=None, path="/", data="",
            content_type="application/octet-stream", **extra):
        """
        Runs the given view with an OPTIONS request.
        
        """
        extra.pop("follow", None)
        return super(Client, self).options(path, data=data,
            content_type=content_type, follow=True,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def put(self, view, view_args=None, view_kwargs=None, path="/", data="",
            content_type="application/octet-stream", **extra):
        """
        Runs the given view with a PUT request.
        
        """
        extra.pop("follow", None)
        return super(Client, self).put(path, data=data,
            content_type=content_type, follow=True,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def patch(self, view, view_args=None, view_kwargs=None, path="/", data="",
            content_type="application/octet-stream", **extra):
        """
        Runs the given view with a PATCH request.
        
        """
        extra.pop("follow", None)
        return super(Client, self).patch(path, data=data,
            content_type=content_type, follow=True,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def delete(self, view, view_args=None, view_kwargs=None, path="/", data="",
            content_type="application/octet-stream", **extra):
        """
        Runs the given view with a DELETE request.
        
        """
        extra.pop("follow", None)
        return super(Client, self).delete(path, data=data,
            content_type=content_type, follow=True,
            **lang.updated(
                extra, self._view_request(view, view_args, view_kwargs)))
    
    def _handle_redirects(self, response, **extra):
        """
        Patches redirect handling to ensure that the base class' get() method
        and the original request handler are used.
        
        """
        get = self.get
        self.get = super(Client, self).get
        handler = self.handler
        self.handler = self._base_handler
        response = super(Client, self)._handle_redirects(response, **extra)
        self.get = get
        self.handler = handler
        return response
