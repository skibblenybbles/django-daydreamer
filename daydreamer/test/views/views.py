from __future__ import unicode_literals

import collections
import functools

from . import base


class TestCase(base.TestCase):
    """
    A test case for making assertions about attributes on a view.
    
    """
    def assertViewIncludes(self, view, names):
        """
        Asserts that the view contains the given attribute name(s).
        
        """
        self.assertAttributesIn(names, view)
    
    def assertViewExcludes(self, view, names):
        """
        Asserts that the view does not contain the given attribute name(s).
        
        """
        self.assertAttributesNotIn(names, view)
    
    def assertViewExact(self, view, attrs):
        """
        Asserts that the view contains the attribute names and values
        specified by attrs.
        
        """
        self.assertAttributesExact(view, attrs)
    
    def create_view_attribute_assertions(self, include=None, exclude=None,
            exact=None):
        """
        Returns a tuple of view assertion callbacks for the given arguments.
        
        """
        include = include or ()
        exclude = exclude or ()
        exact = (
            exact
                if isinstance(exact, collections.Mapping)
                else dict(exact or {}))
        return (
            ((functools.partial(self.assertViewIncludes, names=include),)
                if include
                else ()) +
            ((functools.partial(self.assertViewExcludes, names=exclude),)
                if exclude
                else ()) +
            ((functools.partial(self.assertViewExact, attrs=exact),)
                if exact
                else ()))
    
    def create_method_assertions(self, include_view=None, exclude_view=None,
            exact_view=None, **kwargs):
        """
        Adds view attribute assertions to the method assertions.
        
        """
        return (
            self.create_view_attribute_assertions(
                include=include_view,
                exclude=exclude_view,
                exact=exact_view) +
            super(TestCase, self).create_method_assertions(**kwargs))
