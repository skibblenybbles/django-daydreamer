from __future__ import unicode_literals

import collections

from django.contrib import auth
from django.contrib.auth import models as auth_models
from django.core import exceptions
from django.utils import six

from .. import core


__all__ = (
    "LoginRequired", "ActiveRequired", "StaffRequired", "SuperuserRequired",
    "GroupsRequired", "PermissionsRequired", "ObjectPermissionsRequired",
    "TestRequired",)


class LoginRequired(core.behaviors.Denial):
    """
    A view behavior that tests whether the user is authenticated.
    
    If the login_required attribute is falsy, the login requirement testing
    will be disabled. Its initial value is True.
    
    Set the login_required_* attributes to configure the behavior when a login
    is required in order for the user to proceed. See
    daydreamer.views.core.behaviors.Denial for the attributes' documentation.
    
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
    
    def get_login_required(self):
        """
        A hook to override the login_required value.
        
        The default implementation returns self.login_required.
        
        """
        return self.login_required
    
    def login_required_test(self):
        """
        A hook to override the way that the login requirement test is peformed.
        
        """
        return (
            not self.get_login_required() or 
            self.request.user.is_authenticated())
    
    def login_required_denied(self, request, *args, **kwargs):
        """
        The handler called upon login requirement test failure.
        
        """
        return self.deny("login_required")
    
    def get_deny_handler(self):
        """
        Returns self.login_required_denied when the login requirement
        test fails, falling back to super().
        
        """
        return (
            not self.login_required_test() and
            self.login_required_denied or
            super(LoginRequired, self).get_deny_handler())


class ActiveRequired(core.behaviors.Denial):
    """
    A view behavior that tests whether the user is active.
    
    If the active_required attribute is falsy, the active requirement testing
    will be disabled. Its initial value is True.
    
    Set the active_required_* attributes to configure the behavior when an
    active user is required in order for the user to proceed. See
    daydreamer.views.core.behaviors.Denial for the attributes' documentation.
    
    """
    active_required = True
    active_required_raise = False
    active_required_exception = None
    active_required_message = None
    active_required_message_level = None
    active_required_message_tags = None
    active_required_redirect_url = None
    active_required_redirect_next_url = None
    active_required_redirect_next_name = auth.REDIRECT_FIELD_NAME
    
    def get_active_required(self):
        """
        A hook to override the active_required value.
        
        The default implementation returns self.active_required.
        
        """
        return self.active_required
    
    def active_required_test(self):
        """
        A hook to override the way that the active requirement test
        is performed.
        
        """
        return (
            not self.get_active_required() or
            self.request.user.is_active)
    
    def active_required_denied(self, request, *args, **kwargs):
        """
        The handler called upon active requirement test failure.
        
        """
        return self.deny("active_required")
    
    def get_deny_handler(self):
        """
        Returns self.active_required_denied when the active requirement
        test fails, falling back to super().
        
        """
        return (
            not self.active_required_test() and
            self.active_required_denied or
            super(ActiveRequired, self).get_deny_handler())


class StaffRequired(core.behaviors.Denial):
    """
    A view behavior that tests whether the user is a staff member.
    
    If the staff_required attribute is falsy, the staff requirement testing
    will be disabled. Its initial value is True.
    
    Set the staff_required_* attributes to configure the behavior when a
    staff user is required in order for the user to proceed. See
    daydreamer.views.core.behaviors.Denial for the attributes' documentation.
    
    """
    staff_required = True
    staff_required_raise = False
    staff_required_exception = None
    staff_required_message = None
    staff_required_message_level = None
    staff_required_message_tags = None
    staff_required_redirect_url = None
    staff_required_redirect_next_url = None
    staff_required_redirect_next_name = auth.REDIRECT_FIELD_NAME
    
    def get_staff_required(self):
        """
        A hook to override the staff_required value.
        
        The default implementation returns self.staff_required.
        
        """
        return self.staff_required
    
    def staff_required_test(self):
        """
        A hook to override the way that the active requirement test
        is performed.
        
        """
        return (
            not self.get_staff_required() or
            self.request.user.is_staff)
    
    def staff_required_denied(self, request, *args, **kwargs):
        """
        The handler called upon staff requirement test failure.
        
        """
        return self.deny("staff_required")
    
    def get_deny_handler(self):
        """
        Returns self.staff_required_denied when the staff requirement
        test fails, falling back to super().
        
        """
        return (
            not self.staff_required_test() and
            self.staff_required_denied or
            super(StaffRequired, self).get_deny_handler())


class SuperuserRequired(core.behaviors.Denial):
    """
    A view behavior that tests whether the user is a superuser.
    
    If the superuser_required attribute is falsy, the superuser requirement
    testing will be disabled. Its initial value is True.
    
    Set the superuser_required_* attributes to configure the behavior when
    a superuser is required in order for the user to proceed. See
    daydreamer.views.core.behaviors.Denial for the attributes' documentation.
    
    """
    superuser_required = True
    superuser_required_raise = False
    superuser_required_exception = None
    superuser_required_message = None
    superuser_required_message_level = None
    superuser_required_message_tags = None
    superuser_required_redirect_url = None
    superuser_required_redirect_next_url = None
    superuser_required_redirect_next_name = auth.REDIRECT_FIELD_NAME
    
    def get_superuser_required(self):
        """
        A hook to override the superuser_required value.
        
        The default implementation returns self.superuser_required.
        
        """
        return self.superuser_required
    
    def superuser_required_test(self):
        """
        A hook to override the way that the superuser requirement test
        is performed.
        
        """
        return (
            not self.get_superuser_required() or
            self.request.user.is_superuser)
    
    def superuser_required_denied(self, request, *args, **kwargs):
        """
        The handler called upon superuser requirement test failure.
        
        """
        return self.deny("superuser_required")
    
    def get_deny_handler(self):
        """
        Returns self.superuser_required_denied when the superuser
        requirement test fails, falling back to super().
        
        """
        return (
            not self.superuser_required_test() and
            self.superuser_required_denied or
            super(SuperuserRequired, self).get_deny_handler())


class GroupsRequired(core.behaviors.Denial):
    """
    A view behavior that tests whether the user is in a set of groups.
    
    If the groups_required attribute is falsy, the groups requirement testing
    will be disabled. Its initial value is None. The groups_required attribute
    can be either a single value or an iterable of values. Each value should be
    a group name or a django.contrib.auth.models.Group object. When named
    groups are specified, the corresponding Groups must exist, or a
    django.core.exceptions.ImproperlyConfigured exception will be raised.
    If any values is not a string or a Group object, a ValueError will
    be raised.
    
    Set the groups_required_* attribute to configure the behavior when a set
    of groups is required in order for the user to proceed. See
    daydreamer.views.core.behaviors.Denial for the attributes' documentation.
    
    """
    groups_required = None
    groups_required_raise = False
    groups_required_exception = None
    groups_required_message = None
    groups_required_message_level = None
    groups_required_message_tags = None
    groups_required_redirect_url = None
    groups_required_redirect_next_url = None
    groups_required_redirect_next_name = auth.REDIRECT_FIELD_NAME
    
    def get_groups_required(self):
        """
        A hook to override the groups_required_value.
        
        The default implementation normalizes the groups into a set
        of primary keys. If the groups_required attribute includes a
        value that is not a group name or a
        django.contrib.auth.models.Group object, a ValueError will be raised.
        If any group names do not exist in the database, a
        django.core.exceptions.ImproperlyConfigured exception will be raised.
        
        """
        # Normalize single instances to tuples.
        groups = self.groups_required or set()
        if isinstance(groups, six.string_types + (auth_models.Group,)):
            groups = (groups,)
        elif not isinstance(groups, collections.Iterable):
            raise ValueError(
                "The value {value!r} specified for groups_required is not a "
                "group name, nor a Group nor an iterable of groups.".format(
                    value=groups))
        
        # Resolve the group names and Group objects into existing Groups'
        # primary keys.
        if groups:
            # Filter the groups into buckets by type.
            named_groups = set()
            actual_groups = set()
            for group in groups:
                if isinstance(group, six.string_types):
                    named_groups.add(group)
                elif isinstance(group, auth_models.Group):
                    actual_groups.add(group)
                else:
                    raise ValueError(
                        "A value {value!r} specified in groups_required "
                        "is not a group name or a Group.".format(value=group))
            
            # Resolve the named groups and perform the sanity check.
            resolved_groups = set(
                auth_models.Group.objects
                    .filter(name__in=named_groups)
                    .values_list("pk", flat=True))
            if len(named_groups) != len(resolved_groups):
                raise exceptions.ImproperlyConfigured(
                    "One or more group names specified in groups_required "
                    "does not exist.")
            
            # Gather all the groups' primary keys.
            groups = resolved_groups | set(group.pk for group in actual_groups)
        return groups
    
    def groups_required_test(self):
        """
        A hook to override the way that the groups requirement test
        is performed.
        
        """
        groups = self.get_groups_required()
        return (
            not groups or
            self.request.user.groups.filter(
                pk__in=groups).count() == len(groups))
    
    def groups_required_denied(self, request, *args, **kwargs):
        """
        The handler called upon groups requirement test failure.
        
        """
        return self.deny("groups_required")
    
    def get_deny_handler(self):
        """
        Returns self.groups_required_denied when the groups
        requirement test fails, falling back to super().
        
        """
        return (
            not self.groups_required_test() and
            self.groups_required_denied or
            super(GroupsRequired, self).get_deny_handler())


class PermissionsRequired(core.behaviors.Denial):
    """
    A view behavior that tests whether the user has a set
    of permissions.
    
    If the permissions_required attribute is falsy, the permissions requirement
    testing will be disabled. Its initial value is None. The permissions_required
    attribute can be either a single permission name or an iterable of
    permission names.
    
    Set the permissions_required_* attributes to configure the behavior when
    permissions are required in order for the user to proceed.
    See daydreamer.views.core.behaviors.Denial for the attributes' documentation.
    
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
    
    def get_permissions_required(self):
        """
        A hook to override the permissions_required value.
        
        The default implementation returns the value of
        self.permissions_required, where a single value is normalized as a
        tuple. If any value in permissions_required is not a permission name, a
        ValueError will be raised.
        
        """
        # Normalize single values to a tuple.
        permissions = self.permissions_required or ()
        if isinstance(permissions, six.string_types):
            permissions = (permissions,)
        elif not isinstance(permissions, collections.Iterable):
            raise ValueError(
                "The permssions_required value is neither a permission name "
                "nor an iterable of permission names.")
        
        # Sanity check.
        if (permissions and
            any(not isinstance(permission, six.string_types)
                for permission in permissions)):
            raise ValueError(
                "One or more values in permissions_required is not a "
                "permission name.")
        
        return permissions
    
    def permissions_required_test(self):
        """
        A hook to override the way that the permissions requirement test
        is performed.
        
        """
        permissions = self.get_permissions_required()
        return (
            not permissions or
            self.request.user.has_perms(permissions))
    
    def permissions_required_denied(self, request, *args, **kwargs):
        """
        The handler called upon permissions requirement test failure.
        
        """
        return self.deny("permissions_required")
    
    def get_deny_handler(self):
        """
        Returns self.permissions_required_denied when the permissions
        requirement test fails, falling back to super().
        
        """
        return (
            not self.permissions_required_test() and
            self.permissions_required_denied or
            super(PermissionsRequired, self).get_deny_handler())


class ObjectPermissionsRequired(core.behaviors.Denial):
    """
    A view behavior that tests whether the user has a set of permissions
    for a particular object.
    
    If either of the object_permissions_required attribute or the
    object_permissions_required_object attributes is falsy, the permissions 
    requirement testing will be disabled. Initial values for these attributes
    are None. The object_permissions_required attribute can be either a single
    permission name or an iterable of permission names. The
    object_permissions_required_object attribute will typically be implemented
    as a property that returns some object retrieved from the database.
    
    Set the object_permissions_required_* attributes to configure the behavior
    when permissions are required for an object in order for the user to
    proceed. See daydreamer.views.core.behaviors.Denial for the
    attributes' documentation.
    
    """
    object_permissions_required = None
    object_permissions_required_object = None
    object_permissions_required_raise = False
    object_permissions_required_exception = None
    object_permissions_required_message = None
    object_permissions_required_message_level = None
    object_permissions_required_message_tags = None
    object_permissions_required_redirect_url = None
    object_permissions_required_redirect_next_url = None
    object_permissions_required_redirect_next_name = auth.REDIRECT_FIELD_NAME
    
    def get_object_permissions_required(self):
        """
        A hook to override the object_permissions_required value.
        
        The default implementation returns the value of
        self.object_permissions_required, where a single value is normalized as
        a tuple. If any value in object_permissions_required is not a
        permission name, a ValueError will be raised.
        
        """
        # Normalize single values to a tuple.
        permissions = self.object_permissions_required or ()
        if isinstance(permissions, six.string_types):
            permissions = (permissions,)
        elif not isinstance(permissions, collections.Iterable):
            raise ValueError(
                "The object_permssions_required value is neither a "
                "permission name nor an iterable of permission names.")
        
        # Sanity check.
        if (permissions and
            any(not isinstance(permission, six.string_types)
                for permission in permissions)):
            raise ValueError(
                "One or more values in object_permissions_required is not a "
                "permission name.")
        return permissions
    
    def get_object_permissions_required_object(self):
        """
        A hook to override the object_permissions_required_object value.
        
        The default implementation returns
        self.object_permissions_required_object.
        
        """
        return self.object_permissions_required_object
    
    def object_permissions_required_test(self):
        """
        A hook to override the way that the object permissions requirement test
        is performed.
        
        """
        permissions = self.get_object_permissions_required()
        obj = self.get_object_permissions_required_object()
        return (
            (not all((permissions, obj,))) or
            self.request.user.has_perms(permissions, obj=obj))
    
    def object_permissions_required_denied(self, request, *args, **kwargs):
        """
        The handler called upon object permissions requirement test failure.
        
        """
        return self.deny("object_permissions_required")
    
    def get_deny_handler(self):
        """
        Returns self.object_permissions_required_denied when the object
        permissions test fails, falling back to super().
        
        """
        return (
            not self.object_permissions_required_test() and
            self.object_permissions_required_denied or
            super(ObjectPermissionsRequired, self).get_deny_handler())


class TestRequired(core.behaviors.Denial):
    """
    A view behavior that performs a test against the current request,
    typically a predicate for self.request.user.
    
    If the test_required attribute is not a callable, the test requirement
    will be disabled. Its initial value is None.
    
    Set the test_required_* attributes to configure the behavior when a
    test must be passed in order for the user to proceed. See
    daydreamer.views.core.behaviors.Denial for the attributes' documentation.
    
    """
    test_required = None
    test_required_raise = False
    test_required_exception = None
    test_required_message = None
    test_required_message_level = None
    test_required_message_tags = None
    test_required_redirect_url = None
    test_required_redirect_next_url = None
    test_required_redirect_next_name = auth.REDIRECT_FIELD_NAME
    
    def get_test_required(self):
        """
        A hook to override the test_required value.
        
        The default implementation returns self.test_required.
        
        """
        return self.test_required
    
    def test_required_test(self):
        """
        A hook to override the way that the required test is performed.
        
        """
        test = self.get_test_required()
        return (
            not isinstance(test, collections.Callable) or
            test())
    
    def test_required_denied(self, request, *args, **kwargs):
        """
        The handler called upon test failure.
        
        """
        return self.deny("test_required")
    
    def get_deny_handler(self):
        """
        Returns self.test_required_denied when the test requirement fails,
        falling back to super().
        
        """
        return (
            not self.test_required_test() and
            self.test_required_denied or
            super(TestRequired, self).get_deny_handler())
