from __future__ import unicode_literals

import collections
import logging

from django import http
from django.conf import settings
from django.contrib import messages
from django.core import exceptions
from django.views import generic

from daydreamer.core import lang, urlresolvers


__all__ = ("View", "TemplateView", "RedirectView",)


class SecuredView(generic.View):
    """
    A view decorator mixin with hooks to make security checks for the request.
    Provides the not_allowed() method, which when called:
    
        * If exceptions are enabled, raises the configured exception.
        * If a failure message has been specified, enqueues a messages with the
          django.contrib.messages framework.
        * Finally, redirects to a failure URL with an optional query string
          specifying the next URL, i.e. to redirect back when desired.
    
    This encapsulates common view patterns and makes them configurable
    through a declarative API, facilitating the implementation of many
    view mixins and helping you avoid repetition of boilerplate code. The
    view mixins in daydreamer.views.decorated make heavy use of these
    features and can simplify your view implementations.
    
    The not_allowed() method should be called with a prefix name that it
    will use to retrieve attributes that customize its behavior as follows:
        
        When the <prefix>_raise attribute is set to a truthy value, raises
        <prefix>_exception.
        
        Set the <prefix>_exception attribute to an exception class or
        instance to raise. Defaults to django.core.exceptions.PermissionDenied
        when falsy.
        
        Set the <prefix>_message attribute to a message to enqueue via the
        django.contrib.messages framework. If falsy, no message will
        be enqueued.
        
        Set the <prefix>_message_level attribute to the level of the failure
        message, a value from django.contrib.messages.constants. Defaults to
        WARNING when falsy.
        
        Set the <prefix>_message_tags attribute to a space-separated string
        specifying additional tags to add to the message, typically used for
        CSS styling purposes. Defaults to the empty string when falsy.
        
        Set the <prefix>_redirect_url attribute to the failure redirect URL.
        Defaults to settings.LOGIN_URL when falsy. The URL must be a string or
        a lazy string, such as the result of
        django.core.urlresovlers.reverse_lazy(). However, settings.LOGIN_URL
        may be a named URL pattern, as documented for Django's settings.
        
        Set the <prefix>_redirect_next_url attribute to the URL of the value
        for the query string parameter to append to the redirect URL. Defaults
        to the request's fully-qualified URL when falsy.
        
        Set the <prefix>_redirect_next_name attribute to the name of the
        query string parameter to append to the redirect URL for the value
        of the next URL. If None, no query string parameter will be added to
        the redirect URL. A typical value would be
        django.contrib.auth.REDIRECT_FIELD_NAME.
        
    Additional object oriented hooks are provided by the implementation. See
    the source code for details.
    
    """
    # Hooks for resolving attribute values used by not_allowed().
    def get_not_allowed_attr(self, prefix, attr):
        """
        A hook to customize the way that attributes for the not_allowed()
        method are retrieved form a prefix and attribute name.
        
        The default implementation joins the prefix and attribute name with
        "_" and looks up the attribute with getattr. This will raise an
        AttributeError if the generated attribute name does not exist.
        
        """
        return getattr(self, "_".join((prefix, attr)))
    
    def get_not_allowed_raise(self, prefix):
        """
        A hook to customize resolution of the exception raising setting
        used by not_allowed().
        
        The default implementation returns self.<prefix>_raise.
        
        """
        return self.get_not_allowed_attr(prefix, "raise")
    
    def get_not_allowed_exception(self, prefix):
        """
        A hook to customize resolution of the exception value to raise
        used by not_allowed().
        
        The default implementation returns self.<prefix>_exception,
        defaulting to django.core.exceptions.PermissionDenied when falsy.
        
        """
        return (
            self.get_not_allowed_attr(prefix, "exception") or
            exceptions.PermissionDenied)
    
    def get_not_allowed_message(self, prefix):
        """
        A hook to customize resolution of the message value to enqueue,
        used by not_allowed().
        
        The default implementation returns self.<prefix>_message.
        
        """
        return self.get_not_allowed_attr(prefix, "message")
    
    def get_not_allowed_message_level(self, prefix):
        """
        A hook to customize resolution of the message level used
        by not_allowed().
        
        The default implementation returns self.<prefix>_message_level,
        defaulting to django.contrib.messages.WARNING when falsy.
        
        """
        return (
            self.get_not_allowed_attr(prefix, "message_level") or
            messages.WARNING)
            
    def get_not_allowed_message_tags(self, prefix):
        """
        A hook to customize resolution of the message tags used
        by not_allowed().
        
        The default implementation returns self.<prefix>_message_tags,
        defaulting to the empty string when falsy.
        
        """
        return (
            self.get_not_allowed_attr(prefix, "message_tags") or
            "")
    
    def get_not_allowed_redirect_url(self, prefix):
        """
        A hook to customize resolution of the redirect URL used
        by not_allowed().
        
        The default implementation returns self.<prefix>_redirect_url,
        defaulting to the resolved value for settings.LOGIN_URL when falsy.
        
        """
        redirect_url = self.get_not_allowed_attr(prefix, "redirect_url")
        try:
            redirect_url = (
                redirect_url or urlresolvers.reverse(settings.LOGIN_URL))
        except urlresolvers.NoReverseMatch:
            redirect_url = settings.LOGIN_URL
        return redirect_url
    
    def get_not_allowed_redirect_next_url(self, prefix):
        """
        A hook to customize resolution of the redirect's next URL used
        by not_allowed().
        
        The default implementation returns self.<prefix>_redirect_next_url,
        defaulting to the request's fully-qualified URL when falsy.
        
        """
        return (
            self.get_not_allowed_attr(prefix, "redirect_next_url") or
            self.request.build_absolute_uri())
    
    def get_not_allowed_redirect_next_name(self, prefix):
        """
        A hook to customize resolution of the redirect next URL query parameter
        name used by not_allowed().
        
        The default implementation returns self.<prefix>_redirect_next_name.
        
        """
        return self.get_not_allowed_attr(prefix, "redirect_next_name")
    
    def get_not_allowed_full_redirect_url(self, prefix):
        """
        A hook to customize building of the full redirect URL used
        by not_allowed().
        
        The default implementation updates the query string for
        self.get_not_allowed_redirect_url() to include a parameter named
        self.get_not_allowed_redirect_next_name() with a value of
        self.get_not_allowed_redirect_next_url(). The query string is updated
        only when the parameter name is truthy. Simplifies the query string
        value with respect to the redirect URL and request.
        
        """
        redirect_url = self.get_not_allowed_redirect_url(prefix)
        next_name = self.get_not_allowed_redirect_next_name(prefix)
        if next_name:
            return urlresolvers.update_query(
                redirect_url, {
                    next_name: urlresolvers.simplify_redirect(
                        self.get_not_allowed_redirect_next_url(prefix),
                        redirect_url,
                        request=self.request)})
        return redirect_url
    
    # The handler to call upon test failure and hooks to modify it.
    def not_allowed(self, prefix):
        """
        The handler that should be called upon access test failure with
        the prefix name for the behavior-controlling attributes.
        
        The default implementation optionally attempts to raise an exception
        with not_allowed_raise_exception(). Then, it optionally enqueues a
        message with not_allowed_enqueue_message(). Finally, it returns a
        redirect response which may include an optional next URL query string
        value with not_allowed_respond().
        
        """
        self.not_allowed_raise_exception(prefix)
        self.not_allowed_enqueue_message(prefix)
        return self.not_allowed_respond(prefix)
    
    def not_allowed_raise_exception(self, prefix):
        """
        A hook to customize raising of an exception in not_allowed().
        
        In the default implementation, when self.get_not_allowed_raise() is
        truthy, raises self.get_not_allowed_exception().
        
        """
        if self.get_not_allowed_raise(prefix):
            raise self.get_not_allowed_exception(prefix)
    
    def not_allowed_enqueue_message(self, prefix):
        """
        A hook to customize message enqueuing in not_allowed().
        
        The default implementation enqueues self.get_not_allowed_messge() using
        the other self.get_not_allowed_message_*() settings when the message
        is truthy.
        
        """
        message = self.get_not_allowed_message(prefix)
        if message:
            messages.add_message(
                self.request,
                self.get_not_allowed_message_level(prefix),
                message,
                extra_tags=self.get_not_allowed_message_tags(prefix))
    
    def not_allowed_respond(self, prefix):
        """
        A hook to customize the response upon in not_allowed().
        
        The default implementation resolves the redirect URL with
        self.get_not_allowed_full_redirect_url() and returns the
        resolved URL in a redirect response.
        
        """
        return http.HttpResponseRedirect(
            self.get_not_allowed_full_redirect_url(prefix))
    
    # The dispatch system.
    def get_not_allowed_handler(self):
        """
        Returns a handler method when the request should not be allowed
        or None otherwise. Subclasses should always return a handler
        or the super()'s handler, e.g.:
        
            def get_not_allowed_handler(self):
                return (
                    not self.some_test() and
                    self.some_test_not_allowed or
                    super(SomeTest, self).get_not_allowed_handler())
        
        Chaining this way provides a way to select amongst alternative
        handler implementations while performing security checks in method
        resolution order.
        
        The returned handler should be a method that takes a request along
        with a variable number of arguments and keyword arguments, i.e.
        (request, *args, **kwargs). It may also take a request with specific
        arguments and keyword arguments that correspond to the view's
        URL pattern.
        
        """
        return None
    
    def get_allowed_handler(self):
        """
        Returns a handler method that will be used when the request is allowed
        or None otherwise. Subclasses should generally return a handler or the
        super()'s handler, e.g.:
        
            def get_allowed_handler(self):
                return (
                    self.some_test() and
                    self.some_test_allowed or
                    super(SomeTest, self).get_allowed_handler())
        
        Chaining this way provides a way to select amongst alternative
        handler implementations in method resolution order.
        
        The returned handler should be a method that takes a request along
        with a variable number of arguments and keyword arguments, i.e.
        (request, *args, **kwargs). It may also take a request with specific
        arguments and keyword arguments that correspond to the view's
        URL pattern.
        
        The default implementation raises NotImplementedError, as it will only
        be called when subclasses have implemented something incorrectly.
        
        """
        raise NotImplementedError
    
    def dispatch(self, request, *args, **kwargs):
        """
        Dispatch the request.
        
        """
        return (
            self.get_not_allowed_handler() or
            self.get_allowed_handler())(
                request, *args, **kwargs)


class CommonResponseView(generic.View):
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
    The not modified (304), not allowed (405) and server error (500) responses
    are not provided, as they are handled automatically by other
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


class View(CommonResponseView, SecuredView):
    """
    Improves Django's base View class with features for generating common
    responses and consistently handling security checks.
    
    Integrates the Django's base View class' HTTP method name security check
    into the dispatch system provided by SecuredView.
    
    """
    def http_method_test(self):
        """
        A hook to override the way that HTTP request methods are checked.
        Returns True to allow the request and False to deny it.
        
        """
        method = self.request.method.lower()
        return (
            method in self.http_method_names and
            isinstance(getattr(self, method, None), collections.Callable))
    
    def get_not_allowed_handler(self):
        """
        Returns self.http_method_not_allowed when the HTTP method name
        is not allowed or not implemented, as calculated by
        self.http_method_test(), falling back to super().
        
        """
        return (
            not self.http_method_test() and
            self.http_method_not_allowed or
            super(View, self).get_not_allowed_handler())
    
    def get_allowed_handler(self):
        """
        Returns a handler based on the HTTP method name, falling back
        to super().
        
        """
        return (
            getattr(self, self.request.method.lower(), None) or
            super(View, self).get_allowed_handler())


class TemplateView(generic.TemplateView, View):
    """
    Extends Django's TemplateView class with features from
    daydreamer.views.generic.View.
    
    """
    pass


class RedirectView(generic.RedirectView, View):
    """
    Extends Django's RedirectView class with features from
    daydreamer.views.generic.View.
    
    """
    pass
