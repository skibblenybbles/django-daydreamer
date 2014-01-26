from __future__ import unicode_literals

import collections
import logging
import sys

from django import http
from django.conf import settings
from django.core import exceptions, signals, urlresolvers
from django.core.handlers import base
from django.utils import encoding, six
from django.views import debug

from daydreamer.core import lang


__all__ = ("Handler",)


logger = logging.getLogger("django.request")


class Handler(base.BaseHandler):
    """
    Provides a refactored get_response() method with a finer grain of control
    over response generation through object-oriented hooks.
    
    """
    def get_resolver(self, request):
        """
        Returns a django.core.urlresolvers.RegexURLResolver for the request's
        urlconf, falling back to the global urlconf fom settings.
        
        """
        urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
        urlresolvers.set_urlconf(urlconf)
        return urlresolvers.RegexURLResolver(r'^/', urlconf)
    
    def get_resolver_match(self, request, resolver):
        """
        Resolves the view using the request and the URL resolver. Returns a
        triple containing the view, its args and its kwargs.
        
        """
        return resolver.resolve(request.path_info)
    
    def resolve_view(self, request, resolver):
        """
        If missing, caches the result of get_resolver_match() on the request.
        Returns the resolver match data. See get_resolver_match() for details.
        
        """
        if (not hasattr(request, "resolver_match") or
            request.resolver_match is None):
            request.resolver_match = self.get_resolver_match(request, resolver)
        return request.resolver_match
    
    def apply_request_middleware(self, request, resolver):
        """
        Apply request middleware in order, returning the first encountered
        response, falling back to None.
        
        """
        return lang.any((
                method(request)
                for method in self._request_middleware),
            None)
    
    def apply_view_middleware(self, request, resolver):
        """
        Resolve the view and apply view middleware in order, returning
        the first encountered response, falling back to None.
        
        """
        match = self.resolve_view(request, resolver)
        return lang.any((
                method(request, *match)
                for method in self._view_middleware),
            None)
    
    def apply_exception_middleware(self, request, resolver, exception):
        """
        Apply exception middleware in order, returning the first encountered
        response, falling back to None.
        
        """
        return lang.any((
                method(request, exception)
                for method in self._exception_middleware),
            None)
    
    def apply_view(self, request, resolver):
        """
        Resolve the view, make it atomic and apply it. If an exception occurs,
        apply the exception middleware.
        
        """
        view, view_args, view_kwargs = self.resolve_view(request, resolver)
        try:
            return self.make_view_atomic(view)(
                request, *view_args, **view_kwargs)
        except Exception as exception:
            return (
                self.apply_exception_middleware(
                    request, resolver, exception) or
                six.reraise(*sys.exc_info()))
    
    def validate_response(self, request, resolver, response):
        """
        If the response is falsy, raise a ValueError complaining about the view
        not returning a response.
        
        """
        if not response:
            view, = self.resolve_view(request, resolver)[:1]
            raise ValueError(
                "The view {module:s}.{name:s} didn't return an "
                "HttpResponse object.".format(
                    module=view.__module__,
                    name=view.__name__
                        if isinstance(view, types.FunctionType)
                        else view.__class__.__name__ + ".__call__"))
        return response
    
    def apply_template_response_middleware(self, request, resolver, response):
        """
        If the response has a render() method, transform the response by
        applying template response middleware in order, finally rendering
        the response.
        
        """
        if isinstance(getattr(response, "render", None), collections.Callable):
            for method in self._template_response_middleware:
                response = method(request, response)
            response = response.render()
        return response
    
    def apply_response_middleware(self, request, resolver, response):
        """
        Transform the response by applying reponse middleware in order.
        
        """
        for method in self._response_middleware:
            response = method(request, response)
        return response
    
    def apply_response_fixes(self, request, resolver, response):
        """
        Apply response fixes.
        
        Calls the base implementation. This hook is provided so that
        consistent arguments are passed to the various apply_* methods.
        
        """
        return super(Handler, self).apply_response_fixes(request, response)
    
    def handle_not_found(self, request, resolver, exception):
        """
        Logs a 404 warning and invokes either the debug handler or the
        resolver's 404 handler.
        
        """
        logger.warning(
            "Not Found: {path:s}".format(path=request.path),
            extra={"status_code": 404, "request": request})
        if settings.DEBUG:
            return debug.technical_404_response(request, exception)
        callback, kwargs = resolver.resolve404()
        return callback(request, **kwargs)
    
    def handle_permission_denied(self, request, resolver, exception):
        """
        Logs a 403 warning and invokes the resolver's 403 handler.
        
        """
        logger.warning(
            "Forbidden (Permission denied): {path:s}".format(
                path=request.path),
            extra={"status_code": 403, "request": request})
        callback, kwargs = resolver.resolve403()
        return callback(request, **kwargs)
    
    def handle_suspicious_operation(self, request, resolver, exception):
        """
        Logs a 400 security error and invokes the resolver's 400 handler.
        
        """
        logging.getLogger(
            ".".join(
                ("django.security",
                exception.__class__.__name__,))).error(
                    encoding.force_text(exception))
        callback, kwargs = resolver.resolve400()
        return callback(request, **kwargs)
    
    def handle_uncaught_exception(self, request, resolver, exc_info):
        """
        Signals the uncaught exception and invokes the
        super()'s implementation.
        
        """
        signals.got_request_exception.send(
            sender=self.__class__, request=request)
        return super(Handler, self).handle_uncaught_exception(
            request, resolver, exc_info)
    
    def view_response(self, request, resolver):
        """
        Generates an initial response from either the request middleware,
        the view middleware or the view, in that order.
        
        """
        return (
            self.apply_request_middleware(request, resolver) or
            self.apply_view_middleware(request, resolver) or
            self.apply_view(request, resolver))
    
    def render_response(self, request, resolver):
        """
        Validates the view response and applies the template response
        middleware, which finishes rendering of the response.
        
        """
        return self.apply_template_response_middleware(
            request, resolver, self.validate_response(
                request, resolver, self.view_response(
                    request, resolver)))
    
    def generate_response(self, request, resolver):
        """
        Renders an initial response, falling back to exception handler
        responses for particular exceptions.
        
        Subclasses wishing to handle more exception types should override this
        method to catch any additional exceptions raised by super().
        
        """
        try:
            return self.render_response(request, resolver)
        except http.Http404 as exception:
            return self.handle_not_found(
                request, resolver, exception)
        except exceptions.PermissionDenied as exception:
            return self.handle_permission_denied(
                request, resolver, exception)
        except exceptions.SuspiciousOperation as exception:
            return self.handle_suspicious_operation(
                request, resolver, exception)
    
    def process_response(self, request, resolver, response):
        """
        Processes the response with response middleware and response fixes,
        returning the finalized response.
        
        """
        return self.apply_response_fixes(
            request, resolver, self.apply_response_middleware(
                request, resolver, response))
    
    def get_response(self, request):
        """
        Overrides the base implementation with object-oriented hooks.
        
        Adapted from django.core.handlers.base.BaseHandler.
        
        """
        resolver = self.get_resolver(request)
        try:
            return self.process_response(
                request, resolver, self.generate_response(
                    request, resolver))
        except SystemExit:
            six.reraise(*sys.exc_info())
        except:
            return self.handle_uncaught_exception(
                request, resolver, sys.exc_info())
