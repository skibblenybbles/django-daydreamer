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
    def assertViewBehavior(self, view, view_args=None, view_kwargs=None,
            path=None, method="get", method_args=None, method_kwargs=None,
            view_includes=None, view_excludes=None, view_exact=None,
            **kwargs):
        """
        Sends an HTTP request to the given view with arguments and keyword
        arguments using the client's method.
        
        If method_args or method_kwargs is specified, their values will
        take precedence to allow for cooperative super() calls.
        
        If the path is not specified, a unique path will be generated.
        
        If view_includes is specified, the generated view function must have the
        specified attributes after it has been called. If view_excludes is
        specified, the generated view function must not have the specified
        attributes after the view has been called. If view_exact is specified,
        the generated view function must have the specified names and exact
        attribute values after the view has been called.
        
        See daydreamer.test.testcases.TestCase.assertViewBehavior for
        documentation of the other arguments.
        
        """
        # Use a unique path?
        path = self.unique_path() if path is None else path
        
        # Generate or use the passed method arguments and keyword arguments?
        if method_args is None or method_kwargs is None:
            method_args = (view,)
            method_kwargs = {
                "view_args": view_args,
                "view_kwargs": view_kwargs,
                "path": path}
        
        # Set up the assertions.
        method_assertions = lang.updated(
            kwargs.pop("method_assertions", {}),
            dict(
                view_includes=view_includes,
                view_excludes=view_excludes,
                view_exact=view_exact),
            copy=True)
        
        return super(TestCase, self).assertViewBehavior(
            None, method=method, method_args=method_args,
            method_kwargs=method_kwargs,
            method_assertions=method_assertions,
            **kwargs)
