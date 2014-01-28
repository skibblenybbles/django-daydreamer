from __future__ import unicode_literals

import collections
import functools

from . import base


class TestCase(base.TestCase):
    """
    A test case for making assertions about the cookies in a response.
    
    """
    def assertCookiesInclude(self, response, names):
        """
        Asserts that the response contains the given cookie name(s).
        
        """
        self.assertTrue(
            hasattr(response, "cookies") and response.cookies,
            "The response must have a non-empty cookies attribute.")
        self.assertKeysIn(names, response.cookies)
    
    def assertCookiesExclude(self, response, names):
        """
        Asserts that the response does not contain the given cookie name(s).
        
        """
        if hasattr(response, "cookies") and response.cookies:
            self.assertKeysNotIn(names, response.cookies)
    
    def assertCookiesExact(self, response, cookies):
        """
        Asserts that the response contains the names and cookie values
        specified by cookies.
        
        """
        self.assertTrue(
            hasattr(response, "cookies") and response.cookies,
            "The response must have a non-empty cookies attribute.")
        self.assertItemsExact(response.cookies, cookies)
    
    def create_cookie_assertions(self, include=None, exclude=None, exact=None):
        """
        Returns a tuple of cookie assertion callbacks for the given arguments.
        
        """
        include = include or ()
        exclude = exclude or ()
        exact = (
            exact
                if isinstance(exact, collections.Mapping)
                else dict(exact or {}))
        return (
            ((functools.partial(self.assertCookiesInclude, names=include),)
                if include
                else ()) +
            ((functools.partial(self.assertCookiesExclude, names=exclude),)
                if exclude
                else ()) +
            ((functools.partial(self.assertCookiesExact, cookies=exact),)
                if exact
                else ()))
    
    def create_response_assertions(self, cookies_include=None,
            cookies_exclude=None, cookies_exact=None, **kwargs):
        """
        Adds cookie assertions to the response assertions.
        
        """
        return (
            self.create_cookie_assertions(
                include=cookies_include,
                exclude=cookies_exclude,
                exact=cookies_exact) +
            super(TestCase, self).create_response_assertions(**kwargs))
