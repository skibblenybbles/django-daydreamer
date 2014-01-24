from __future__ import unicode_literals

import types

from django import http
from django.utils import six

from .. import testcases
from . import client


__all__ = ("TestCase",)


class TestCase(testcases.TestCase):
    """
    A test case for dynamically generating and testing class-based views.
    Uses a customized client and request handler to facilitate view testing
    without using the URL resolution framework.
    
    To turn on Django's CSRF framework during testing, set the class'
    enforce_csrf_checks attribute to True.
    
    """
    client_class = client.Client
    enforce_csrf_checks = False
    
    # All HTTP verbs that should be automatically generated when
    # a string is provided in self.view()'s attrs.
    generate_http_verbs = (
        b"get", b"head", b"options", b"post", b"put", b"patch", b"delete",)
    
    def _pre_setup(self):
        """
        Replaces the default test client, providing a hook to specify whether
        to use Django's CSRF framework during testing.
        
        """
        super(TestCase, self)._pre_setup()
        self.client = self.client_class(
            enforce_csrf_checks=self.enforce_csrf_checks)
    
    def unique_path(self):
        """
        Returns a unique path for use in testing class-based views.
        
        """
        return "/{unique:s}/".format(unique=self.unique())
    
    def generate_http_verb(self, verb, content):
        """
        Generates an HTTP verb handler method that returns a normal
        response with the specified content.
        
        """
        def methd(self, request, *args, **kwargs):
            return http.HttpResponse(content)
        method.__name__ = verb
        return method
    
    def view(self, view_classes, **attrs):
        """
        Generate a view from the given view class(es) and attributes.
        
        The view_classes may specify a single class or an iterable of
        classes to inherit from.
        
        The generated view will inherit from the view classes, so be sure
        to inherit from django.views.generic.base.View, or a class that is
        duck type equivalent.
        
        The attrs argument should be a dictionary of values that will be
        added to the class at creation time.
        
        For methods that implement HTTP verbs (get, post, put, etc.),
        if the attrs specify a string, a method that returns a simple
        response containing the string will be automatically generated.
        
        """
        # Normalize the view classes.
        view_classes = (
            (view_classes,)
                if isinstance(view_classes, types.TypeType)
                else view_classes
                    if isinstance(view_classes, tuple)
                    else tuple(view_classes))
        
        # Generate methods for HTTP verbs?
        for method in self.generate_http_verbs:
            content = attrs.get(method, None)
            if isinstance(content, six.string_types):
                attrs[method] = self.generate_http_verb(method, content)
        
        # Create the view.
        return type(
            b"".join(
                (b"Test",) + 
                tuple(view_class.__name__ for view_class in view_classes)),
            view_classes,
            attrs).as_view()
