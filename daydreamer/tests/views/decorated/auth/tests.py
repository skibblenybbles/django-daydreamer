from __future__ import unicode_literals

from django.contrib import auth

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
        username = self.unique()[:30]
        password = self.unique()
        auth.get_user_model().objects.create_user(username, password=password)
        self.client.login(username=username, password=password)
        return {}
