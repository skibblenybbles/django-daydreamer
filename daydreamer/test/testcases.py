from __future__ import unicode_literals

from daydreamer.core import lang

from . import context, cookies, headers, messages, redirects, requests


class TestCase(requests.TestCase, headers.TestCase, cookies.TestCase,
        context.TestCase, messages.TestCase, redirects.TestCase):
    """
    A test case that provides a variety of general testing features and an
    enhanced version of the base class' assertViewBehavior().
    
    """
    def assertViewBehavior(self,
            path="/", method="get", method_args=None, method_kwargs=None,
            data=None, follow=False, headers=None,
            setup=None, repeat=None, exception=None,
            status_code=None, content=None,
            include_request=None, exclude_request=None, exact_request=None,
            include_headers=None, exclude_headers=None, exact_headers=None,
            include_cookies=None, exclude_cookies=None, exact_cookies=None,
            include_context=None, exclude_context=None, exact_context=None,
            message=None, message_level=None, message_tags=None,
            message_limit=None,
            redirect_url=None, redirect_next_url=None,
            redirect_next_name=None, redirect_status_code=None,
            redirect_target_status_code=None,
            method_assertions=None,
            request_assertions=None,
            response_assertions=None,
            **kwargs):
        """
        Sends an HTTP request to the given path using the specified method.
        
        If method_args or method_kwargs is specified, their values will
        take precedence to allow for cooperative super() calls.
        
        If include_request is specified, the request passed to the generated
        view must have the specified attributes after the view has been called.
        If exclude_response is specified, the request passed to the generated
        view must not have the specified attributes after the view has been
        called. If exact_response is specified, the request passed to the
        generated view must have the specified names and exact attribute values
        after the view has been called.
        
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
        
        If message is specified, checks that a message with the given message
        level and tags is present in the response's context, optionally
        checking that message limit count. Otherwise, checks that no messages
        are present in the response's context.
        
        If redirect_url is specified, checks that the response redirects to a
        URL which may have a query parameter specifying the next URL with the
        value of redirect_next_url and a name of redirect_next_name when
        the both are specified. The redirect status code and the target status
        will also be checked if specified.
        
        See daydreamer.test.base.TestCase.assertViewBehavior for documentation
        of the other arguments.
        
        """
        # Use the passed method arguments and keyword arguments or
        # generate them?
        if method_args is None and method_kwargs is None:
            method_args = (path,)
        
        # Set up the assertions.
        request_assertions = lang.updated(
            request_assertions or {},
            dict(
                include_request=include_request,
                exclude_request=exclude_request,
                exact_request=exact_request),
            copy=bool(request_assertions))
        
        response_assertions = lang.updated(
            response_assertions or {},
            dict(
                include_headers=include_headers,
                exclude_headers=exclude_headers,
                exact_headers=exact_headers,
                include_cookies=include_cookies,
                exclude_cookies=exclude_cookies,
                exact_cookies=exact_cookies,
                include_context=include_context,
                exclude_context=exclude_context,
                exact_context=exact_context,
                message=message,
                message_level=message_level,
                message_tags=message_tags,
                message_limit=message_limit,
                redirect_url=redirect_url,
                redirect_next_url=redirect_next_url,
                redirect_next_name=redirect_next_name,
                redirect_status_code=redirect_status_code,
                redirect_target_status_code=redirect_target_status_code),
            copy=bool(response_assertions))
        
        return super(TestCase, self).assertViewBehavior(
            method=method, method_args=method_args,
            method_kwargs=method_kwargs,
            data=data, follow=follow, headers=headers,
            setup=setup, repeat=repeat,
            exception=exception, status_code=status_code, content=content,
            method_assertions=method_assertions,
            request_assertions=request_assertions,
            response_assertions=response_assertions,
            **kwargs)
