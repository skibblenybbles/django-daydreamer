from __future__ import unicode_literals

from django.conf import settings
from django.utils import six

from django.contrib import auth, messages
from daydreamer.core import lang
from daydreamer.test import messages as test_messages, views as test_views


class TestCase(test_messages.TestCase, test_views.TestCase):
    """
    Common utilities for testing auth decorated views.
    
    Specify a view class to use for the test cases and a prefix to use
    for the prefixedattrs passed to self.view().
    
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
    def prefixed(self, prefix, data):
        """
        Returns a copy of the data dictionary with all its keys prefixed
        by prefix.
        
        """
        return dict(
            ("_".join((prefix, key)) if key else prefix, value)
            for key, value in six.iteritems(data))
    
    def view(self, prefixedattrs=None, staticattrs=None, **kwargs):
        """
        Mixes the specified attributes that should be prefixed into the static
        attributes dictionary and defers to super().
        
        """
        return super(TestCase, self).view(
            self.view_class, staticattrs=lang.updated(
                staticattrs or {},
                self.prefixed(self.prefix, prefixedattrs or {})),
            **kwargs)
    
    # Assertions.
    def assertViewResponse(self, path, setup, view_attrs, method="get",
            exception=None, ok=False, status_code=None,
            message=None, message_level=None, message_tags=None,
            redirect_url=None, redirect_next_url=None,
            redirect_next_name=None):
        """
        Sets up the environment with the setup callback and generates a view
        from setup()'s return and the provided view_attrs. Makes a request
        with the given HTTP method for the given path and makes a series of
        assertions about the response.
        
        If exception is specified, the view should raise the exception,
        and no other assertions will be performed.
        
        If ok is True, checks that the response's status code is 200 and
        that its content is "OK".
        
        If status code is specified, the response's status code must match.
        
        If message is specified, checks that no messages are present in the
        response's context. Otherwise, checks that exactly one message with the
        given message_level and message_tags is present in the response's
        context.
        
        If redirect_url is specified, checks that the response redirects to a
        URL which may have a query parameter specifying the next URL with the
        value of redirect_next_url and a name of redirect_next_name when
        the latter is specified.
        
        """
        if exception:
            # Raise an exception?
            with self.assertRaises(
                exception.__class__
                    if isinstance(exception, Exception)
                    else exception):
                getattr(self.client, method)(
                    self.view(lang.updated(view_attrs, setup())),
                    path=path)
        
        else:
            response = getattr(self.client, method)(
                self.view(lang.updated(view_attrs, setup())),
                path=path, follow=True)
            
            # Simple ok?
            if ok:
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, "OK")
            
            # Check status code?
            if status_code:
                self.assertEqual(response.status_code, status_code)
            
            # Contains a message?
            if message:
                self.assertMessage(
                    response, message, message_level, message_tags, limit=1)
            else:
                self.assertNoMessages(response)
            
            # Redirects?
            if redirect_url:
                # We don't care about the status code, because we're testing
                # outside of the URL resolution framework.
                self.assertRedirects(
                    response, redirect_url,
                    query={redirect_next_name: redirect_next_url}
                        if redirect_next_name
                        else None,
                    target_status_code=response.status_code)
    
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
        self.assertViewResponse(
            path, 
            setup_unauth_fail or self.setup_unauth_fail,
            {},
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
        self.assertViewResponse(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"raise": True},
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
        self.assertViewResponse(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"raise": True, "exception": exception},
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
        self.assertViewResponse(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"exception": exception},
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
        self.assertViewResponse(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"message": message},
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
        self.assertViewResponse(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"message": message, "message_level": level},
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
        self.assertViewResponse(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"message": message, "message_tags": tags},
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
        self.assertViewResponse(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"message_level": messages.SUCCESS},
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
        self.assertViewResponse(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"message_tags": tags},
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
        self.assertViewResponse(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"redirect_url": redirect},
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
        self.assertViewResponse(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"redirect_next_url": next},
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
        self.assertViewResponse(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"redirect_next_name": name},
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
        self.assertViewResponse(
            path,
            setup_unauth_fail or self.setup_unauth_fail,
            {"redirect_next_name": None},
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
        self.assertViewResponse(
            path, 
            setup_unauth_fail or self.setup_unauth_fail,
            {},
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
        self.assertViewResponse(
            path, 
            setup_auth_fail or self.setup_auth_fail,
            {},
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
        self.assertViewResponse(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"raise": True},
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
        self.assertViewResponse(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"raise": True, "exception": exception},
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
        self.assertViewResponse(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"exception": exception},
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
        self.assertViewResponse(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"message": message},
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
        self.assertViewResponse(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"message": message, "message_level": level},
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
        self.assertViewResponse(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"message": message, "message_tags": tags},
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
        self.assertViewResponse(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"message_level": messages.SUCCESS},
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
        self.assertViewResponse(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"message_tags": tags},
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
        self.assertViewResponse(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"redirect_url": redirect},
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
        self.assertViewResponse(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"redirect_next_url": next},
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
        self.assertViewResponse(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"redirect_next_name": name},
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
        self.assertViewResponse(
            path,
            setup_auth_fail or self.setup_auth_fail,
            {"redirect_next_name": None},
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
        self.assertViewResponse(
            path, 
            setup_auth_fail or self.setup_auth_fail,
            {},
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
        self.assertViewResponse(
            self.unique_path(),
            setup_unauth_pass or self.setup_unauth_pass,
            {},
            ok=True)
    
    def test_unauth_pass_raise(self, setup_unauth_pass=None):
        """
        Check that <prefix>_raise is ignored for an unauthenticated user
        passing the test.
        
        Settings:
            <prefix>_raise=True
        
        A custom setup_unauth_pass callback may be provided to reuse this
        test method.
        
        """
        self.assertViewResponse(
            self.unique_path(),
            setup_unauth_pass or self.setup_unauth_pass,
            {"raise": True},
            ok=True)
    
    def test_unauth_pass_message(self, setup_unauth_pass=None):
        """
        Check that <prefix>_message is ignored for an unauthenticated user
        passing the test.
        
        Settings:
            <prefix>_message=<unique>
        
        A custom setup_unauth_pass callback may be provided to reuse this
        test method.
        
        """
        self.assertViewResponse(
            self.unique_path(),
            setup_unauth_pass or self.setup_unauth_pass,
            {"message": self.unique()},
            ok=True)
    
    def test_auth_pass_message(self, setup_auth_pass=None):
        """
        Check that <prefix>_message is ignored for an authenticated user
        passing the test.
        
        Settings:
            <prefix>_message=<unique>
        
        A custom setup_auth_pass callback may be provided to reuse this
        test method.
        
        """
        self.assertViewResponse(
            self.unique_path(),
            setup_auth_pass or self.setup_auth_pass,
            {"message": self.unique()},
            ok=True)
    
    def test_auth_pass(self, setup_auth_pass=None):
        """
        Check default behavior for an authenticated user passing the test.
        
        Settings:
            (defaults)
        
        A custom setup_auth_pass callback may be provided to reuse this
        test method.
        
        """
        self.assertViewResponse(
            self.unique_path(),
            setup_auth_pass or self.setup_auth_pass,
            {},
            ok=True)
    
    def test_auth_pass_raise(self, setup_auth_pass=None):
        """
        Check that <prefix>_raise is ignored for an authenticated user
        passing the test.
        
        Settings:
            <prefix>_raise=True
        
        A custom setup_auth_pass callback may be provided to reuse this
        test method.
        
        """
        self.assertViewResponse(
            self.unique_path(),
            setup_auth_pass or self.setup_auth_pass,
            {"raise": True},
            ok=True)
    
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
        self.assertViewResponse(
            self.unique_path(),
            setup_unauth_pass or self.setup_unauth_pass,
            {},
            method="post",
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
        self.assertViewResponse(
            self.unique_path(),
            setup_auth_pass or self.setup_auth_pass,
            {},
            method="post",
            status_code=405)