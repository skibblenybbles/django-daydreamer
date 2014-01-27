from __future__ import unicode_literals

from daydreamer.core import lang

from .. import testcases
from . import redirects, views


class TestCase(views.TestCase, redirects.TestCase, testcases.TestCase):
    """
    A test case that provides a variety of general testing features and an
    enhanced version of the base class' assertViewBehavior().
    
    """
    # Utilities.
    def unique_path(self):
        """
        Returns a unique path for use in testing views.
        
        While operating outside of the URL resolution framework, this should be
        used to generate a path to pass to the client to verify that a view's
        behavior is independent of the request's path.
        
        """
        return "/{unique:s}/".format(unique=self.unique())
    
    # Assertions.
    def assertViewBehavior(self,
            view, view_args=None, view_kwargs=None,
            path=None, method="get", method_args=None, method_kwargs=None,
            data=None, follow=False, headers=None,
            setup=None, repeat=None, exception=None,
            status_code=None, content=None,
            include_view=None, exclude_view=None, exact_view=None,
            method_assertions=None,
            request_assertions=None,
            response_assertions=None,
            **kwargs):
        """
        Sends an HTTP request to the given view with arguments and keyword
        arguments using the client's method.
        
        If method_args or method_kwargs is specified, their values will
        take precedence to allow for cooperative super() calls.
        
        If the path is not specified, a unique path will be generated.
        
        If include_view is specified, the generated view function must have the
        specified attributes after it has been called. If exclude_view is
        specified, the generated view function must not have the specified
        attributes after the view has been called. If exact_view is specified,
        the generated view function must have the specified names and exact
        attribute values after the view has been called.
        
        See daydreamer.test.testcases.TestCase.assertViewBehavior for
        documentation of the other arguments.
        
        """
        # Use a unique path?
        path = self.unique_path() if path is None else path
        
        # Generate or use the passed method arguments and keyword arguments?
        if method_args is None and method_kwargs is None:
            method_args = (view,)
            method_kwargs = {
                "view_args": view_args,
                "view_kwargs": view_kwargs,
                "path": path}
        
        # Set up the assertions.
        method_assertions = lang.updated(
            method_assertions or {},
            dict(
                include_view=include_view,
                exclude_view=exclude_view,
                exact_view=exact_view),
            copy=bool(method_assertions))
        
        return super(TestCase, self).assertViewBehavior(
            path, method=method, method_args=method_args,
            method_kwargs=method_kwargs,
            data=data, follow=follow, headers=headers,
            setup=setup, repeat=repeat,
            exception=exception,
            status_code=status_code, content=content,
            method_assertions=method_assertions,
            request_assertions=request_assertions,
            response_assertions=response_assertions,
            **kwargs)
