from __future__ import unicode_literals

from django import http
from django.conf import settings
from django.contrib import messages
from django.core import exceptions

from daydreamer.core import urlresolvers

from . import base


__all__ = ("Denial",)


class Denial(base.Deny):
    """
    An abstract base class providing a denial behavior framework.
    
    Implements the deny() method, which when called:
    
        * If exceptions are enabled, raises the configured exception.
        * If a denial message has been specified, enqueues a message with the
          django.contrib.messages framework.
        * Finally, redirects to a denial URL with an optional query string
          specifying the next URL, i.e. to redirect back when desired.
    
    This encapsulates common view patterns and makes them configurable
    through a declarative API, facilitating the implementation of many
    view behaviors and helping you avoid repetition of boilerplate code. The
    view behaviors in daydreamer.views.behaviors make heavy use of these
    features and can simplify your view implementations.
    
    The deny() method should be called with a prefix name that it
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
        
    Additional object-oriented hooks are provided by the implementation. See
    the source code for details.
    
    """
    # Hooks for resolving attribute values used by deny().
    def get_denial_attr(self, prefix, attr):
        """
        A hook to customize the way that attributes for the deny()
        method are retrieved from a prefix and attribute name.
        
        The default implementation joins the prefix and attribute name with
        "_" and looks up the attribute with getattr. This will raise an
        AttributeError if the generated attribute name does not exist.
        
        """
        return getattr(self, "_".join((prefix, attr)))
    
    def get_denial_raise(self, prefix):
        """
        A hook to customize resolution of the exception raising setting
        used by deny().
        
        The default implementation returns self.<prefix>_raise.
        
        """
        return self.get_denial_attr(prefix, "raise")
    
    def get_denial_exception(self, prefix):
        """
        A hook to customize resolution of the exception value to raise
        used by deny().
        
        The default implementation returns self.<prefix>_exception,
        defaulting to django.core.exceptions.PermissionDenied when falsy.
        
        """
        return (
            self.get_denial_attr(prefix, "exception") or
            exceptions.PermissionDenied)
    
    def get_denial_message(self, prefix):
        """
        A hook to customize resolution of the message value to enqueue,
        used by deny().
        
        The default implementation returns self.<prefix>_message.
        
        """
        return self.get_denial_attr(prefix, "message")
    
    def get_denial_message_level(self, prefix):
        """
        A hook to customize resolution of the message level used
        by deny().
        
        The default implementation returns self.<prefix>_message_level,
        defaulting to django.contrib.messages.WARNING when falsy.
        
        """
        return (
            self.get_denial_attr(prefix, "message_level") or
            messages.WARNING)
            
    def get_denial_message_tags(self, prefix):
        """
        A hook to customize resolution of the message tags used
        by deny().
        
        The default implementation returns self.<prefix>_message_tags,
        defaulting to the empty string when falsy.
        
        """
        return (
            self.get_denial_attr(prefix, "message_tags") or "")
    
    def get_denial_redirect_url(self, prefix):
        """
        A hook to customize resolution of the redirect URL used
        by deny().
        
        The default implementation returns self.<prefix>_redirect_url,
        defaulting to the resolved value for settings.LOGIN_URL when falsy.
        
        """
        redirect_url = self.get_denial_attr(prefix, "redirect_url")
        try:
            redirect_url = (
                redirect_url or urlresolvers.reverse(settings.LOGIN_URL))
        except urlresolvers.NoReverseMatch:
            redirect_url = settings.LOGIN_URL
        return redirect_url
    
    def get_denial_redirect_next_url(self, prefix):
        """
        A hook to customize resolution of the redirect's next URL used
        by deny().
        
        The default implementation returns self.<prefix>_redirect_next_url,
        defaulting to the request's fully-qualified URL when falsy.
        
        """
        return (
            self.get_denial_attr(prefix, "redirect_next_url") or
            self.request.build_absolute_uri())
    
    def get_denial_redirect_next_name(self, prefix):
        """
        A hook to customize resolution of the redirect next URL query parameter
        name used by deny().
        
        The default implementation returns self.<prefix>_redirect_next_name.
        
        """
        return self.get_denial_attr(prefix, "redirect_next_name")
    
    def get_denial_full_redirect_url(self, prefix):
        """
        A hook to customize building of the full redirect URL used
        by deny().
        
        The default implementation updates the query string for
        self.get_denial_redirect_url() to include a parameter named
        self.get_denial_redirect_next_name() with a value of
        self.get_denial_redirect_next_url(). The query string is updated
        only when the parameter name is truthy. Simplifies the query string
        value with respect to the redirect URL and request.
        
        """
        redirect_url = self.get_denial_redirect_url(prefix)
        next_name = self.get_denial_redirect_next_name(prefix)
        if next_name:
            return urlresolvers.update_query(
                redirect_url, {
                    next_name: urlresolvers.simplify_redirect(
                        self.get_denial_redirect_next_url(prefix),
                        redirect_url,
                        request=self.request)})
        return redirect_url
    
    # Hooks to modify the implementation of deny().
    def denial_raise_exception(self, prefix):
        """
        A hook to customize raising of an exception in deny().
        
        In the default implementation, when self.get_denial_raise() is
        truthy, raises self.get_denial_exception().
        
        """
        if self.get_denial_raise(prefix):
            raise self.get_denial_exception(prefix)
    
    def denial_enqueue_message(self, prefix):
        """
        A hook to customize message enqueuing in deny().
        
        The default implementation enqueues self.get_denial_messge() using
        the other self.get_denial_message_*() settings when the message
        is truthy.
        
        """
        message = self.get_denial_message(prefix)
        if message:
            messages.add_message(
                self.request,
                self.get_denial_message_level(prefix),
                message,
                extra_tags=self.get_denial_message_tags(prefix))
    
    def denial_respond(self, prefix):
        """
        A hook to customize the response upon in deny().
        
        The default implementation resolves the redirect URL with
        self.get_denial_full_redirect_url() and returns the
        resolved URL in a redirect response.
        
        """
        return http.HttpResponseRedirect(
            self.get_denial_full_redirect_url(prefix))
    
    def deny(self, prefix):
        """
        The handler that should be called upon access test failure with
        the prefix name for the behavior-controlling attributes.
        
        The default implementation optionally attempts to raise an exception
        with denial_raise_exception(). Then, it optionally enqueues a
        message with denial_enqueue_message(). Finally, it returns a
        redirect response which may include an optional next URL query string
        value with denial_respond().
        
        """
        self.denial_raise_exception(prefix)
        self.denial_enqueue_message(prefix)
        return self.denial_respond(prefix)
