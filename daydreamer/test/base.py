from __future__ import unicode_literals

import collections
import sys
import uuid

from django import test
from django.utils import encoding, six

from daydreamer.core import lang

from . import client


class TestCase(test.TestCase):
    """
    A test case that enhances Django's base test case with common testing
    utilities. Includes the assertBehavior(), which provides a flexible
    way to send an HTTP request and make assertions about the request
    and response objects.
    
    To turn on Django's CSRF framework during testing, set the
    enforce_csrf_checks attribute to True.
    
    """
    enforce_csrf_checks = False
    client_class = client.Client
    
    # Setup.
    def _pre_setup(self):
        """
        Replaces the default test client, providing a hook to specify whether
        to use Django's CSRF framework during testing.
        
        """
        super(TestCase, self)._pre_setup()
        self.client = self.client_class(
            enforce_csrf_checks=self.enforce_csrf_checks)
    
    # Utilities.
    def unique(self):
        """
        Returns a unique string (a UUID), useful for dummy values in tests.
        Helps to guarantee that functions or methods are not returning
        hardcoded values that coincidentally match a value used for
        a test.
        
        """
        return encoding.force_text(uuid.uuid4())
    
    # Assertions.
    def assertKeysIn(self, keys, data, message=None):
        """
        Asserts that the keys are present in the data.
        
        """
        for key in (
            (keys,)
                if isinstance(keys, six.string_types)
                else keys or ()):
            self.assertIn(
                key, data,
                message or "The key {key!r} was not found.".format(
                    key=key))
    
    def assertKeysNotIn(self, keys, data, message=None):
        """
        Asserts that the keys are not present in the data.
        
        """
        for key in (
            (keys,)
                if isinstance(keys, six.string_types)
                else keys or ()):
            self.assertNotIn(
                key, data,
                message or "The key {key!r} was found.")
    
    def assertItemsExact(self, data, items, message=None):
        """
        Asserts that the keys specified in items are present in data and that
        their values are equal.
        
        """
        for key, value in six.iteritems(
            items
                if isinstance(items, collections.Mapping)
                else dict(items or {})):
            self.assertIn(
                key, data,
                "The key {key!r} was not found.".format(key=key))
            self.assertEqual(
                data[key], value, (
                    message or
                    "The {actual!r} value for the key {key!r} was not equal "
                    "to {value!r}.".format(
                        actual=data[key], key=key, value=value)))
    
    def assertAttributesIn(self, attrs, obj, message=None):
        """
        Asserts that the attributes are present in the object.
        
        """
        for attr in (
            (attrs,)
                if isinstance(attrs, six.string_types)
                else attrs or ()):
            self.assertTrue(
                hasattr(obj, attr),
                message or "The attribute {attr!r} was not found.".format(
                    attr=attr))
    
    def assertAttributesNotIn(self, attrs, obj, message=None):
        """
        Asserts that the attributes are not present in the object.
        
        """
        for attr in (
            (attrs,)
                if isinstance(attrs, six.string_types)
                else attrs or ()):
            self.assertFalse(
                hasattr(obj, attr),
                message or "The attribute {attr!r} was found.".format(
                    attr=attr))
    
    def assertAttributesExact(self, obj, items, message=None):
        """
        Asserts that the attributes from items are present in the object and
        that their values are equal.
        
        """
        for attr, value in six.iteritems(
            items
                if isinstance(items, collections.Mapping)
                else dict(items or {})):
            self.assertTrue(
                hasattr(obj, attr),
                "The atrribute {attr!r} was not found".format(
                    attr=attr))
            self.assertEqual(
                getattr(obj, attr), value, (
                    message or
                    "The {actual!r} value for the attribute {attr!r} was not "
                    "equal to {value!r}.".format(
                        actual=getattr(obj, attr), attr=attr, value=value)))
    
    def assertViewBehavior(self, method="get",
            method_args=None, method_kwargs=None,
            data=None, follow=False, headers=None,
            setup=None, repeat=None, exception=None,
            status_code=None, content=None,
            method_assertions=None,
            request_assertions=None,
            response_assertions=None):
        """
        Sends an HTTP request for the specified method including optional
        data or headers and optionally following redirects. Makes a series of
        assertions about the underlying view's behavior.
        
        The method along with its method_args and method_kwargs will be used to
        send a request with the test case's client.
        
        If data is specified, it should be a dictionary for a "get", "post"
        or "head" request and a string otherwise. When specified, its value
        will be added to method_kwargs under the "data" key.
        
        If follow is True, redirects will be followed recursively. Its value
        will be added to method_kwargs under the "follow" key.
        
        If headers is specified, it should be a dictionary containing header
        values for the request, which will be mixed into method_kwargs.
        
        If the setup() callback is specified, it will be called before the
        request is sent.
        
        If repeat is specified, it should indicate the number of times to
        repeat the request. Each call will be wrapped in an exception handler
        until the last call, which will be processed by the assertions.
        
        If exception is specified, the request should raise the exception,
        and no other assertions will be performed.
        
        If status code is specified, the response's status code must match.
        
        If content is specified, the response's content must match.
        
        If any of method_assertions, request_assertions or response_assesrtions
        is specified, it should be a dictionary of values to pass to the
        corresponding get_<type>_assertions() methods.
        
        """
        # Sanity check and normalize the arguments.
        method_args = method_args or ()
        method_kwargs = (
            method_kwargs
                if isinstance(method_kwargs, collections.Mapping)
                else dict(method_kwargs or {}))
        if data is not None:
            if method in ("get", "post", "head",):
                if not isinstance(data, collections.Mapping):
                    raise ValueError(
                        'The data must be a dictionary for "get", "post" or '
                        '"head" requests.')
            else:
                if not isinstance(data, six.string_types):
                    raise ValueError(
                        "The data must be a string for request methods other "
                        'than "get", "post" or "head".')
        else:
            data = {} if method in ("get", "post", "head",) else ""
        headers = (
            headers
                if isinstance(headers, collections.Mapping)
                else dict(headers or {}))
        repeat = repeat or 0
        method_assertions = (
            method_assertions
                if isinstance(method_assertions, collections.Mapping)
                else dict(method_assertions or {}))
        request_assertions = (
            request_assertions
                if isinstance(request_assertions, collections.Mapping)
                else dict(request_assertions or {}))
        response_assertions = (
            response_assertions
                if isinstance(response_assertions, collections.Mapping)
                else dict(response_assertions or {}))
        
        # Mix data and headers into the method keyword arguments.
        method_kwargs = lang.updated(
            method_kwargs,
            dict(
                ((("data", data),) if data else ()) +
                (("follow", follow),) +
                tuple(six.iteritems(headers))),
            copy=True)
        
        # Burn through the repetitions?
        while repeat > 1:
            try:
                getattr(self.client, method)(
                    *method_args, **method_kwargs)
            except SystemExit:
                six.reraise(*sys.exc_info())
            except:
                pass
            repeat -= 1
        
        # Do we expect an exception or a normal response?
        if exception:
            with self.assertRaises(
                exception.__class__
                    if isinstance(exception, Exception)
                    else exception):
                getattr(self.client, method)(
                    *method_args, **method_kwargs)
        else:
            response = getattr(self.client, method)(
                *method_args, **method_kwargs)
            request = self.client.handler.last_request
            if status_code is not None:
                self.assertEqual(response.status_code, status_code)
            if content is not None:
                self.assertEqual(response.content, content)
            for assertion in self.create_method_assertions(
                **method_assertions):
                assertion(*method_args or ())
            for assertion in self.create_request_assertions(
                **request_assertions):
                assertion(request)
            for assertion in self.create_response_assertions(
                **response_assertions):
                assertion(response)
    
    def create_method_assertions(self):
        """
        Subclasses should accept arbitrary keyword arguments and pass any
        unused keywords to super(). That way, this base implementation will
        raise an exception if keywords have gone unused.
        
        """
        return ()
    
    def create_request_assertions(self):
        """
        A hook for creating request assertions. Must return a tuple of
        callbacks that accept the request that was generated to make
        the request.
        
        Subclasses should accept arbitrary keyword arguments and pass any
        unused keywords to super(). That way, this base implementation will
        raise an exception if keywords have gone unused.
        
        """
        return ()
    
    def create_response_assertions(self):
        """
        A hook for creating response assertions. Must return a tuple of
        callbacks that accept the response that was generated by making
        the request.
        
        Subclasses should accept arbitrary keyword arguments and pass any
        unused keywords to super(). That way, this base implementation will
        raise an exception if keywords have gone unused.
        
        """
        return ()
