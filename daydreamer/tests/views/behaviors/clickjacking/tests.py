from __future__ import unicode_literals

from daydreamer.views.behaviors import clickjacking

from . import base


class XFrameOptionsDenyTestCase(base.TestCase):
    """
    Tests for the XFrameOptionsDeny view behavior.
    
    Clickjacking middleware is turned off to enable edge case behavior.
    
    """
    view_classes = clickjacking.XFrameOptionsDeny
    
    def test_deny_headers(self):
        """
        Check that the DENY X-Frame-Options header is set on the response.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content},
            status_code=200,
            content=content,
            headers_exact={"X-Frame-Options": "DENY"})
    
    def test_deny_disabled(self):
        """
        Check that no X-Frame-Options header is set on the response when the
        view behavior is disabled.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"xframe_options_deny": False, "get": content},
            status_code=200,
            content=content,
            headers_exclude="X-Frame-Options")
    
    def test_deny_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        and that the DENY X-Frame-Options header is set on the response.
        
        """
        self.assertViewBehavior(
            status_code=405,
            headers_exact={"X-Frame-Options": "DENY"})
    
    def test_deny_disabled_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        and that no X-Frame-Options header is set on the response when the
        view behavior is disabled.
        
        """
        self.assertViewBehavior(
            {"xframe_options_deny": False},
            status_code=405,
            headers_exclude="X-Frame-Options")


class XFrameOptionsSameOriginTestCase(base.TestCase):
    """
    Tests for the XFrameOptionsSameOrigin view behavior.
    
    Clickjacking middleware is turned off to enable edge case behavior.
    
    """
    view_classes = clickjacking.XFrameOptionsSameOrigin
    
    def test_same_origin_headers(self):
        """
        Check that the SAMEORIGIN X-Frame-Options header is set on
        the response.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content},
            status_code=200,
            content=content,
            headers_exact={"X-Frame-Options": "SAMEORIGIN"})
    
    def test_same_origin_disabled(self):
        """
        Check that no X-Frame-Options header is set on the response when the
        view behavior is disabled.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"xframe_options_same_origin": False, "get": content},
            status_code=200,
            content=content,
            headers_exclude="X-Frame-Options")
    
    def test_same_origin_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        and that the SAMEORIGIN X-Frame-Options header is set on the response.
        
        """
        self.assertViewBehavior(
            status_code=405,
            headers_exact={"X-Frame-Options": "SAMEORIGIN"})
    
    def test_same_origin_disabled_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        and that no X-Frame-Options header is set on the response when the
        view behavior is disabled.
        
        """
        self.assertViewBehavior(
            {"xframe_options_same_origin": False},
            status_code=405,
            headers_exclude="X-Frame-Options")


class XFrameOptionsExemptTestCase(base.TestCase):
    """
    Tests for the XFrameOptionsExempt view behavior.
    
    Clickjacking middleware is turned on to enable edge case behavior.
    
    """
    view_classes = clickjacking.XFrameOptionsExempt
    clickjacking_middleware_enabled = True
    
    def test_exempt(self):
        """
        Check that no X-Frame-Options header is set on the response.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content},
            status_code=200,
            content=content,
            headers_exclude="X-Frame-Options")
    
    def test_exempt_disabled(self):
        """
        Check that an X-Frame-Options header is set on the response when the
        view behavior is disabled.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"xframe_options_exempt": False, "get": content},
            status_code=200,
            content=content,
            headers_include="X-Frame-Options")
    
    def test_exempt_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        and that no X-Frame-Options header is set on the response.
        
        """
        self.assertViewBehavior(
            status_code=405,
            headers_exclude="X-Frame-Options")
    
    def test_exempt_disabled_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        and that an X-Frame-Options header is set on the response when the
        view behavior is disabled.
        
        """
        self.assertViewBehavior(
            {"xframe_options_exempt": False},
            status_code=405,
            headers_include="X-Frame-Options")
