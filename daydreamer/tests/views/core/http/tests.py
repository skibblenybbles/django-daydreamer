from __future__ import unicode_literals

from daydreamer.views.core import http

from . import base


class HttpMethodAllowTestCase(base.TestCase):
    """
    Tests for the HttpMethodAllow view base class.
    
    """
    view_classes = http.HttpMethodAllow
    
    def test_included_present_allowed(self):
        """
        Check that an included HTTP method name's handler is dispatched when
        the handler is present.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content, "http_method_names": ("get",)},
            status_code=200,
            content=content)
    
    def test_included_missing_denied(self):
        """
        Check that an included HTTP method name is denied when its handler
        is missing.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"http_method_names": ("get",)},
            status_code=405)
    
    def test_excluded_present_allowed(self):
        """
        Check that an excluded HTTP method name's handler is dispatched when
        the handler is present.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content, "http_method_names": ()},
            status_code=200,
            content=content)
    
    def test_excluded_present_denied(self):
        """
        Check that an excluded HTTP method name is denied when its handler is
        missing.
        
        """
        self.assertViewBehavior(
            {"http_method_names": ()},
            status_code=405)


class HttpMethodDenyTestCase(base.TestCase):
    """
    Tests for the HttpMethodDeny view base class.
    
    """
    view_classes = http.HttpMethodDeny
    
    def test_included_present_denied(self):
        """
        Check that an included HTTP method name is denied when the handler
        is present.
        
        """
        self.assertViewBehavior(
            {"get": self.unique(), "http_method_names": ("get",)},
            status_code=405)
    
    def test_included_missing_denied(self):
        """
        Check that an included HTTP method name is denied when the handler
        is missing.
        
        """
        self.assertViewBehavior(
            {"http_method_names": ("get",)},
            status_code=405)
    
    def test_excluded_present_denied(self):
        """
        Check that an excluded HTTP method name is denied when the handler
        is present.
        
        """
        self.assertViewBehavior(
            {"get": self.unique(), "http_method_names": ()},
            status_code=405)
    
    def test_exclude_missing_denied(self):
        """
        Check that an excluded HTTP method name is denied when the handler
        is missing.
        
        """
        self.assertViewBehavior(
            {"http_method_names": ()},
            status_code=405)
