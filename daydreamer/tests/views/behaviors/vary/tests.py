from __future__ import unicode_literals

from daydreamer.views import generic
from daydreamer.views.behaviors import vary

from . import base


class VaryOnHeadersTestCase(base.TestCase):
    """
    Tests for the VaryOnHeaders view behavior.
    
    """
    view_classes = (vary.VaryOnHeaders, generic.View,)
    
    def test_vary_on_headers_single(self):
        """
        Check that a single Vary header value is set on the response.
        
        """
        content = self.unique()
        vary = self.unique()
        self.assertViewBehavior(
            {"vary_on_headers": vary, "get": content},
            status_code=200,
            content=content,
            headers_exact={"Vary": vary})
    
    def test_vary_on_headers_multiple(self):
        """
        Check that multiple Vary header values are set on the response.
        
        """
        content = self.unique()
        vary = (self.unique(), self.unique(),)
        self.assertViewBehavior(
            {"vary_on_headers": vary, "get": content},
            status_code=200,
            content=content,
            headers_exact={"Vary": ", ".join(vary)})
    
    def test_vary_on_headers_disabled(self):
        """
        Check that the behavior is disabled when no Vary header values
        are specified.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content},
            status_code=200,
            content=content,
            headers_exclude="Vary")
    
    def test_vary_on_headers_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        and that no Vary headers are set on the response.
        
        """
        vary = self.unique()
        self.assertViewBehavior(
            {"vary_on_headers": vary},
            status_code=405,
            headers_exclude="Vary")


class VaryOnCookieTestCase(base.TestCase):
    """
    Tests for the VaryOnCookie view behavior.
    
    """
    view_classes = (vary.VaryOnCookie, generic.View,)
    
    def test_vary_on_cookie(self):
        """
        Check that a Vary header value for cookies is set on the response.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content},
            status_code=200,
            content=content,
            headers_exact={"Vary": "Cookie"})
    
    def test_vary_on_cookie_disabled(self):
        """
        Check that the behavior is disabled when specified.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"vary_on_cookie": False, "get": content},
            status_code=200,
            content=content,
            headers_exclude="Vary")
    
    def test_vary_on_cookie_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        and that no Vary headers are set on the response.
        
        """
        vary = self.unique()
        self.assertViewBehavior(
            status_code=405,
            headers_exclude="Vary")
