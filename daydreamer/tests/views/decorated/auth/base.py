from __future__ import unicode_literals

from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes import models as type_models
from django.utils import six

from daydreamer.tests.views.generic import base


class TestCase(base.TestCase):
    """
    Common utilities for testing authentication view decorator mixins.
    
    Specify a view class to use for the test cases and a prefix to use
    for the attributes passed to self.view().
    
    You must also provide overrides for the four setup_*() methods.
    
    """
    view_class = None
    prefix = None
    
    # Test environment setups.
    def setup_unauth_fail(self):
        """
        Sets up an unauthenticated user and returns view attributes that should
        cause the user to fail the test.
        
        Subclasses must implement this.
        
        """
        raise NotImplementedError
    
    def setup_auth_fail(self):
        """
        Sets up an authenticated user and returns view attributes that should
        cause the user to fail the test.
        
        Subclasses must implement this.
        
        """
        raise NotImplementedError
    
    def setup_unauth_pass(self):
        """
        Sets up an unauthenticated user and returns view attributes that should
        cause the user to pass the test.
        
        Subclasses must implement this.
        
        """
        raise NotImplementedError
    
    def setup_auth_pass(self):
        """
        Sets up an authenticated user and returns view attributes that should
        cause the user to pass the test.
        
        Subclasses must implement this.
        
        """
        raise NotImplementedError
    
    # Utilities.
    def unique_username(self):
        """
        Create a unique string appropriate for a username.
        
        """
        return self.unique()[:30]
    
    def unique_group(self):
        """
        Create a unique string appropriate for a group.
        
        """
        return self.unique()[:80]
    
    def unique_permission(self):
        """
        Create a unique string appropriate for a permission.
        
        """
        return self.unique()[:100]
    
    def create_authenticated_user(self, **attrs):
        """
        Creates a user with a unique username and password, sets the specified
        attributes on the user and logs in. Returns the new,
        authenticated user.
        
        """
        username = self.unique_username()
        password = self.unique()
        user = auth.get_user_model().objects.create_user(username, password=password)
        if attrs:
            for name, value in six.iteritems(attrs):
                setattr(user, name, value)
            user.save()
        self.client.login(username=username, password=password)
        return user
    
    def create_group(self):
        """
        Creates a group with a unique name and returns it.
        
        """
        return auth_models.Group.objects.create(name=self.unique_group())
    
    def create_permission(self):
        """
        Creates a permission on the User model with a unique codename and
        returns it.
        
        """
        return auth_models.Permission.objects.create(
            content_type=type_models.ContentType.objects.get_for_model(
                auth.get_user_model()),
            codename=self.unique_permission())
    
    def view(self, attrs=None, *args, **kwargs):
        """
        Hardcodes self.view_class and adds self.prefix to all of the attributes.
        
        """
        return super(TestCase, self).view(
            attrs={
                "_".join((self.prefix, key)) if key else self.prefix: value
                for key, value in six.iteritems(attrs or {})},
            *args, **kwargs)
    
    # Common tests.
    def test_unauth_fail(self, setup_unauth_fail=None):
        """
        Check default behavior for an unauthenticated user failing the test.
        
        Settings:
            (defaults)
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_unauth_fail_raise(self, setup_unauth_fail=None):
        """
        Check exception raising behavior for an unauthenticated user failing
        the test.
        
        Settings:
            <prefix>_raise=True
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"raise": True},
            {"get": self.unique()},
            status_code=403)
    
    def test_unauth_fail_raise_exception(self, setup_unauth_fail=None):
        """
        Check custom exception exception raising behavior for an
        unauthenticated user failing the test.
        
        Settings:
            <prefix>_raise=True
            <prefix>_exception=<unique>
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        class TestException(Exception):
            pass
        path = self.unique_path()
        exception = TestException(self.unique())
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"raise": True, "exception": exception},
            {"get": self.unique()},
            exception=exception)
    
    def test_unauth_fail_exception(self, setup_unauth_fail=None):
        """
        Check that exception raising behavior is controlled by <prefix>_raise,
        not by a coupling error with <prefix>_exception for an unauthenticated
        user failing the test.
        
        Settings:
            <prefix>_exception=<unique>
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        class TestException(Exception):
            pass
        path = self.unique_path()
        exception = TestException(self.unique())
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"exception": exception},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_unauth_fail_message(self, setup_unauth_fail=None):
        """
        Check message enqueuing behavior for an unauthenticated user failing
        the test.
        
        Settings:
            <prefix>_message=<unique>
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        message = self.unique()
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"message": message},
            {"get": self.unique()},
            message=message,
            message_level=messages.WARNING,
            message_tags="warning",
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_unauth_fail_message_message_level(self, setup_unauth_fail=None):
        """
        Check message enqueuing behavior with a custom message level for an
        unauthenticated user failing the test.
        
        Settings:
            <prefix>_message=<unique>
            <prefix>_message_level=messages.SUCCESS
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        message = self.unique()
        level = messages.SUCCESS
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"message": message, "message_level": level},
            {"get": self.unique()},
            message=message,
            message_level=level,
            message_tags="success",
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_unauth_fail_message_message_tags(self, setup_unauth_fail=None):
        """
        Check message enqueuing behavior with custom message tags for an
        unauthenticated user failing the test.
        
        Settings:
            <prefix>_message=<unique>
            <prefix>_message_tags=<unique>
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        message = self.unique()
        tags = " ".join((self.unique(), self.unique()))
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"message": message, "message_tags": tags},
            {"get": self.unique()},
            message=message,
            message_level=messages.WARNING,
            message_tags=" ".join(("warning", tags,)),
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_unauth_fail_message_level(self, setup_unauth_fail=None):
        """
        Check that message enqueuing behavior is controlled by
        <prefix>_message, not by a coupling error with <prefix>_message_level
        for an unauthenticated user failing the test.
        
        Settings:
            <prefix>_message_level=<unique>
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"message_level": messages.SUCCESS},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_unauth_fail_message_tags(self, setup_unauth_fail=None):
        """
        Check that message enqueuing behavior is controlled by
        <prefix>_message, not by a coupling error with <prefix>_message_tags
        for an unauthenticated user failing the test.
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        tags = " ".join((self.unique(), self.unique(),))
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"message_tags": tags},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)

    def test_unauth_fail_redirect_url(self, setup_unauth_fail=None):
        """
        Check redirect behavior to a custom URL for an unauthenticated user
        failing the test.
        
        Settings:
            <prefix>_redirect_url=<unique>
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        redirect = self.unique_path()
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"redirect_url": redirect},
            {"get": self.unique()},
            redirect_url=redirect,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_unauth_fail_redirect_next_url(self, setup_unauth_fail=None):
        """
        Check redirect behavior with a custom next URL query parameter value
        for an unauthenticated user failing the test.
        
        Settings:
            <prefix>_redirect_next_url=<unique>
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        next = self.unique_path()
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"redirect_next_url": next},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=next,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_unauth_fail_redirect_next_name(self, setup_unauth_fail=None):
        """
        Check redirect behavior with a custom next URL query parameter name
        for an unauthenticated user failing the test.
        
        Settings:
            <prefix>_redirect_next_name=<unique>
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        name = self.unique()
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"redirect_next_name": name},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=name)
    
    def test_unauth_fail_no_redirect_next_name(self, setup_unauth_fail=None):
        """
        Check redirect behavior with no return query parameter name for an
        unauthenticated user failing the test.
        
        Settings:
            <prefix>_redirect_next_name=None
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        self.assertResponseBehavior(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"redirect_next_name": None},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL)
    
    def test_unauth_fail_precedence(self, setup_unauth_fail=None):
        """
        Check that the view decorator mixin's behavior takes precedence when
        using an unsupported HTTP method for an unauthenticated user failing
        the test.
        
        Settings:
            (defaults)
        
        A custom setup_unauth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        self.assertResponseBehavior(
            path, 
            setup_unauth_fail or self.setup_unauth_fail,
            {},
            {"get": self.unique()},
            method="post",
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_auth_fail(self, setup_auth_fail=None):
        """
        Check default behavior for an authenticated user failing the test.
        
        Settings:
            (defaults)
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        self.assertResponseBehavior(
            path, 
            setup_auth_fail or self.setup_auth_fail,
            {},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_auth_fail_raise(self, setup_auth_fail=None):
        """
        Check exception raising behavior for an authenticated user failing
        the test.
        
        Settings:
            <prefix>_raise=True
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        self.assertResponseBehavior(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"raise": True},
            {"get": self.unique()},
            status_code=403)
    
    def test_auth_fail_raise_exception(self, setup_auth_fail=None):
        """
        Check custom exception exception raising behavior for an
        authenticated user failing the test.
        
        Settings:
            <prefix>_raise=True
            <prefix>_exception=<unique>
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        class TestException(Exception):
            pass
        path = self.unique_path()
        exception = TestException(self.unique())
        self.assertResponseBehavior(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"raise": True, "exception": exception},
            {"get": self.unique()},
            exception=exception)
    
    def test_auth_fail_exception(self, setup_auth_fail=None):
        """
        Check that exception raising behavior is controlled by <prefix>_raise,
        not by a coupling error with <prefix>_exception for an authenticated
        user failing the test.
        
        Settings:
            <prefix>_exception=<unique>
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        class TestException(Exception):
            pass
        path = self.unique_path()
        exception = TestException(self.unique())
        self.assertResponseBehavior(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"exception": exception},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_auth_fail_message(self, setup_auth_fail=None):
        """
        Check message enqueuing behavior for an authenticated user failing
        the test.
        
        Settings:
            <prefix>_message=<unique>
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        message = self.unique()
        self.assertResponseBehavior(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"message": message},
            {"get": self.unique()},
            message=message,
            message_level=messages.WARNING,
            message_tags="warning",
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_auth_fail_message_message_level(self, setup_auth_fail=None):
        """
        Check message enqueuing behavior with a custom message level for an
        authenticated user failing the test.
        
        Settings:
            <prefix>_message=<unique>
            <prefix>_message_level=messages.SUCCESS
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        message = self.unique()
        level = messages.SUCCESS
        self.assertResponseBehavior(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"message": message, "message_level": level},
            {"get": self.unique()},
            message=message,
            message_level=level,
            message_tags="success",
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_auth_fail_message_message_tags(self, setup_auth_fail=None):
        """
        Check message enqueuing behavior with custom message tags for an
        authenticated user failing the test.
        
        Settings:
            <prefix>_message=<unique>
            <prefix>_message_tags=<unique>
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        message = self.unique()
        tags = " ".join((self.unique(), self.unique()))
        self.assertResponseBehavior(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"message": message, "message_tags": tags},
            {"get": self.unique()},
            message=message,
            message_level=messages.WARNING,
            message_tags=" ".join(("warning", tags,)),
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_auth_fail_message_level(self, setup_auth_fail=None):
        """
        Check that message enqueuing behavior is controlled by
        <prefix>_message, not by a coupling error with <prefix>_message_level
        for an authenticated user failing the test.
        
        Settings:
            <prefix>_message_level=<unique>
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        self.assertResponseBehavior(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"message_level": messages.SUCCESS},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_auth_fail_message_tags(self, setup_auth_fail=None):
        """
        Check that message enqueuing behavior is controlled by
        <prefix>_message, not by a coupling error with <prefix>_message_tags
        for an authenticated user failing the test.
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        tags = " ".join((self.unique(), self.unique(),))
        self.assertResponseBehavior(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"message_tags": tags},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_auth_fail_redirect_url(self, setup_auth_fail=None):
        """
        Check redirect behavior to a custom URL for an authenticated user
        failing the test.
        
        Settings:
            <prefix>_redirect_url=<unique>
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        redirect = self.unique_path()
        self.assertResponseBehavior(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"redirect_url": redirect},
            {"get": self.unique()},
            redirect_url=redirect,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_auth_fail_redirect_next_url(self, setup_auth_fail=None):
        """
        Check redirect behavior with a custom next URL query parameter value
        for an authenticated user failing the test.
        
        Settings:
            <prefix>_redirect_next_url=<unique>
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        next = self.unique_path()
        self.assertResponseBehavior(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"redirect_next_url": next},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=next,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_auth_fail_redirect_next_name(self, setup_auth_fail=None):
        """
        Check redirect behavior with a custom next URL query parameter name
        for an authenticated user failing the test.
        
        Settings:
            <prefix>_redirect_next_name=<unique>
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        name = self.unique()
        self.assertResponseBehavior(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"redirect_next_name": name},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=name)
    
    def test_auth_fail_no_redirect_next_name(self, setup_auth_fail=None):
        """
        Check redirect behavior with no return query parameter name for an
        authenticated user failing the test.
        
        Settings:
            <prefix>_redirect_next_name=None
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        self.assertResponseBehavior(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"redirect_next_name": None},
            {"get": self.unique()},
            redirect_url=settings.LOGIN_URL)
    
    def test_auth_fail_precedence(self, setup_auth_fail=None):
        """
        Check that the view decorator mixin's behavior takes precedence when
        using an unsupported HTTP method for an authenticated user failing
        the test.
        
        Settings:
            (defaults)
        
        A custom setup_auth_fail callback may be provided to reuse this
        test method.
        
        """
        path = self.unique_path()
        self.assertResponseBehavior(
            path, 
            setup_auth_fail or self.setup_auth_fail,
            {},
            {"get": self.unique()},
            method="post",
            redirect_url=settings.LOGIN_URL,
            redirect_next_url=path,
            redirect_next_name=auth.REDIRECT_FIELD_NAME)
    
    def test_unauth_pass(self, setup_unauth_pass=None):
        """
        Check default behavior for an unauthenticated user passing the test.
        
        Settings:
            (defaults)
        
        A custom setup_unauth_pass callback may be provided to reuse this
        test method.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            self.unique_path(),
            setup_unauth_pass or self.setup_unauth_pass,
            {},
            {"get": content},
            status_code=200,
            content=content)
    
    def test_unauth_pass_raise(self, setup_unauth_pass=None):
        """
        Check that <prefix>_raise is ignored for an unauthenticated user
        passing the test.
        
        Settings:
            <prefix>_raise=True
        
        A custom setup_unauth_pass callback may be provided to reuse this
        test method.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            self.unique_path(),
            setup_unauth_pass or self.setup_unauth_pass,
            {"raise": True},
            {"get": content},
            status_code=200,
            content=content)
    
    def test_unauth_pass_message(self, setup_unauth_pass=None):
        """
        Check that <prefix>_message is ignored for an unauthenticated user
        passing the test.
        
        Settings:
            <prefix>_message=<unique>
        
        A custom setup_unauth_pass callback may be provided to reuse this
        test method.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            self.unique_path(),
            setup_unauth_pass or self.setup_unauth_pass,
            {"message": self.unique()},
            {"get": content},
            status_code=200,
            content=content)
    
    def test_auth_pass_message(self, setup_auth_pass=None):
        """
        Check that <prefix>_message is ignored for an authenticated user
        passing the test.
        
        Settings:
            <prefix>_message=<unique>
        
        A custom setup_auth_pass callback may be provided to reuse this
        test method.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            self.unique_path(),
            setup_auth_pass or self.setup_auth_pass,
            {"message": self.unique()},
            {"get": content},
            status_code=200,
            content=content)
    
    def test_auth_pass(self, setup_auth_pass=None):
        """
        Check default behavior for an authenticated user passing the test.
        
        Settings:
            (defaults)
        
        A custom setup_auth_pass callback may be provided to reuse this
        test method.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            self.unique_path(),
            setup_auth_pass or self.setup_auth_pass,
            {},
            {"get": content},
            status_code=200,
            content=content)
    
    def test_auth_pass_raise(self, setup_auth_pass=None):
        """
        Check that <prefix>_raise is ignored for an authenticated user
        passing the test.
        
        Settings:
            <prefix>_raise=True
        
        A custom setup_auth_pass callback may be provided to reuse this
        test method.
        
        """
        content=self.unique()
        self.assertResponseBehavior(
            self.unique_path(),
            setup_auth_pass or self.setup_auth_pass,
            {"raise": True},
            {"get": content},
            status_code=200,
            content=content)
    
    def test_unauth_pass_precedence(self, setup_unauth_pass=None):
        """
        Check that the behavior of the base view class takes precedence
        when using an unsupported HTTP method for an unauthenticated user
        passing the test.
        
        Settings:
            (defaults)
        
        A custom setup_unauth_pass callback may be provided to reuse this
        test method.
        
        """
        self.assertResponseBehavior(
            self.unique_path(),
            setup_unauth_pass or self.setup_unauth_pass,
            status_code=405)
    
    def test_auth_pass_precedence(self, setup_auth_pass=None):
        """
        Check that the behavior of the base view class takes precedence
        when using an unsupported HTTP method for an authenticated user
        passing the test.
        
        Settings:
            (defaults)
        
        A custom setup_auth_pass callback may be provided to reuse this
        test method.
        
        """
        self.assertResponseBehavior(
            self.unique_path(),
            setup_auth_pass or self.setup_auth_pass,
            status_code=405)
