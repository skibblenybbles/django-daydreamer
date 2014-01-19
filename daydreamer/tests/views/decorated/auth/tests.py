from __future__ import unicode_literals

from daydreamer.views.decorated import auth as auth_decorated

from . import base


class LoginRequiredTestCase(base.TestCase):
    """
    Tests for the LoginRequired view decorator mixin.
    
    """
    view_class = auth_decorated.LoginRequired
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
    Tests for the ActiveRequired view decorator mixin.
    
    """
    view_class = auth_decorated.ActiveRequired
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
    Tests for the StaffRequired view decorator mixin.
    
    """
    view_class = auth_decorated.StaffRequired
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
    Tests for the SuperuserRequired view decorator mixin.
    
    """
    view_class = auth_decorated.SuperuserRequired
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




