from __future__ import unicode_literals

import collections

from django.utils import six

from daydreamer.core import lang
from daydreamer.test import messages as test_messages, views as test_views


class TestCase(test_messages.TestCase, test_views.TestCase):
    """
    Common utilities for testing base views.
    
    Specify a view class to use for the test cases.
    
    """
    view_class = None
    
    # Utilities.
    def view(self, *args, **kwargs):
        """
        Hardcodes self.view_class.
        
        """
        return super(TestCase, self).view(self.view_class, *args, **kwargs)
    
    # Assertions.
    def assertResponseBehavior(self, path,
            setup=None, view_attrs=None, view_kwargs=None, method="get",
            exception=None, status_code=None, follow_status_code=False,
            content=None, headers=None,
            message=None, message_level=None, message_tags=None,
            redirect_url=None, redirect_next_url=None,
            redirect_next_name=None):
        """
        Sets up the environment with the optional setup callback and generates
        a view from setup()'s return and the optional attributes. Makes an
        HTTP request for the specified method and path and makes a series of
        assertions about the response behavior.
        
        If exception is specified, the view should raise the exception,
        and no other assertions will be performed.
        
        If status code is specified, the response's status code must match.
        
        If follow_status_code is specified, a redirected response's status
        code must match. Typically, this will be None while bypassing the URL
        resolution framework.
        
        If content is specified, the response's content must match.
        
        If headers is specified, its names and values must be present in the
        response's headers.
        
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
            # Expecting an exception.
            with self.assertRaises(
                exception.__class__
                    if isinstance(exception, Exception)
                    else exception):
                getattr(self.client, method)(
                    self.view(
                        lang.updated(
                            view_attrs or {},
                            setup() or {}
                                if isinstance(setup, collections.Callable)
                                else {}),
                        **view_kwargs or {}),
                    path=path)
        
        else:
            # Expecting a normal response.
            response = getattr(self.client, method)(
                self.view(
                    lang.updated(
                        view_attrs or {},
                        setup() or {}
                            if isinstance(setup, collections.Callable)
                            else {}),
                    **view_kwargs or {}),
                path=path)
            
            # Check status code?
            if status_code:
                self.assertEqual(response.status_code, status_code)
            
            # Check content?
            if content:
                self.assertEqual(response.content, content)
            
            # Check headers?
            if headers:
                for name, value in six.iteritems(
                    headers
                        if isinstance(headers, collections.Mapping)
                        else dict(headers)):
                    self.assertIn(name, response)
                    self.assertEqual(response[name], value)
            
            # Contains a message?
            if message:
                self.assertMessage(
                    response, message, message_level, message_tags, limit=1)
            else:
                self.assertNoMessages(response)
            
            # Redirects?
            if redirect_url:
                self.assertRedirects(
                    response, redirect_url,
                    query={redirect_next_name: redirect_next_url}
                        if redirect_next_name
                        else None,
                    target_status_code=
                        follow_status_code or response.status_code)
