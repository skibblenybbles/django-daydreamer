from __future__ import unicode_literals

import collections
import functools
import urlparse

from django import http
from django.http import request
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import decorators as auth_decorators
from django.core import exceptions
from django.utils import encoding, six

from uap.core import urlresolvers

from .. import generic


__all__ = ("AccessTest", "LoginRequired", "PermissionsRequired",)


class AccessTest(generic.View):
    """
    A view decorator mixin that checks a predicate against the request.
    When the test fails:
        * If exceptions are an enabled, raises the configured exception.
        * If a failure message has been specified, messages the user with
          the django.contrib.messages framework.
        * Finally, redirects to the failure URL with an optional query string
          specifying the next URL, i.e. to to redirect back when desired.
    
    The access_test() method should be a predicate that returns a boolean.
    To facilitate multiple mixins, you should calculate a result and 
    combine it the super()'s result by anding, e.g.:
    
        def access_test(self):
            return (
                self.some_access_test() and
                super(SomeView, self).access_test())
    
    If the access_test attribute is None, all access testing will be disabled.
    
    When access_test_raise attribute is set to a truthy value, raises
    self.access_test_exception upon test failure. It initial value is False.
    
    Set the access_test_exception attribute to an exception class or instance
    that should be raised upon test failure. Defaults to
    django.core.exceptions.PermissionDenied when falsy.
    
    Set the access_test_message attribute to a message to display to the user
    via the django.contrib.messages framework upon test failure. If falsy, no
    message will be displayed.
    
    Set the access_test_message_level attribute to the level of the failure
    message, a value from django.contrib.messages.constants. Defaults
    to WARNING when falsy.
    
    Set the access_test_message_tags attribute to a space-separated string
    specifying additional tags to add to the message, typically used for CSS
    styling purposes. Defaults to the empty string when falsy.
    
    Set the access_test_redirect_url attribute to the failure redirect URL.
    Defaults to settings.LOGIN_URL when falsy. Unlike the view decorators in
    django.contrib.auth.decorators, the URL must be a string or a lazy string,
    such as the result of django.core.urlresolvers.reverse_lazy(). However,
    settings.LOGIN_URL may be a named URL pattern, as documented for Django's
    settings.
    
    Set the access test_redirect_next_url attribute to the URL of the value
    for the query string parameter to append to the redirect URL. Defaults
    to the requst's fully-qualified URL when falsy.
    
    Set the access_test_redirect_next_field_name attribute to the name of the
    query string parameter to append to the redirect URL for the value of
    the next URL. if None, the addition of the query string parameter will be
    disabled. The initial setting is django.contrib.auth.REDIRECT_FIELD_NAME.
    
    These attributes are used by access_test_not_allowed() and the
    other access_test_not_allows_*() methods to implement the access test
    failure response behavior. See their documentation for available hooks.
    
    For subclass mixins in general, views will run the rightmost inherited
    AccessTest subclass' test first and then proceed to the left. In order
    for the correct exception, message, etc. attribute to be selected,
    subclasses should implement attributes as properties and only return
    their customized values when their subclass implements the active handler
    in self.handler, always falling back to the super()'s value. For better
    abstraction, subclasses should define a predicate to test whether it is
    the handler. Here's an example:
    
        class SomeTest(AccessTest):
            def some_test_not_allowed(self):
                # The not allowed handler for this class' test.
                # ...
            
            @property
            def some_test_is_handler(self):
                return self.handler == self.some_test_not_allowed
            
            @property
            def access_test_exception(self):
                return (
                    self.some_test_is_handler and
                    self.some_test_exception or
                    super(SomeTest, self).access_test_exception)
            
            @property
            def access_test_message(self):
                # ...
            
            # ...
    
    """
    access_test_raise = False
    access_test_exception = None
    access_test_message = None
    access_test_message_level = None
    access_test_message_tags = None
    access_test_redirect_url = None
    access_test_redirect_next_url = None
    access_test_redirect_next_field_name = auth.REDIRECT_FIELD_NAME
    
    @property
    def access_test_is_handler(self):
        """
        A predicate to test whether AccessTest's handler is active.
        
        Not used in this implementation, but provided for symmetry with
        subclass usage patterns.
        
        """
        return self.handler == self.access_test_not_allowed
    
    def access_test(self):
        """
        By default, this test always passes. Subclasses should override the
        access_test() method to calculate a predicate and combine the result
        with the super() method's by anding them together, e.g.
        
            def access_test(self):
                return (
                    self.some_access_test() and
                    super(SomeView, self).access_test())
        
        """
        return True
    
    def access_test_not_allowed_exception(self):
        """
        A hook to customize optional exception raising upon access
        test failure.
        
        The default implementation raises self.access_test_exception if it is
        not None.
        
        """
        if self.access_test_raise:
            raise self.access_test_exception or exceptions.PermissionDenied
    
    def access_test_not_allowed_message(self):
        """
        A hook to customize optional message enqueuing upon access
        test failure.
        
        The default implementation enqueues self.access_test_message using the
        other self.access_test_message_* parameters when the message is
        not None.
        
        """
        message = self.access_test_message
        if message:
            messages.add_message(self.request,
                self.access_test_message_level or messages.WARNING,
                message,
                extra_tags=self.access_test_message_tags or "")
    
    def access_test_not_allowed_redirect_next_url(self):
        """
        A hook to customize resolution of redirect's next URL upon access test
        failure.
        
        The default implementation returns self.access_test_redirect_next_url,
        defaulting to the request's fully-qaulified URL when it is None.
        
        """
        return (
            self.access_test_redirect_next_url or
            self.request.build_absolute_url())
    
    def access_test_not_allowed_redirect_next(self, redirect_url):
        """
        A hook to customize the addition of a next URL query parameter to the
        redirect URL. Must accept a redirect URL argument, which may be lazy.
        
        The default implementation updates the redirect URL's query string with
        a parameter name from self.access_test_redirect_field_name and a value
        from self.access_test_not_allowed_redirect_url() when the parameter
        name is not None. Simplifies the query string value with respect to the
        redirect URL and request.
        
        """
        next_field_name = self.access_test_redirect_next_field_name
        if next_field_name is not None:
            return urlresolvers.update_query(redirect_url, {
                next_field_name: urlresolvers.simplify_redirect(
                    self.access_test_not_allowed_redirect_next_url(),
                    redirect_url,
                    request=self.request)})
        return redirect
    
    def access_test_not_allowed_redirect_url(self):
        """
        A hook to customize resolution of the redirect URL upon access
        test failure.
        
        The default implementation returns self.access_test_redirect_url,
        falling back to the resolved value for settings.LOGIN_URL.
        
        """
        redirect_url = self.access_test_redirect_url
        try:
            redirect_url = redirect or urlresolvers.resolve(settings.LOGIN_URL)
        except urlresolvers.NoReverseMatch:
            redirect_url = settings.LOGIN_URL
        return redirect_url
    
    def access_test_not_allowed_response(self):
        """
        A hook to customize the response upon access test failure.
        
        The default resolves the redirect URL with
        self.access_test_not_allowed_redirect_url(), appends the next URL
        query string with self.access_test_not_allowed_redirect_next()
        and returns the resolved URL in a redirect response.
        
        """
        return http.HttpResponseRedirect(
            self.access_test_not_allowed_redirect_next(
                self.access_test_not_allowed_redirect_url()))
    
    def access_test_not_allowed(self, request, *args, **kwargs):
        """
        The handler called upon access test failure.
        
        """
        self.access_test_not_allowed_exception()
        self.access_test_not_allowed_message()
        return self.access_test_not_allowed_response()
    
    def not_allowed_handler(self):
        """
        Returns self.access_test_not_allowed when the access test fails,
        falling back to the super().
        
        """
        return (
            isinstance(self.access_test, collections.Callable) and
            not self.access_test() and 
            self.access_test_not_allowed or
            super(AccessTest, self).not_allowed_handler())


class LoginRequired(AccessTest):
    """
    A view decorator mixin that tests whether the user is authenticated.
    
    If the login_required attribute is falsy, the login requirement testing
    will be disabled. Its initial value is True.
    
    When login_required_raise attribute is set to a truthy value, raises
    self.login_required_exception upon test failure. If falsy, the base class'
    access_test_raise value will be used.
    
    Set the login_required_exception attribute to an exception class or
    instance that should be raised upon test failure. If falsy, the base class'
    access_test_exception value will be used.
    
    Set the login_required_message attribute to a message to display to the
    user via the django.contrib.messages framework upon test failure. If falsy,
    the base class' access_test_message value will be used.
    
    Set the login_required_message_level attribute to the level of the failure
    message, a value from django.contrib.messages.constants. If falsy, the base
    class' access_test_message_level value will be used.
    
    Set the login_required_message_tags attribute to a space-separated string
    specifying additional tags to add to the message, typically used for CSS
    styling purposes. If falsy, the base class' access_test_message_tags value
    will be used.
    
    Set the login_required_redirect_url attribute to the failure redirect URL.
    If falsy, the base class' access_test_redirect_url value will be used.
    The URL must be a string or a lazy string, such as the result of
    django.core.urlresolvers.reverse_lazy().
    
    Set the login_required_redirect_next_url attribute to the URL of the value
    for the query string parameter to append to the redirect URL. If falsy,
    the base class' access_test_redirect_next_url value will be used.
    
    Set the login_required_redirect_next_field_name attribute to the name of
    the query string parameter to append to the redirect URL for the value of
    the next URL. If falsy, the base class' access_test_redirect_next_field_name
    value will be useed.
    
    """
    login_required = True
    login_required_raise = False
    login_required_exception = None
    login_required_message = None
    login_required_message_level = None
    login_required_message_tags = None
    login_required_redirect_url = None
    login_required_redirect_next_url = None
    login_required_redirect_next_field_name = None
    
    @property
    def login_required_is_handler(self):
        """
        A predicate to test whether LoginRequired's handler is active.
        
        """
        return self.handler == self.login_required_not_allowed
    
    @property
    def access_test_raise(self):
        return (
            self.login_required_is_handler and
            self.login_required_raise or
            super(LoginRequired, self).access_test_raise)
    
    @property
    def access_test_exception(self):
        return (
            self.login_required_is_handler and
            self.login_required_exception or
            super(LoginRequired, self).access_test_exception)
    
    @property
    def access_test_message(self):
        return (
            self.login_required_is_handler and
            self.login_required_message or
            super(LoginRequired, self).access_test_message)
    
    @property
    def access_test_message_level(self):
        return (
            self.login_required_is_handler and
            self.login_required_message_level or
            super(LoginRequired, self).access_test_message_level)
    
    @property
    def access_test_message_tags(self):
        return (
            self.login_required_is_handler and
            self.login_required_message_tags or
            super(LoginRequired, self).access_test_message_tags)
    
    @property
    def access_test_redirect_url(self):
        return (
            self.login_required_is_handler and
            self.login_required_redirect_url or
            super(LoginRequired, self).access_test_redirect_url)
    
    @property
    def access_test_redirect_next_url(self):
        return (
            self.login_required_is_handler and
            self.login_required_redirect_next_url or
            super(LoginRequired, self).access_test_redirect_next_url)
    
    @property
    def access_test_redirect_next_field_name(self):
        return (
            self.login_required_is_handler and
            self.login_required_redirect_next_field_name or
            super(LoginRequired, self).access_test_redirect_next_field_name)
    
    def login_required_not_allowed(self, request, *args, **kwargs):
        """
        The handler called upon login required test failure.
        
        """
        return self.access_test_not_allowed(request, *args, **kwargs)
    
    def not_allowed_handler(self):
        """
        Returns self.login_required_not_allowed when the login requirement
        test fails, falling back to super().
        
        """
        return (
            self.login_required and
            not self.request.user.is_authenticated() and
            self.login_required_not_allowed or
            super(LoginRequired, self).not_allowed_handler())


class PermissionsRequired(AccessTest):
    """
    A view decorator mixin that tests whether the user has a set of
    specific permissions.
    
    If the permissions_required attribute is falsy, the permissions requirement
    testing will be disalbed. Its initial value is None. The value can be
    either a single permission name, an iterable of permission names or an
    iterable of two-tuples where the first item is either a single permission
    name or an iterable of permission names and the second item is an object
    to which the permissions apply. Typically, you would generate the object
    dynamically by writing the attribute as a prroperty. Here are valid
    examples of permissions:
        
        # Single permission.
        permissions_required = "article.can_add"
        
        # Permission list.
        permissions_required = ("article.can_add", "article.can_edit")
        
        # Single permission for an object.
        @property
        def permissions_required(self):
            return (
                ("article.can_add", self.get_article()),)
        
        # Multiple permissions for an object.
        @property
        def permissions_required(self):
            return (
                (("article.can_add", "article.can_edit"), self.get_article()),)
        
        # Mixed permissions and objects.
        @property
        def permissions_required(self):
            return (
                "article.can_add",
                ("article.can_edit", self.get_artricle()),
                (("comment.can_add", "comment.can_edit"), self.get_comment()),)
    
    When permissions_required_raise attribute is set to a truthy value, raises
    self.permissions_required_exception upon test failure. If falsy, the base
    class' access_test_raise value will be used.
    
    Set the permissions_required_exception attribute to an exception class or
    instance that should be raised upon test failure. If falsy, the base class'
    access_test_exception value will be used.
    
    Set the permissions_required_message attribute to a message to display to the
    user via the django.contrib.messages framework upon test failure. If falsy,
    the base class' access_test_message value will be used.
    
    Set the permissions_required_message_level attribute to the level of the
    failure message, a value from django.contrib.messages.constants. If falsy,
    the base class' access_test_message_level value will be used.
    
    Set the permissions_required_message_tags attribute to a space-separated string
    specifying additional tags to add to the message, typically used for CSS
    styling purposes. If falsy, the base class' access_test_message_tags value
    will be used.
    
    Set the permissions_required_redirect_url attribute to the failure redirect URL.
    If falsy, the base class' access_test_redirect_url value will be used.
    The URL must be a string or a lazy string, such as the result of
    django.core.urlresolvers.reverse_lazy().
    
    Set the permissions_required_redirect_next_url attribute to the URL of the value
    for the query string parameter to append to the redirect URL. If falsy,
    the base class' access_test_redirect_next_url value will be used.
    
    Set the permissions_required_redirect_next_field_name attribute to the name of
    the query string parameter to append to the redirect URL for the value of
    the next URL. If falsy, the base class' access_test_redirect_next_field_name
    value will be useed.
    
    """
    permissions_required = None
    permissions_required_raise = False
    permissions_required_exception = None
    permissions_required_message = None
    permissions_required_message_level = None
    permissions_required_message_tags = None
    permissions_required_redirect_url = None
    permissions_required_redirect_next_url = None
    permissions_required_redirect_next_field_name = None
    
    @property
    def permissions_required_is_handler(self):
        """
        A predicate to test whether PermissionsRequired's handler is active.
        
        """
        return self.handler == self.permissions_required_not_allowed
    
    @property
    def permissions_required_raise(self):
        return (
            self.permissions_required_is_handler and
            self.permissions_required_raise or
            super(PermissionsRequired, self).access_test_raise)
    
    @property
    def access_test_exception(self):
        return (
            self.permissions_required_is_handler and
            self.permissions_required_exception or
            super(PermissionsRequired, self).access_test_exception)
    
    @property
    def access_test_message(self):
        return (
            self.permissions_required_is_handler and
            self.permissions_required_message or
            super(PermissionsRequired, self).access_test_message)
    
    @property
    def access_test_message_level(self):
        return (
            self.permissions_required_is_handler and
            self.permissions_required_message_level or
            super(PermissionsRequired, self).access_test_message_level)
    
    @property
    def access_test_message_tags(self):
        return (
            self.permissions_required_is_handler and
            self.permissions_required_message_tags or
            super(PermissionsRequired, self).access_test_message_tags)
    
    @property
    def access_test_redirect_url(self):
        return (
            self.permissions_required_is_handler and
            self.permissions_required_redirect_url or
            super(PermissionsRequired, self).access_test_redirect_url)
    
    @property
    def access_test_redirect_next_url(self):
        return (
            self.permissions_required_is_handler and
            self.permissions_required_redirect_next_url or
            super(PermissionsRequired, self).access_test_redirect_next_url)
    
    @property
    def access_test_redirect_next_field_name(self):
        return (
            self.permissions_required_is_handler and
            self.permissions_required_redirect_next_field_name or
            super(PermissionsRequired, self).access_test_redirect_next_field_name)
    
    def permissions_required_not_allowed(self, request, *args, **kwargs):
        """
        The handler called upon permissions requirement test failure.
        
        """
        return self.access_test_not_allowed(request, *args, **kwargs)
    
    def not_allowed_handler(self):
        """
        Returns self.permissions_required_not_allowed when the permissions
        test fails, falling back to super().
        
        Returns the super()'s not allowed handler, falling back to the
        self.permissions_required_not_allowed() handler when the permissions
        requirement test fails.
        
        """
        def unpack(permission):
            if isinstance(permission, six.string_types):
                return ((permission,), None,)
            permissions, obj = permission
            if isinstance(permissions, six.string_types):
                return ((permissions,), obj,)
            return permission
        
        permissions_required = self.permissions_required
        if isinstance(permissions_required, six.string_types):
            permissions_required = (permissions_required,)
        
        return (
            permissions_required and
            not any(
                self.request.user.has_perms(permissions, obj)
                for permissions, obj in (
                    unpack(permission)
                    for permission in permissions_required or ())) and
            self.permission_required_not_allowed or
            super(PermissionsRequired, self).not_allowed_handler())
