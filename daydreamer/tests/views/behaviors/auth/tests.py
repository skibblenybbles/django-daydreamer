from __future__ import unicode_literals

import unittest

from django.core import exceptions

from daydreamer.views import generic
from daydreamer.views.behaviors import auth as auth

from . import base


class LoginRequiredTestCase(base.TestCase):
    """
    Tests for the LoginRequired view behavior.
    
    """
    view_classes = (auth.LoginRequired, generic.View,)
    prefix = "login_required"
    
    def setup_unauth_fail(self):
        return {}
    
    def setup_auth_fail(self):
        # All authenticated users should pass, so defer to the unauthenticated
        # failure setup.
        return self.setup_unauth_fail()
    
    def setup_unauth_pass(self):
        return {"": False}
    
    def setup_auth_pass(self):
        self.create_authenticated_user()
        return {}


class ActiveRequiredTestCase(base.TestCase):
    """
    Tests for the ActiveRequired view behavior.
    
    """
    view_classes = (auth.ActiveRequired, generic.View,)
    prefix = "active_required"
    
    def setup_unauth_fail(self):
        return {}
    
    def setup_auth_fail(self):
        self.create_authenticated_user(is_active=False)
        return {}
    
    def setup_unauth_pass(self):
        return {"": False}
    
    def setup_auth_pass(self):
        self.create_authenticated_user()
        return {}


class StaffRequiredTestCase(base.TestCase):
    """
    Tests for the StaffRequired view behavior.
    
    """
    view_classes = (auth.StaffRequired, generic.View,)
    prefix = "staff_required"
    
    def setup_unauth_fail(self):
        return {}
    
    def setup_auth_fail(self):
        self.create_authenticated_user()
        return {}
    
    def setup_unauth_pass(self):
        return {"": False}
    
    def setup_auth_pass(self):
        self.create_authenticated_user(is_staff=True)
        return {}


class SuperuserRequiredTestCase(base.TestCase):
    """
    Tests for the SuperuserRequired view behavior.
    
    """
    view_classes = (auth.SuperuserRequired, generic.View,)
    prefix = "superuser_required"
    
    def setup_unauth_fail(self):
        return {}
    
    def setup_auth_fail(self):
        self.create_authenticated_user()
        return {}
    
    def setup_unauth_pass(self):
        return {"": False}
    
    def setup_auth_pass(self):
        self.create_authenticated_user(is_superuser=True)
        return {}


class GroupsRequiredTestCase(base.TestCase):
    """
    Tests for the GroupsRequired view behavior.
    
    """
    view_classes = (auth.GroupsRequired, generic.View,)
    prefix = "groups_required"
    
    def setup_unauth_fail(self):
        group = self.create_group()
        return {"": group.name}
    
    def setup_auth_fail(self):
        self.create_authenticated_user()
        group = self.create_group()
        return {"": group.name}
    
    def setup_unauth_pass(self):
        return {"": None}
    
    def setup_auth_pass(self):
        user = self.create_authenticated_user()
        group = self.create_group()
        user.groups.add(group)
        return {"": group.name}
    
    # Setups for multiple groups required.
    def setup_unauth_fail_multiple(self):
        group1, group2 = groups = (
            self.create_group(), self.create_group(),)
        return {"": (group1.name, group2)}
    
    def setup_auth_fail_multiple(self):
        user = self.create_authenticated_user()
        group1, group2 = groups = (
            self.create_group(), self.create_group(),)
        user.groups.add(group1)
        return {"": (group1.name, group2)}
    
    def setup_auth_pass_multiple(self):
        user = self.create_authenticated_user()
        group1, group2 = groups = (
            self.create_group(), self.create_group(),)
        map(user.groups.add, groups)
        return {"": (group1.name, group2)}
    
    # Tests for multiple groups required.
    def test_unauth_fail_multiple(self):
        return self.test_unauth_fail(self.setup_unauth_fail_multiple)
    
    def test_auth_fail_multiple(self):
        return self.test_auth_fail(self.setup_auth_fail_multiple)
    
    def test_auth_pass_multiple(self):
        return self.test_auth_pass(self.setup_auth_pass_multiple)
    
    # Tests for invalid group values.
    def test_invalid_type(self):
        with self.assertRaises(ValueError):
            self.client.get(self.view(**{"": 1}))
    
    def test_invalid_type_multiple(self):
        with self.assertRaises(ValueError):
            self.client.get(self.view(**{"": (1, 1)}))
    
    def test_invalid_group(self):
        with self.assertRaises(exceptions.ImproperlyConfigured):
            self.client.get(self.view(**{"": self.unique()}))
    
    def test_invalid_group_multiple(self):
        with self.assertRaises(exceptions.ImproperlyConfigured):
            self.client.get(self.view(**{"": (self.unique(), self.unique(),)}))


class PermissionsRequiredTestCase(base.TestCase):
    """
    Tests for the PermissionsRequired view behavior.
    
    """
    view_classes = (auth.PermissionsRequired, generic.View,)
    prefix = "permissions_required"
    
    def setup_unauth_fail(self):
        permission = self.create_permission()
        return {"": ".".join(("auth", permission.codename,))}
    
    def setup_auth_fail(self):
        permission = self.create_permission()
        self.create_authenticated_user()
        return {"": ".".join(("auth", permission.codename,))}
    
    def setup_unauth_pass(self):
        return {}
    
    def setup_auth_pass(self):
        permission = self.create_permission()
        user = self.create_authenticated_user()
        user.user_permissions.add(permission)
        return {"": ".".join(("auth", permission.codename,))}
    
    # Setups for multiple permissions.
    def setup_unauth_fail_multiple(self):
        permissions = self.create_permission(), self.create_permission()
        return {"": [
            ".".join(("auth", permission.codename,))
            for permission in permissions]}
    
    def setup_auth_fail_multiple(self):
        permissions = permission1, permission2 = (
            self.create_permission(), self.create_permission())
        user = self.create_authenticated_user()
        user.user_permissions.add(permission1)
        return {"": [
            ".".join(("auth", permission.codename,))
            for permission in permissions]}
    
    def setup_auth_pass_multiple(self):
        permissions = self.create_permission(), self.create_permission()
        user = self.create_authenticated_user()
        map(user.user_permissions.add, permissions)
        return {"": [
            ".".join(("auth", permission.codename,))
            for permission in permissions]}
    
    # Tests for multiple groups required.
    def test_unauth_fail_multiple(self):
        return self.test_unauth_fail(self.setup_unauth_fail_multiple)
    
    def test_auth_fail_multiple(self):
        return self.test_auth_fail(self.setup_auth_fail_multiple)
    
    def test_auth_pass_multiple(self):
        return self.test_auth_pass(self.setup_auth_pass_multiple)
    
    # Tests for invalid permission values.
    def test_invalid(self):
        with self.assertRaises(ValueError):
            self.client.get(self.view(**{"": 1}))
    
    def test_invalid_multiple(self):
        with self.assertRaises(ValueError):
            self.client.get(self.view(**{"": (1, 1)}))


class ObjectPermissionsRequiredTestCase(base.TestCase):
    """
    Tests for the ObjectPermissionsRequired view behavior.
    
    """
    view_classes = (auth.ObjectPermissionsRequired, generic.View,)
    prefix = "object_permissions_required"
    
    def setup_unauth_fail(self):
        permission = self.create_permission()
        return {
            "": ".".join(("auth", permission.codename,)),
            "object": object()}
    
    def setup_auth_fail(self):
        permission = self.create_permission()
        self.create_authenticated_user()
        return {
            "": ".".join(("auth", permission.codename,)),
            "object": object()}
    
    def setup_unauth_pass(self):
        return {}
    
    def setup_auth_pass(self):
        permission = self.create_permission()
        obj = object()
        user = self.create_authenticated_user()
        # With an object permissions system, the permissions should be for
        # the object.
        user.user_permissions.add(permission)
        return {
            "": ".".join(("auth", permission.codename,)),
            "object": obj}
    
    # Setups for multiple permissions.
    def setup_unauth_fail_multiple(self):
        permissions = self.create_permission(), self.create_permission()
        return {
            "": [
                ".".join(("auth", permission.codename,))
                for permission in permissions],
            "object": object()}
    
    def setup_auth_fail_multiple(self):
        permissions = permission1, permission2 = (
            self.create_permission(), self.create_permission())
        user = self.create_authenticated_user()
        # With an object permissions system, the permissions should be for
        # the object.
        user.user_permissions.add(permission1)
        return {
            "": [
                ".".join(("auth", permission.codename,))
                for permission in permissions],
            "object": object()}
    
    def setup_auth_pass_multiple(self):
        permissions = self.create_permission(), self.create_permission()
        obj = object()
        user = self.create_authenticated_user()
        # With an object permissions system, the permissions should be for
        # the object.
        map(user.user_permissions.add, permissions)
        return {
            "": [
                ".".join(("auth", permission.codename,))
                for permission in permissions],
            "object": obj}
    
    # Tests that cannot pass without an object permissions system.
    @unittest.expectedFailure
    def test_auth_pass(self, setup_auth_pass=None):
        return (
            super(ObjectPermissionsRequiredTestCase, self)
                .test_auth_pass(setup_auth_pass))
    
    @unittest.expectedFailure
    def test_auth_pass_raise(self, setup_auth_pass=None):
        return (
            super(ObjectPermissionsRequiredTestCase, self)
                .test_auth_pass_raise(setup_auth_pass))
    
    @unittest.expectedFailure
    def test_auth_pass_message(self, setup_auth_pass=None):
        return (
            super(ObjectPermissionsRequiredTestCase, self)
                .test_auth_pass_message(setup_auth_pass))
    
    @unittest.expectedFailure
    def test_auth_pass_precedence(self, setup_auth_pass=None):
        return (
            super(ObjectPermissionsRequiredTestCase, self)
                .test_auth_pass(setup_auth_pass))
    
    @unittest.expectedFailure
    def test_auth_pass_multiple(self):
        return self.test_auth_pass(self.setup_auth_pass_multiple)
    
    # Tests for multiple groups required.
    def test_unauth_fail_multiple(self):
        return self.test_unauth_fail(self.setup_unauth_fail_multiple)
    
    def test_auth_fail_multiple(self):
        return self.test_auth_fail(self.setup_auth_fail_multiple)
    
    # Tests for invalid permission values.
    def test_invalid(self):
        with self.assertRaises(ValueError):
            self.client.get(self.view(**{"": 1, "object": object()}))
    
    def test_invalid_multiple(self):
        with self.assertRaises(ValueError):
            self.client.get(self.view(**{"": (1, 1), "object": object()}))


class TestRequiredTestCase(base.TestCase):
    """
    Tests for the TestRequired view behavior.
    
    """
    view_classes = (auth.TestRequired, generic.View,)
    prefix = "test_required"
    
    def create_name_test(self, name):
        def test_required(self):
            return getattr(self.request.user, "first_name", None) == name
        return test_required
    
    def setup_unauth_fail(self):
        return {"": self.create_name_test(self.unique_username())}
    
    def setup_auth_fail(self):
        self.create_authenticated_user()
        return {"": self.create_name_test(self.unique_username())}
    
    def setup_unauth_pass(self):
        return {}
    
    def setup_auth_pass(self):
        name = self.unique_username()
        self.create_authenticated_user(first_name=name)
        return {"": self.create_name_test(name)}
