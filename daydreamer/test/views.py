from __future__ import unicode_literals

import collections
import logging
import types
import sys
import urlparse

from django import http
from django.conf import settings
from django.core import exceptions, signals, urlresolvers
from django.http import request
from django.test import client
from django.utils import encoding, six
from django.views import debug

from daydreamer.core import lang

from . import base


logger = logging.getLogger("django.request")


class ClientHandler(client.ClientHandler):
    """
    A customized test client handler that subverts the URL resolution system
    and directly runs a specified view with arguments and keyword arguments.
    
    """
    def get_response(self, request):
        """
        A simplified request processor that directly runs a view with arguments
        and keyword arguments specified in the request's META keys,
        "django.view", "django.view_args" and "django.view_kwargs".
        
        Adapted from django.core.handlers.base.BaseHandler. It would be nice if
        the base implementation provided some object-oriented hooks so this
        didn't require so much copy/paste.
        
        """
        # The URL resolver, used in exception handling.
        urlconf = settings.ROOT_URLCONF
        urlresolvers.set_urlconf(urlconf)
        resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
        
        # Try to generate a response.
        try:
            response = None
            
            # Get the view data from the request.
            view = request.META.get("django.view")
            view_args = request.META.get("django.view_args", ())
            view_kwargs = request.META.get("django.view_kwargs", {})
            
            # Apply request middleware.
            for middleware_method in self._request_middleware:
                response = middleware_method(request)
                if response:
                    break
            
            # Apply view middleware.
            if not response:
                for middleware_method in self._view_middleware:
                    response = middleware_method(
                        request, view, view_args, view_kwargs)
                    if response:
                        break
            
            # Apply the view.
            if not response:
                wrapped_view = self.make_view_atomic(view)
                try:
                    response = wrapped_view(request, *view_args, **view_kwargs)
                except Exception as exception:
                    # Apply exception middleware.
                    for middleware_method in self._exception_middleware:
                        response = middleware_method(request, exception)
                        if response:
                            break
                    # Re-raise?
                    if response is None:
                        raise
            
            # If we have no response by now, raise a ValueError.
            if not response:
                raise ValueError(
                    "The view {module:s}.{name:s} didn't return an "
                    "HttpResponse object.".format(
                        module=view.__module__,
                        name=view.__name__
                            if isinstance(view, types.FunctionType)
                            else view.__class__.__name__ + ".__call__"))
            
            # Apply template response middleware and render the response?
            if isinstance(
                getattr(response, "render", None), collections.Callable):
                for middleware_method in self._template_response_middleware:
                    response = middleware_method(request, response)
                response = response.render()
        
        except http.Http404 as exception:
            # Handle 404.
            logger.warning(
                "Not Found: {path:s}".format(path=request.path),
                extra={"status_code": 404, "request": request})
            if settings.DEBUG:
                response = debug.technical_404_response(request, exception)
            else:
                try:
                    callback, kwargs = resolver.resolve404()
                    response = callback(request, **kwargs)
                except:
                    signals.got_request_exception.send(
                        sender=self.__class__, request=request)
                    response = self.handle_uncaught_exception(
                        request, resolver, sys.exc_info())
        
        except exceptions.PermissionDenied:
            # Handle 403.
            logger.warning(
                "Forbidden (Permission denied): {path:s}".format(
                    path=request.path),
                extra={"status_code": 403, "request": request})
            try:
                callback, kwargs = resolver.resolve403()
                response = callback(request, **kwargs)
            except:
                signals.got_request_exception.send(
                    sender=self.__class__, request=request)
                response = self.handle_uncaught_exception(
                    request, resolver, sys.exc_info())
        
        except exceptions.SuspiciousOperation as exception:
            # Handle 400.
            security_logger = logging.getLogger(
                "django.security.{name:s}".format(
                    name=exception.__class__.__name__))
            security_logger.error(encoding.force_text(exception))
            try:
                callback, kwargs = resolver.resolve400()
                response = callback(request, **kwargs)
            except:
                signals.got_request_exception.send(
                    sender=self.__class__, request=request)
                response = self.handle_uncaught_exception(
                    request, resolver, sys.exc_info())
        
        except SystemExit:
            # Re-raise exit.
            raise
        
        except:
            # Handle anything else.
            signals.got_request_exception.send(
                sender=self.__class__, request=request)
            response = self.handle_uncaught_exception(
                request, resolver, sys.exc_info())
        
        # Apply response middleware and fixes.
        try:
            for middleware_method in self._response_middleware:
                response = middleware_method(request, response)
            response = self.apply_response_fixes(request, response)
        except:
            signals.got_request_exception.send(
                sender=self.__class__, request=request)
            response = self.handle_uncaught_exception(
                request, resolver, sys.exc_info())
        
        return response


class Client(client.Client):
    """
    A test client that uses the customized request handler to directly test 
    a specified view with arguments and keyword arguments.
    
    To avoid a bug encountered in implementation, all HTTP methods
    hardcode follow=True.
    
    """
    # Redirect status codes.
    redirect_status_codes = set((301, 302, 303, 307))
    
    def __init__(self, enforce_csrf_checks=False, **defaults):
        """
        Replace the default handler with the customized request handler.
        
        """
        super(Client, self).__init__(
            enforce_csrf_checks=enforce_csrf_checks, **defaults)
        self._client_handler = self.handler
        self.handler = ClientHandler(enforce_csrf_checks)
    
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
        self.handler = self._client_handler
        response = super(Client, self)._handle_redirects(response, **extra)
        self.get = get
        self.handler = handler
        return response


class TestCase(base.TestCase):
    """
    A test case for dynamically generating and testing class-based views.
    Uses a customized client and request handler to facilitate view testing
    without using the URL resolution framework.
    
    To turn on Django's CSRF framework during testing, set the class'
    enforce_csrf_checks attribute to True.
    
    """
    client_class = Client
    enforce_csrf_checks = False
    
    def unique_path(self):
        """
        Returns a unique path for use in testing class-based views.
        
        """
        return "/{unique:s}/".format(unique=self.unique())
    
    def _pre_setup(self):
        """
        Replaces the default test client, providing a hook to specify whether
        to use Django's CSRF framework during testing.
        
        """
        super(TestCase, self)._pre_setup()
        self.client = self.client_class(
            enforce_csrf_checks=self.enforce_csrf_checks)
    
    def view(self, view_class, attrs=None,
            get=None, post=None, head=None,
            put=None, patch=None, delete=None):
        """
        Generate a view from the given view class and attributes.
        
        The generated view will inherit from the view_class, so it should be
        a class that inherits from django.views.generic.base.View, or a class
        that is duck type equivalent.
        
        The attrs argument should be a dictionary of values that will be
        added to the class at creation time.
        
        If get is truthy and a get() method is not provided by either
        the view_class or the attrs, a simple get() method that
        returns an HttpResponse with the content in the get argument will be
        automatically added to the class. If False, it is the caller's
        responsibility to provide any required HTTP method handlers.
        
        The other HTTP method name argumnts operate similarly to get, except
        that the head() method hardcodes the empty string for the response's
        content. An ensure_options argument is not provided, as an options()
        method is provided by the django.views.generic.base.View base class.
        
        """
        # Normalize the attributes.
        attrs = attrs or {}
        
        # Add a get() method?
        if (get and 
            not hasattr(view_class, "get") and
            "get" not in attrs):
            def _get(self, request, *args, **kwargs):
                return http.HttpResponse(get)
            attrs["get"] = _get
        
        # Add a post() method?
        if (post and
            not hasattr(view_class, "post") and
            "post" not in attrs):
            def _post(self, request, *args, **kwargs):
                return http.HttpResopnse(post)
            attrs["post"] = _post
        
        # Add a head() method?
        if (head and
            not hasattr(view_class, "head") and
            "head" not in attrs):
            def _head(self, request, *args, **kwargs):
                return http.HttpResopnse("")
            attrs["head"] = _head
        
        # Add a put() method?
        if (put and
            not hasattr(view_class, "put") and
            "put" not in attrs):
            def _put(self, request, *args, **kwargs):
                return http.HttpResopnse(put)
            attrs["put"] = _put
        
        # Add a patch() method?
        if (patch and
            not hasattr(view_class, "patch") and
            "patch" not in attrs):
            def _patch(self, request, *args, **kwargs):
                return http.HttpResopnse(patch)
            attrs["patch"] = _patch
        
        # Add a delete() method?
        if (delete and
            not hasattr(view_class, "delete") and
            "delete" not in attrs):
            def _delete(self, request, *args, **kwargs):
                return http.HttpResopnse(delete)
            attrs["delete"] = _delete
        
        # Create the view.
        return type(
            b"Test{base:s}".format(base=view_class.__name__),
            (view_class,),
            attrs).as_view()
