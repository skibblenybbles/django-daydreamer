from __future__ import unicode_literals

import collections

from daydreamer.core import lang

from .. import testcases
from . import base


class TestCase(base.TestCase, testcases.TestCase):
    """
    A test case that provides a variety of general testing features
    for class-based views.
    
    Set the view_classes attribute to specify which view class(es) to inherit
    from for the test cases.
    
    """
    view_classes = None
    
    def view(self, **attrs):
        """
        Hardcodes self.view_classes as the first argument.
        
        """
        return super(TestCase, self).view(self.view_classes, **attrs)
    
    # Assertions.
    def assertViewBehavior(self,
            attrs=None, setup=None, view_args=None, view_kwargs=None,
            path=None, method="get", method_args=None, method_kwargs=None,
            data=None, follow=False, headers=None,
            repeat=None, exception=None,
            status_code=None, content=None,
            method_assertions=None,
            request_assertions=None,
            response_assertions=None,
            **kwargs):
        """
        Sends an HTTP request to the view created from attrs with arguments
        and keyword arguments using the client's method.
        
        If method_args or method_kwargs is specified, their values will
        take precedence to allow for cooperative super() calls.
        
        If the setup() callback is specified, its optional return value
        will be mixed into the view attributes.
        
        See daydreamer.test.views.testcases.TestCase.assertViewBehavior for
        documentation of the other arguments.
        
        """
        return super(TestCase, self).assertViewBehavior(
            self.view(
                **lang.updated(
                    attrs or {},
                    setup() or {}
                        if isinstance(setup, collections.Callable)
                        else {})),
            view_args=view_args, view_kwargs=view_kwargs,
            path=path, method=method, method_args=method_args,
            method_kwargs=method_kwargs,
            data=data, follow=follow, headers=headers,
            repeat=repeat,
            exception=exception,
            status_code=status_code, content=content,
            method_assertions=method_assertions,
            request_assertions=request_assertions,
            response_assertions=response_assertions,
            **kwargs)
