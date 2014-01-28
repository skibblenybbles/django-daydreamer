from __future__ import unicode_literals

import collections
import functools

from . import base


class TestCase(base.TestCase):
    """
    A test case for making assertions about the headers in a response.
    
    """
    def assertHeadersInclude(self, response, names):
        """
        Asserts that the response contains the given header name(s)
        
        """
        self.assertKeysIn(names, response)
    
    def assertHeadersExclude(self, response, names):
        """
        Asserts that the response does not contain the given header name(s).
        
        """
        self.assertKeysNotIn(names, response)
    
    def assertHeadersExact(self, response, headers):
        """
        Asserts that the response contains the names and values specified
        by headers.
        
        """
        self.assertItemsExact(response, headers)
    
    def create_header_assertions(self, include=None, exclude=None, exact=None):
        """
        Returns a tuple of header assertion callbacks for the given arguments.
        
        """
        include = include or ()
        exclude = exclude or ()
        exact = (
            exact
                if isinstance(exact, collections.Mapping)
                else dict(exact or {}))
        return (
            ((functools.partial(self.assertHeadersInclude, names=include),)
                if include
                else ()) +
            ((functools.partial(self.assertHeadersExclude, names=exclude),)
                if exclude
                else ()) +
            ((functools.partial(self.assertHeadersExact, headers=exact),)
                if exact
                else ()))
    
    def create_response_assertions(self, headers_include=None,
            headers_exclude=None, headers_exact=None, **kwargs):
        """
        Adds header assertions to the response assertions.
        
        """
        return (
            self.create_header_assertions(
                include=headers_include,
                exclude=headers_exclude,
                exact=headers_exact) +
            super(TestCase, self).create_response_assertions(**kwargs))
