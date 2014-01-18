from __future__ import unicode_literals

from daydreamer.views.decorated import auth

from . import base


class LoginRequiredTestCase(base.TestCase):
    """
    Tests for the LoginRequired view decorator mixin.
    
    """
    def test_login_required_defaults(self):
        
        from daydreamer.views import generic
        response = self.client.get("/", **{
            "django.view": self.view(
                generic.View, "")})
        
        '''
        response = self.client.get("/", **{
            "django.view": self.view(
                auth.LoginRequired, "login_required")})
        '''
        
        print '-' * 75
        print response
        print '-' * 75
