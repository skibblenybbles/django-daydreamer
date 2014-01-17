from __future__ import unicode_literals

from django.contrib import auth, messages
from django.contrib.auth import decorators as auth_decorators
from django.core import exceptions
from django.utils import encoding, six

from uap.core import urlresolvers

from .. import generic


__all__ = ("LoginRequired", "PermissionsRequired",)


class LoginRequired(generic.View):
    """
    A view decorator mixin that tests whether the user is authenticated.
    
    If the login_required attribute is falsy, the login requirement testing
    will be disabled. Its initial value is True.
    
    Set the login_required_* attributes to configure the behavior when a login
    is required for the user to proceed. See daydreamer.views.generic.base.View
    for the attributes' documentation.
    
    """
    login_required = True
    login_required_raise = False
    login_required_exception = None
    login_required_message = None
    login_required_message_level = None
    login_required_message_tags = None
    login_required_redirect_url = None
    login_required_redirect_next_url = None
    login_required_redirect_next_name = auth.REDIRECT_FIELD_NAME
    
    def login_required_test(self):
        """
        A hook to override the way that the login requirement test is peformed.
        
        """
        return (
            not self.login_required or 
            self.request.user_is_authenticated())
    
    def login_required_not_allowed(self, request, *args, **kwargs):
        """
        The handler called upon login required test failure.
        
        """
        return self.not_allowed("login_required")
    
    def not_allowed_handler(self):
        """
        Returns self.login_required_not_allowed when the login requirement
        test fails, falling back to super().
        
        """
        return (
            not self.login_required_test() and
            self.login_required_not_allowed or
            super(LoginRequired, self).not_allowed_handler())


class PermissionsRequired(AccessTest):
    """
    A view decorator mixin that tests whether the user has a set
    of permissions.
    
    If the permissions_required attribute is falsy, the permissions requirement
    testing will be disabled. Its initial value is None. The permissions_required
    attribute can be either a single permission name or an iterable of
    permission names.
    
    Set the permissions_required_* attributes to configure the behavior when
    permissions are required for the user to proceed.
    See daydreamer.views.generic.base.View for the attributes' documentation.
    
    """
    permissions_required = None
    permissions_required_raise = False
    permissions_required_exception = None
    permissions_required_message = None
    permissions_required_message_level = None
    permissions_required_message_tags = None
    permissions_required_redirect_url = None
    permissions_required_redirect_next_url = None
    permissions_required_redirect_next_name = auth.REDIRECT_FIELD_NAME
    
    def permissions_required_test(self):
        """
        A hook to override the way that the permissions requirement test
        is performed.
        
        """
        permissions = self.permissions_required
        if isinstance(permissions, six.string_types):
            permissions = (permissions,)
        return (
            not permissions_required or
            self.request.user.has_perms(permissions))
    
    def permissions_required_not_allowed(self, request, *args, **kwargs):
        """
        The handler called upon permissions requirement test failure.
        
        """
        return self.not_allowed("permissions_required")
    
    def not_allowed_handler(self):
        """
        Returns self.permissions_required_not_allowed when the permissions
        test fails, falling back to super().
        
        """
        return (
            not self.permissions_required_test() and
            self.permissions_required_not_allowed or
            super(PermissionsRequired, self).not_allowed_handler())
