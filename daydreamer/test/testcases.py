from __future__ import unicode_literals

from daydreamer.core import lang

from . import context, cookies, headers, messages, redirects, requests


class TestCase(requests.TestCase, headers.TestCase, cookies.TestCase,
        context.TestCase, messages.TestCase, redirects.TestCase):
    """
    A test case that provides a variety of general testing features and an
    enhanced version of the base class' assertViewBehavior().
    
    """
    def assertViewBehavior(self, path, method="get",
            method_args=None, method_kwargs=None,
            request_includes=None, request_excludes=None, request_exact=None,
            headers_include=None, headers_exclude=None, headers_exact=None,
            cookies_include=None, cookies_exclude=None, cookies_exact=None,
            context_includes=None, context_excludes=None, context_exact=None,
            message=None, message_level=None, message_tags=None,
            message_limit=None,
            redirect_url=None, redirect_next_url=None,
            redirect_next_name=None, redirect_status_code=None,
            redirect_target_status_code=None,
            **kwargs):
        """
        Sends an HTTP request to the given path using the specified method.
        
        If method_args or method_kwargs is specified, their values will
        take precedence to allow for cooperative super() calls.
        
        If request_includes is specified, the request passed to the generated
        view must have the specified attributes after the view has been called.
        If exclude_response is specified, the request passed to the generated
        view must not have the specified attributes after the view has been
        called. If exact_response is specified, the request passed to the
        generated view must have the specified names and exact attribute values
        after the view has been called.
        
        If headers_include is specified, the response must contain the header
        name or names. If headers_exclude is specified, the response must not
        contain the header name or names. If headers_exact is specified, its
        names and exact values must be present in the response's headers.
        
        If cookies_include is specified, the response must contain the cookie
        name or names. If cookies_exclude is specified, the response must not
        contain the cookie name or names. If cookies_exact is specified, its
        names and exact values must be present in the response's cookies.
        
        If context_includes is specified, the response's context must contain
        the name or names. If context_excludes is specified, the response's
        context must not contain the name or names. If context_exact is
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
        if method_args is None or method_kwargs is None:
            method_args = (path,)
            method_kwargs = None
        
        # Set up the assertions.
        request_assertions = lang.updated(
            kwargs.pop("request_assertions", {}),
            dict(
                request_includes=request_includes,
                request_excludes=request_excludes,
                request_exact=request_exact),
            copy=True)
        
        response_assertions = lang.updated(
            kwargs.pop("response_assertions", {}),
            dict(
                headers_include=headers_include,
                headers_exclude=headers_exclude,
                headers_exact=headers_exact,
                cookies_include=cookies_include,
                cookies_exclude=cookies_exclude,
                cookies_exact=cookies_exact,
                context_includes=context_includes,
                context_excludes=context_excludes,
                context_exact=context_exact,
                message=message,
                message_level=message_level,
                message_tags=message_tags,
                message_limit=message_limit,
                redirect_url=redirect_url,
                redirect_next_url=redirect_next_url,
                redirect_next_name=redirect_next_name,
                redirect_status_code=redirect_status_code,
                redirect_target_status_code=redirect_target_status_code),
            copy=True)
        
        return super(TestCase, self).assertViewBehavior(
            method=method, method_args=method_args,
            method_kwargs=method_kwargs,
            request_assertions=request_assertions,
            response_assertions=response_assertions,
            **kwargs)
