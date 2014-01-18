from __future__ import unicode_literals

import collections
import functools
import logging
import operator
import types
import sys

from django import http, test
from django.conf import settings
from django.core import exceptions, signals, urlresolvers
from django.test import client
from django.utils import encoding, six
from django.views import debug


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
        
        Adapted from django.core.handlers.base.BaseHandler.
        
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
        
        # Apply response middleware.
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
    A test client that uses the customized Client handler to directly test 
    a specified view with arguments and keyword arguments.
    
    """
    def __init__(self, enforce_csrf_checks=False, **defaults):
        super(Client, self).__init__(
            enforce_csrf_checks=enforce_csrf_checks, **defaults)
        self.handler = ClientHandler(enforce_csrf_checks)


class TestCase(test.TestCase):
    """
    Common utilities for testing auth decorated views.
    
    """
    client_class = Client
    
    def view(self, view_class, prefix, get=None, post=None, **attrs):
        
        if not get:
            def get(self, request, *args, **kwargs):
                return http.HttpResponse("OK")
        
        return type(
            b"Test{base:s}".format(base=view_class.__name__),
            (view_class,),
            dict(functools.reduce(
                operator.add, (
                    (("get", get if get else default_get),),
                    (("post", post) if post else ()),) +
                    tuple(
                        ("_".join(prefix, name), value) 
                        for name, value in six.iteritems(attrs)),
                ()))).as_view()
