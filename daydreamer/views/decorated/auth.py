from __future__ import unicode_literals

import collections
import functools

from django.contrib import auth, messages
from django.contrib.auth import decorators as auth_decorators
from django.core.exceptions import PermissionDenied
from django.utils.decorators import available_attrs, classonlymethod
from django.views import generic


__all__ = ("UserPassesTest",)


class UserPassesTest(generic.View):
    """
    A view decorator mixin that checks a predicate against the request.user
    object. If the test fails, redirects to the login URL with a query string
    specifying a return URL to this request's URL. Also provides a means to
    message the user with the django.contrib.messages framework.
    
    Set the user_passes_test attribute to a class method that accepts the
    user object. If it is None, no access check will be performed.
    
    Set the user_passes_test_login_url attribute to the URL of the login page.
    It defaults to settings.LOGIN_URL.
    
    Set the user_passes_test_redirect_field_name attribute to the name of the
    query string parameter to append to the login URL. Set to a falsy value to
    disable addition of the query string parameter. The default is
    django.contrib.auth.REDIRECT_FIELD_NAME.
    
    Set the user_passes_test_message to a message to display to the user via
    the django.contrib.messages framework upon test failure. If None, no
    message will be displayed.
    
    Set the user_passes_test_message_level to a value from
    django.contrib.messages.constants to set the level of the message. Defaults
    to WARNING.
    
    Set the user_passes_test_message_extra_tags to a space-separated string
    specifying additional tags to add to the message, typically used for CSS
    styling purposes. Defaults to the empty string.
    
    """
    user_passes_test = None
    user_passes_test_login_url = None
    user_passes_test_redirect_field_name = auth.REDIRECT_FIELD_NAME
    user_passes_test_message = None
    user_passes_test_message_level = None
    user_passes_test_message_extra_tags = ""
    
    @classmethod
    def get_user_passes_test_login_url(cls, request):
        """
        A hook to override the login URL. Must be a class method that
        accepts the request.
        
        """
        return cls.user_passes_test_login_url
    
    @classmethod
    def get_user_passes_test_redirect_field_name(cls, request):
        """
        A hook to override the name of the redirect query string parameter
        name. Must be a class method that accepts the request.
        
        """
        return cls.user_passes_test_redirect_field_name
    
    @classmethod
    def get_user_passes_test_message(cls, request):
        """
        A hook to override the failure message. Must be a class method that
        accepts the request.
        
        """
        return cls.user_passes_test_message
    
    @classmethod
    def get_user_passes_test_message_level(cls, request):
        """
        A hook to override the failure message level. Must be a class method
        that accepts the request.
        
        """
        return cls.user_passes_test_message_level \
            if cls.user_passes_test_message_level is not None \
            else messages.WARNING
    
    @classmethod
    def get_user_passes_test_message_extra_tags(cls, request):
        """
        A hook to override the failure message tags. Must be a class method
        that accepts the request.
        
        """
        return cls.user_passes_test_message_extra_tags
    
    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Decorates the returned view with
        django.contrib.auth.decorators.user_passes_test() and adds
        messaging functionality.
        
        """
        view = super(UserPassesTest, cls).as_view(**kwargs)
        if isinstance(cls.user_passes_test, collections.Callable):
            @functools.wraps(view, assigned=available_attrs(view))
            def _view(request, *args, **kwargs):
                # Does the user pass the test?
                result = cls.user_passes_test(request.user)
                if result:
                    pass
                # Decorate and call the view.
                return auth_decorators.user_passes_test(
                    lambda user: result,
                    login_url=cls.get_user_passes_test_login_url(request),
                    redirect_field_name=\
                        cls.get_user_passes_test_redirect_field_name(request))(
                            view)(request, *args, **kwargs)
            return _view
        return view
