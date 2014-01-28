from __future__ import unicode_literals

from daydreamer.views.behaviors import gzip

from . import base


class GZipPageTestCase(base.TestCase):
    """
    Tests for the GZipPage view behavior.
    
    """
    view_classes = gzip.GZipPage
    
    def test_gzip_page(self):
        """
        Check that a response's content is gzipped when the conditions for
        gzipping are correct.
        
        """
        content = self.unique_gzip()
        self.assertViewBehavior(
            {"get": content},
            headers={"HTTP_ACCEPT_ENCODING": "gzip"},
            status_code=200,
            content=self.compress(content),
            headers_exact={"Content-Encoding": "gzip"})
    
    def test_gzip_page_disabled(self):
        """
        Check that the response's content is not gzipped when the view behavior
        is disabled, even when the conditions for gzipping are correct.
        
        """
        content = self.unique_gzip()
        self.assertViewBehavior(
            {"gzip_page": False, "get": content},
            headers={"HTTP_ACCEPT_ENCODING": "gzip"},
            status_code=200,
            content=content,
            headers_exclude="Content-Encoding")
    
    def test_gzip_page_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence and
        that the response's content is not gzipped, because the content is
        too short.
        
        """
        self.assertViewBehavior(
            headers={"HTTP_ACCEPT_ENCODING": "gzip"},
            status_code=405,
            headers_exclude="Content-Encoding")
    
    def test_gzip_page_disabled_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence and
        that the response's context is not gzipped when the view behavior is
        disabled, even when the conditions for gzipping are correct.
        
        """
        self.assertViewBehavior(
            {"gzip_page": False},
            headers={"HTTP_ACCEPT_ENCODING": "gzip"},
            status_code=405,
            headers_exclude="Content-Encoding")
    