from __future__ import unicode_literals

from django import http

from daydreamer.views import generic
from daydreamer.views.behaviors import cache

from . import base


class CachePageTestCase(base.TestCase):
    """
    Tests for the CachePage view behavior.
    
    """
    view_classes = (cache.CachePage, generic.View,)
    
    def test_cache_page(self):
        """
        Check that the response is cached.
        
        """
        content = self.unique()
        calls = []
        def get(self, request, *args, **kwargs):
            calls.append(None)
            return http.HttpResponse(content)
        self.assertViewBehavior(
            {"get": get},
            repeat=2,
            status_code=200,
            content=content)
        self.assertEqual(len(calls), 1)
    
    def test_cache_page_disabled(self):
        """
        Check that the response is not cached when the behavior is disabled.
        
        """
        content = self.unique()
        calls = []
        def get(self, request, *args, **kwargs):
            calls.append(None)
            return http.HttpResponse(content)
        self.assertViewBehavior(
            {"cache_page": False, "get": get},
            repeat=2,
            status_code=200,
            content=content)
        self.assertEqual(len(calls), 2)
    
    def test_cache_page_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence.
        
        """
        self.assertViewBehavior(
            status_code=405)


class CacheControlTestCase(base.TestCase):
    """
    Tests for the CacheControl view behavior.
    
    """
    view_classes = (cache.CacheControl, generic.View,)
    
    def test_defaults(self):
        """
        Check that the defaults do not set any cache control headers on
        the response.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content},
            status_code=200,
            content=content,
            headers_exclude="Cache-Control")
    
    def test_public(self):
        """
        Check that the public cache control header is set on the resopnse.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"cache_control_public": True, "get": content},
            status_code=200,
            content=content,
            headers_exact={"Cache-Control": "public"})
    
    def test_private(self):
        """
        Check that the private cache control header is set on the resopnse.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"cache_control_public": False, "get": content},
            status_code=200,
            content=content,
            headers_exact={"Cache-Control": "private"})
    
    def test_no_cache(self):
        """
        Check that the no_cache cache control header is set on the resopnse.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"cache_control_no_cache": True, "get": content},
            status_code=200,
            content=content,
            headers_exact={"Cache-Control": "no-cache"})
    
    def test_no_transform(self):
        """
        Check that the no_transform cache control header is set on the resopnse.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"cache_control_no_transform": True, "get": content},
            status_code=200,
            content=content,
            headers_exact={"Cache-Control": "no-transform"})
    
    def test_must_revalidate(self):
        """
        Check that the must_revalidate cache control header is set on
        the resopnse.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"cache_control_must_revalidate": True, "get": content},
            status_code=200,
            content=content,
            headers_exact={"Cache-Control": "must-revalidate"})
    
    def test_proxy_revalidate(self):
        """
        Check that the proxy_revalidate cache control header is set on
        the response.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"cache_control_proxy_revalidate": True, "get": content},
            status_code=200,
            content=content,
            headers_exact={"Cache-Control": "proxy-revalidate"})
    
    def test_max_age(self):
        """
        Check that the max_age cache control header is set on the resopnse.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"cache_control_max_age": 1, "get": content},
            status_code=200,
            content=content,
            headers_exact={"Cache-Control": "max-age=1"})
    
    def test_s_maxage(self):
        """
        Check that the s_maxage cache control header is set on the response.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"cache_control_s_maxage": 1, "get": content},
            status_code=200,
            content=content,
            headers_exact={"Cache-Control": "s-maxage=1"})
    
    def test_disabled(self):
        """
        Check that the behavior is disabled when cache_control is falsy.
        
        """
        content = self.unique()
        self.assertViewBehavior({
                "cache_control": False,
                "cache_control_public": True,
                "get": content},
            status_code=200,
            content=content,
            headers_exclude="Cache-Control")
    
    def test_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence and
        that no cache control headers are set on the response.
        
        """
        self.assertViewBehavior(
            {"cache_control_public": True},
            status_code=405,
            headers_exclude="Cache-Control")


class NeverCacheTestCase(base.TestCase):
    """
    Test for the NeverCache view behavior.
    
    """
    view_classes = (cache.NeverCache, generic.View,)
    
    def test_defaults(self):
        """
        Check that the defaults set the never cache control headers on
        the response.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content},
            status_code=200,
            content=content,
            headers_exact={"Cache-Control": "max-age=0"})
    
    def test_disabled(self):
        """
        Check that the behavior is disabled when never_cache is falsy.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"never_cache": False, "get": content},
            status_code=200,
            content=content,
            headers_exclude="Cache-Control")
    
    def test_precedence(self):
        """
        Check that the defualt HTTP method name protection takes precedence and
        that no cache control headers are set on the response.
        
        """
        self.assertViewBehavior(
            status_code=405,
            headers_exclude="Cache-Control")
