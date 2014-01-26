from __future__ import unicode_literals

import collections
import functools
import sys

from django.utils import six
from django.utils.decorators import available_attrs

from daydreamer.core import lang
from daydreamer.test.views import generic, messages


class TestCase(messages.TestCase, generic.TestCase):
    """
    Common utilities for testing view classes.
    
    Specify view class(es) to inherit from for the test cases.
    
    """
    view_classes = None
    
    # Utilities.
    def view(self, **attrs):
        """
        Hardcodes self.view_classes as the first argument.
        
        """
        return super(TestCase, self).view(self.view_classes, **attrs)
    
    # Assertions.
    def assertViewBehavior(self,
            attrs=None, setup=None, view_args=None, view_kwargs=None,
            method="get", path=None, data=None, headers=None, repeat=None,
            exception=None,
            status_code=None, follow_status_code=None, content=None,
            include_headers=None, exclude_headers=None, exact_headers=None,
            include_cookies=None, exclude_cookies=None, exact_cookies=None,
            include_context=None, exclude_context=None, exact_context=None,
            include_request_attrs=None, exclude_request_attrs=None,
                exact_request_attrs=None,
            include_view_attrs=None, exclude_view_attrs=None,
                exact_view_attrs=None,
            message=None, message_level=None, message_tags=None,
            redirect_url=None, redirect_next_url=None,
                redirect_next_name=None):
        """
        Generates a view from the optional attributes and from the setup()
        callback's return value. Makes an HTTP request for the specified
        method and path, with optional request, data or headers, passing the
        optional view arguments and keyword arguments. Makes a series of
        assertions about the response behavior.
        
        If the setup callback is specified, it should set up the test
        environment and return an optional dictionary of attributes to mix
        into the creatd view class instance.
        
        If path is specified, usees the path for the request. Otherwise
        generates a unique path to user for the request.
        
        If data is specified, it should be a dictionary for a "get", "post"
        or "head" request. Otherwise, it should be a string.
        
        If header is specified, it should be a dictionary with header
        values for the request.
        
        If repeat is specified, it should indicate the number of times to
        repeat the request. Each call will be wrapped in an exception handler
        until the last call, which will be processed by the assertions.
        
        If exception is specified, the view should raise the exception,
        and no other assertions will be performed.
        
        If status code is specified, the response's status code must match.
        
        If follow_status_code is specified, a redirected response's status
        code must match. Typically, this will be None while bypassing the URL
        resolution framework.
        
        If content is specified, the response's content must match.
        
        If include_headers is specified, the response must contain the header
        name or names. If exclude_headers is specified, the response must not
        contain the header name or names. If exact_headers is specified, its
        names and exact values must be present in the response's headers.
        
        If include_cookies is specified, the response must contain the cookie
        name or names. If exclude_cookies is specified, the response must not
        contain the cookie name or names. If exact_cookies is specified, its
        names and exact values must be present in the response's cookies.
        
        If include_context is specified, the response's context must contain
        the name or names. If exclude_context is specified, the response's
        context must not contain the name or names. If exact_context is
        specified, the names and exact values must be present in the response's
        context.
        
        If include_request_attrs is specified, the request passed to the
        generated view must have the specified attributes after the view has
        been called. If exclude_response_attrs is specified, the request
        passed to the generated view must not have the specified attributes
        after the view has been called. If exact_response_attrs is specified,
        the request passed to the generated view must have the specified names
        and exact attribute values after the view has been called.
        
        If include_view_attrs is specified, the generated view function must
        have the specified attributes after it has been called. If
        exclude_view_attrs is specified, the generated view function must not
        have the specified attributes after the view has been called. If
        exact_view_attrs is specified, the generated view function must have
        the specified names and exact attribute values after the view has
        been called.
        
        If message is not specified, checks that no messages are present in the
        response's context. Otherwise, checks that exactly one message with the
        given message_level and message_tags is present in the response's
        context.
        
        If redirect_url is specified, checks that the response redirects to a
        URL which may have a query parameter specifying the next URL with the
        value of redirect_next_url and a name of redirect_next_name when
        the latter is specified.
        
        """
        # Sanity check and normalize the arguments.
        attrs = attrs or {}
        view_args = view_args or ()
        view_kwargs = view_kwargs or {}
        path = self.unique_path() if path is None else path
        if data is not None:
            if method in ("get", "post", "head",):
                if not isinstance(data, collections.Mapping):
                    raise ValueError(
                        'The data must be a dictionary for "get", "post" or '
                        '"head" requests.')
            else:
                if not isinstance(data, six.string_types):
                    raise ValueError(
                        "The data must be a string for request methods other "
                        'than "get", "post" or "head".')
        else:
            data = {} if method in ("get", "post", "head",) else ""
        headers = headers or {}
        repeat = repeat or 0
        include_headers = (
            (include_headers,)
                if isinstance(include_headers, six.string_types)
                else include_headers or ())
        exclude_headers = (
            (exclude_headers,)
                if isinstance(exclude_headers, six.string_types)
                else exclude_headers or ())
        exact_headers = (
            exact_headers
                if isinstance(exact_headers, collections.Mapping)
                else dict(exact_headers or {}))
        
        include_cookies = (
            (include_cookies,)
                if isinstance(include_cookies, six.string_types)
                else include_cookies or ())
        exclude_cookies = (
            (exclude_cookies,)
                if isinstance(exclude_cookies, six.string_types)
                else exclude_cookies or ())
        exact_cookies = (
            exact_cookies
                if isinstance(exact_context, collections.Mapping)
                else dict(exact_cookies or {}))
        
        include_context = (
            (include_context,)
                if isinstance(include_context, six.string_types)
                else include_context or ())
        exclude_context = (
            (exclude_context,)
                if isinstance(exclude_context, six.string_types)
                else exclude_context or ())
        exact_context = (
            exact_context
                if isinstance(exact_context, collections.Mapping)
                else dict(exact_context or {}))
        
        include_view_attrs = (
            (include_view_attrs,)
                if isinstance(include_view_attrs, six.string_types)
                else include_view_attrs or ())
        exclude_view_attrs = (
            (exclude_view_attrs,)
                if isinstance(exclude_view_attrs, six.string_types)
                else exclude_view_attrs or ())
        exact_view_attrs = (
            exact_view_attrs
                if isinstance(exact_view_attrs, collections.Mapping)
                else dict(exact_view_attrs or {}))
        
        include_request_attrs = (
            (include_request_attrs,)
                if isinstance(include_request_attrs, six.string_types)
                else include_request_attrs or ())
        exclude_request_attrs = (
            (exclude_request_attrs,)
                if isinstance(exclude_request_attrs, six.string_types)
                else exclude_request_attrs or ())
        exact_request_attrs = (
            exact_request_attrs
                if isinstance(exact_request_attrs, collections.Mapping)
                else dict(exact_request_attrs or {}))
        
        # Create the view function, wrapping it in a closure so we can extract
        # the passed request argument.
        closure = {}
        _view = self.view(
            **lang.updated(
                attrs,
                setup() or {}
                    if isinstance(setup, collections.Callable)
                    else {}))
        @functools.wraps(_view, assigned=available_attrs(_view))
        def view(request, *args, **kwargs):
            closure["request"] = request
            return _view(request, *args, **kwargs)
        
        # Set up a closure to call the view.
        def respond():
            return getattr(self.client, method)(
                view, view_args, view_kwargs, path=path, data=data, **headers)
        
        # Burn through the repetions?
        while repeat > 1:
            try:
                respond()
            except SystemExit:
                six.reraise(*sys.exc_info())
            except:
                pass
            repeat -= 1
        
        # Do we expect an exception or a normal response?
        if exception:
            # Expecting an exception.
            with self.assertRaises(
                exception.__class__
                    if isinstance(exception, Exception)
                    else exception):
                respond()
        else:
            # Expecting a normal response.
            response = respond()
            
            # Get the request.
            request = closure.get("request", None)
            
            # Check status code?
            if status_code is not None:
                self.assertEqual(response.status_code, status_code)
            
            # Check content?
            if content is not None:
                self.assertEqual(response.content, content)
            
            # Check headers.
            for name in include_headers:
                self.assertIn(name, response)
            for name in exclude_headers:
                self.assertNotIn(name, response)
            for name, value in six.iteritems(exact_headers):
                self.assertIn(name, response)
                self.assertEqual(response[name], value)
            
            # Check cookies.
            for name in include_cookies:
                self.assertIn(name, response.cookies)
            for name in exclude_cookies:
                self.assertNotIn(name, response.cookies)
            for name, value in six.iteritems(exact_cookies):
                self.assertIn(name, response.cookies)
                self.assertEqual(response.cookies[name].value, value)
            
            # Check context.
            if include_context:
                self.assertTrue(
                    hasattr(response, "context") and response.context,
                    "The response must have a context attribute that is "
                    "not None.")
                for name in include_context:
                    self.assertIn(name, response.context)
            if exclude_context:
                if hasattr(response, "context") and response.context:
                    for name in exclude_context:
                        self.assertNotIn(name, response.context)
            if exact_context:
                self.assertTrue(
                    hasattr(response, "context") and response.context,
                    "The response must have a context attribute that is "
                    "not None.")
                for name, value in six.iteritems(exact_context):
                    self.assertIn(name, response.context)
                    self.assertEqual(response.context[name], value)
            
            # Check request attributes.
            self.assertTrue(
                request or not any((
                    include_request_attrs,
                    exclude_request_attrs,
                    exact_request_attrs)))
            for name in include_request_attrs:
                self.assertTrue(hasattr(request, name))
            for name in exclude_request_attrs:
                self.assertTrue(not hasattr(request, name))
            for name, value in six.iteritems(exact_request_attrs):
                self.assertTrue(hasattr(request, name))
                self.assertEqual(getattr(request, name), value)
            
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
