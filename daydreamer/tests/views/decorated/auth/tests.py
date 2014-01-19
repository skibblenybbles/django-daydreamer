from __future__ import unicode_literals

from django.conf import settings
from django.contrib import auth, messages

from daydreamer.views.decorated import auth as auth_decorated

from . import base


class LoginRequiredTestCase(base.TestCase):
    """
    Tests for the LoginRequired view decorator mixin.
    
    Note: for redirect tests, the target status code is ignored,
    becuase its value depends on how the root urlconf is set up.
    
    """
    view_class = auth_decorated.LoginRequired
    prefix = "login_required"
    
    def test_unauth(self):
        """
        With default settings, the response for an unauthenticated user
        should not have a message and should redirect according to
        the defaults.
        
        """
        path = self.unique_path()
        response = self.client.get(
            self.view(),
            path=path, follow=True)
        self.assertNoMessages(response)
        self.assertRedirects(
            response, settings.LOGIN_URL,
            query={auth.REDIRECT_FIELD_NAME: path},
            target_status_code=response.status_code)
    
    def test_unauth_raise(self):
        """
        With login_required_raise set to True, the response for an
        unauthenticated user should be 403.
        
        """
        path = self.unique_path()
        response = self.client.get(
            self.view({"raise": True}),
            path=path)
        self.assertEqual(response.status_code, 403)
    
    def test_unauth_exception(self):
        """
        With login_required_exception set to a custom exception, the
        response for an unauthenticated user should not raise the exception,
        and should redirect according to the defaults.
        
        """
        path = self.unique_path()
        class TestException(Exception):
            pass
        response = self.client.get(
            self.view({"exception": TestException(self.unique())}),
            path=path, follow=True)
        self.assertRedirects(
            response, settings.LOGIN_URL,
            query={auth.REDIRECT_FIELD_NAME: path},
            target_status_code=response.status_code)
    
    def test_unauth_raise_exception(self):
        """
        With login_required_exception set to a custom exception and
        login_required_raise set to True, the response for an
        unauthenticated user should raise the exception.
        
        """
        path = self.unique_path()
        class TestException(Exception):
            pass
        with self.assertRaises(TestException):
            self.client.get(
                self.view({
                    "raise": True,
                    "exception": TestException(self.unique())}),
                path=path)
    
    def test_unauth_message(self):
        """
        With login_required_message set to a custom message, the response
        for an unauthenticated user should have a message and should redirect
        according to the defaults.
        
        """
        path = self.unique_path()
        message = self.unique()
        response = self.client.get(
            self.view({"message": message}),
            path=path, follow=True)
        self.assertMessage(
            response, message, messages.WARNING, "warning", limit=1)
        self.assertRedirects(
            response, settings.LOGIN_URL,
            query={auth.REDIRECT_FIELD_NAME: path},
            target_status_code=response.status_code)
    
    def test_unauth_message_level(self):
        """
        With login_required_message_level set to a custom value, the response
        for an unauthenticated user should not have a message and should
        redirect according to the defaults.
        
        """
        path = self.unique_path()
        response = self.client.get(
            self.view({"message_level": messages.SUCCESS}),
            path=path, follow=True)
        self.assertNoMessages(response)
        self.assertRedirects(
            response, settings.LOGIN_URL,
            query={auth.REDIRECT_FIELD_NAME: path},
            target_status_code=response.status_code)
    
    def test_unauth_message_tags(self):
        """
        With login_required_message_tags set to a custom value, the response
        for an unauthenticated user should not have a message and should
        redirect according to the defaults.
        
        """
        path = self.unique_path()
        tags = self.unique()
        response = self.client.get(
            self.view({"message_tags": tags}),
            path=path, follow=True)
        self.assertNoMessages(response)
        self.assertRedirects(
            response, settings.LOGIN_URL,
            query={auth.REDIRECT_FIELD_NAME: path},
            target_status_code=response.status_code)
    
    def test_unauth_message_message_level(self):
        """
        With login_required_message set to a custom message and
        login_required_message_level set to a custom value, the response
        for an unauthenticated user should have a message and should redirect
        according to the defaults.
        
        """
        path = self.unique_path()
        message = self.unique()
        level = messages.SUCCESS
        response = self.client.get(
            self.view({"message": message, "message_level": level}),
            path=path, follow=True)
        self.assertMessage(
            response, message, level, "success", limit=1)
        self.assertRedirects(
            response, settings.LOGIN_URL,
            query={auth.REDIRECT_FIELD_NAME: path},
            target_status_code=response.status_code)
    
    def test_unauth_message_message_tags(self):
        """
        With login_required_message set to a custom message and
        login_required_message_tags set to a custom value, the response
        for an unauthenticated user should have a message and should redirect
        according to the defaults.
        
        """
        path = self.unique_path()
        message = self.unique()
        tags = " ".join((self.unique(), self.unique()))
        response = self.client.get(
            self.view({"message": message, "message_tags": tags}),
            path=path, follow=True)
        self.assertMessage(
            response, message, messages.WARNING, " ".join(("warning", tags)),
            limit=1)
        self.assertRedirects(
            response, settings.LOGIN_URL,
            query={auth.REDIRECT_FIELD_NAME: path},
            target_status_code=response.status_code)

    def test_unauth_message_redirect_url(self):
        """
        With login_required_redirect_url set to a custom value, the response
        for an unauthenticated user should redirect to the custom URL.
        
        """
        path = self.unique_path()
        redirect = self.unique_path()
        response = self.client.get(
            self.view({"redirect_url": redirect}),
            path=path, follow=True)
        self.assertRedirects(
            response, redirect,
            query={auth.REDIRECT_FIELD_NAME: path},
            target_status_code=response.status_code)
    
    def test_unauth_message_redirect_next_url(self):
        """
        With login_required_redirect_next_url set to a custom value, the
        response for an unauthenticated user should redirect with the custom
        query parameter value.
        
        """
        path = self.unique_path()
        next = self.unique_path()
        response = self.client.get(
            self.view({"redirect_next_url": next}),
            path=path, follow=True)
        self.assertRedirects(
            response, settings.LOGIN_URL,
            query={auth.REDIRECT_FIELD_NAME: next},
            target_status_code=response.status_code)
    
    def test_unauth_message_redirect_next_name(self):
        """
        With login_required_redirect_next_name set to a custom value, the
        response for an unauthenticated user should redirect with the custom
        query parameter name.
        
        """
        path = self.unique_path()
        name = self.unique()
        response = self.client.get(
            self.view({"redirect_next_name": name}),
            path=path, follow=True)
        self.assertRedirects(
            response, settings.LOGIN_URL,
            query={name: path},
            target_status_code=response.status_code)
    
    def test_unauth_message_no_redirect_next_name(self):
        """
        With login_required_redirect_next_name set to a falsy value, the
        response for an unauthenticated user should redirect without a
        query string.
        
        """
        path = self.unique_path()
        response = self.client.get(
            self.view({"redirect_next_name": None}),
            path=path, follow=True)
        self.assertRedirects(
            response, settings.LOGIN_URL,
            target_status_code=response.status_code)

















