from __future__ import unicode_literals

import collections
import functools

from . import base


class TestCase(base.TestCase):
    """
    A test case for making assertions about the context in a response.
    
    """
    def assertContextIncludes(self, response, names):
        """
        Asserts that the response's context contains the given name(s).
        
        """
        self.assertTrue(
            hasattr(response, "context") and response.context,
            "The response must have a non-empty context attribute.")
        self.assertKeysIn(names, response.context)
    
    def assertContextExcludes(self, response, names):
        """
        Asserts that the respone's context does not contain the given name(s).
        
        """
        if hasattr(response, "context") and response.context:
            self.assertKeysNotIn(names, response.context)
    
    def assertContextExact(self, response, context):
        """
        Asserts that the response's context contains the names and values
        specified by context.
        
        """
        self.assertTrue(
            hasattr(response, "context") and response.context,
            "The response must have a non-empty context attribute.")
        self.assertItemsExact(response.context, context)
    
    def create_context_assertions(self, include=None, exclude=None, exact=None):
        """
        Returns a tuple of context assertion callbacks for the given arguments.
        
        """
        include = include or ()
        exclude = exclude or ()
        exact = (
            exact
                if isinstance(exact, collections.Mapping)
                else dict(exact or {}))
        return (
            ((functools.partial(self.assertContextIncludes, names=include),)
                if include
                else ()) +
            ((functools.partial(self.assertContextExcludes, names=exclude),)
                if exclude
                else ()) +
            ((functools.partial(self.assertContextExact, context=exact),)
                if exact
                else ()))
    
    def create_response_assertions(self, context_includes=None,
            context_excludes=None, context_exact=None, **kwargs):
        """
        Add context assertions to the response assertions.
        
        """
        return (
            self.create_context_assertions(
                include=context_includes,
                exclude=context_excludes,
                exact=context_exact) +
            super(TestCase, self).create_response_assertions(**kwargs))
