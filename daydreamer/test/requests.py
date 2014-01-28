from __future__ import unicode_literals

import collections
import functools

from . import base


class TestCase(base.TestCase):
    """
    A test case for making assertions about attributes on a request.
    
    """
    def assertRequestIncludes(self, request, names):
        """
        Asserts that the request contains the given attribute name(s).
        
        """
        self.assertAttributesIn(names, request)
    
    def assertRequestExcludes(self, request, names):
        """
        Asserts that the request does not contain the given attribute name(s).
        
        """
        self.assertAttributesNotIn(names, request)
    
    def assertRequestExact(self, request, attrs):
        """
        Asserts that the request contains the attribute names and values
        specified by attrs.
        
        """
        self.assertAttributesExact(request, attrs)
    
    def create_request_attribute_assertions(self, include=None, exclude=None,
            exact=None):
        """
        Returns a tuple of request assertion callbacks for the given arguments.
        
        """
        include = include or ()
        exclude = exclude or ()
        exact = (
            exact
                if isinstance(exact, collections.Mapping)
                else dict(exact or {}))
        return (
            ((functools.partial(self.assertRequestIncludes, names=include),)
                if include
                else ()) +
            ((functools.partial(self.assertRequestExcludes, names=exclude),)
                if exclude
                else ()) +
            ((functools.partial(self.assertRequestExact, attrs=exact),)
                if exact
                else ()))
    
    def create_request_assertions(self, request_includes=None,
            request_excludes=None, request_exact=None, **kwargs):
        """
        Adds request attribute assertions to the request assertions.
        
        """
        return (
            self.create_request_attribute_assertions(
                include=request_includes,
                exclude=request_excludes,
                exact=request_exact) +
            super(TestCase, self).create_request_assertions(**kwargs))
