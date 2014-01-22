from __future__ import unicode_literals

import logging

from django import http
from django.core import exceptions
from django.views import generic

from daydreamer.core import lang, urlresolvers


__all__ = ("Core", "Null", "Allow", "Deny",)


class Core(generic.View):
    """
    Provides helpful features for generating common responses and
    reversing URLs.
    
    URL reversing is handled by daydreamer.core.urlresolvers.reverse().
    Because the request is available, it is easy to reverse fully-qualified
    URLs with the request's host domain and scheme. Simply pass qualified=True
    to self.reverse().
    
    Included responses are file attachments, redirects (301 and 302) and
    gone (410). Helpers that raise appropriate exceptions for not found (404),
    permission denied (403) and suspicious operation (400) are also provided.
    The not modified (304), method not allowed (405) and server error (500)
    responses are not provided, as they are handled automatically by other
    Django mechanisms.
    
    Even though the not_found(), permission_denied() and suspicious_operation()
    methods raise exceptions, it is recommended to return the responses from
    these calls for stylistic consistency, e.g.:
    
        # Do this:
        if resource.not_available():
            return self.not_found()
        
        # Not this:
        if resource.not_available():
            self.not_found()
    
    Since these methods raise exceptions, rather than return responses, take
    care to avoid catching their exceptions, or Django's special response
    exception handling machinery will be neutralized.
    
    """
    # The request logger.
    logger = logging.getLogger("django.request")
    
    # URL reversing.
    def reverse(self, viewname, qualified=False, scheme=None, **kwargs):
        """
        Reverse a URL from the given viewname and other optional arguments to
        django.contrib.urlresolvers.reverse(). If qualified is True, the result
        will include the URL scheme and host. If the scheme is also specified,
        it will take precedence over the current request's scheme.
        
        """
        return urlresolvers.reverse(viewname, **lang.updated(kwargs, (
            {"qualified": True, "scheme": scheme, "request": self.request}
                if qualified
                else {}),
            copy=True))
    
    # Responses.
    def attachment(self, data, content_type, filename):
        """
        Returns a file attachment response with the data as its payload
        and the specified content type (MIME type) and filename.
        
        """
        return lang.updated(
            http.HttpResponse(data, content_type=content_type), {
                "Content-Disposition":
                    "attachment; filename=\"{filename:s}\"".format(
                        filename=filename)})
    
    def redirect(self, viewname, permanent=False, **kwargs):
        """
        Returns a 301 or 302 redirect response with the reversed URL from the
        given viewname and other optional arguments to View.reverse().
        If permanent is True, the redirect will be a permanent 301 redirect.
        Otherwise, it will be a temporary 302 redirect.
        
        """
        return (
            http.HttpResponsePermanentRedirect
                if permanent
                else http.HttpResponseRedirect)(
                    self.reverse(viewname, **kwargs))
    
    def gone(self, debug_message=""):
        """
        Logs and returns a 410 gone response.
        
        """
        self.logger.info(
            "Gone ({method:s}: {path:s})".format(
                method=self.request.method, path=self.request.path),
            extra={"status_code": 410, "request": self.request})
        return http.HttpResponseGone(debug_message)
    
    def not_found(self, debug_message=""):
        """
        Raises an Http404 exception to trigger the 404 not found response
        machinery. Even though this raises an exception, it is recommended
        to return it for stylistic consistency:
        
            return self.not_found()
        
        """
        raise http.Http404(debug_message)
    
    def permission_denied(self, debug_message=""):
        """
        Raises a PermissionDenied exception to trigger the 403 forbidden
        response machinery. Even though this raises an exception, it is
        recommended to return it for stylistic consistency:
        
            return self.permission_denied()
        
        """
        raise exceptions.PermissionDenied(debug_message)
    
    def suspicious_operation(self, debug_message=""):
        """
        Raises a SuspiciousOperation exception to trigger the 400 bad request
        response machinery. Even though this raises an exception, it is
        recommended to return it for stylistic consistency:
        
            return self.suspicious_operation()
        
        """
        raise exceptions.SuspiciousOperation(debug_message)


class Null(Core):
    """
    The null view. Dispatches directly to the HTTP method denied handler.
    
    """
    def dispatch(self, request, *args, **kwargs):
        """
        The buck stops here. The request's method is denied.
        
        """
        return self.http_method_not_allowed(request, *args, **kwargs)


class Allow(Null):
    """
    The allow view. Selects a handler to allow the request or defers
    to super().
    
    """
    def get_allow_handler(self):
        """
        Either return a handler to allow the request or defer to super().
        
        """
        return None
    
    def dispatch(self, request, *args, **kwargs):
        """
        Call the allow handler or defer to super().
        
        """
        return (
            self.get_allow_handler() or
            super(Allow, self).dispatch)(
                request, *args, **kwargs)


class Deny(Null):
    """
    The denial view. Selects a handler to deny the request or defers
    to super().
    
    """
    def get_deny_handler(self):
        """
        Either return a handler to deny the request or defer to super().
        
        """
        return None
    
    def dispatch(self, request, *args, **kwargs):
        """
        Call the deny handler or defer to super().
        
        """
        return (
            self.get_deny_handler() or 
            super(Deny, self).dispatch)(
                request, *args, **kwargs)
