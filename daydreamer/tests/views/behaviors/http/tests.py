from __future__ import unicode_literals

import datetime

from daydreamer.views import generic
from daydreamer.views.behaviors import http

from . import base


class RequireGETTestCase(base.TestCase):
    """
    Tests for the RequireGET view behavior.
    
    """
    view_classes = (http.RequireGET, generic.View,)
    
    def test_get_allowed(self):
        """
        Check that GET requests are allowed.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content},
            status_code=200,
            content=content)
    
    def test_head_denied(self):
        """
        Check that HEAD requests are denied.
        
        """
        self.assertViewBehavior(
            {"head": self.unique()},
            method="head",
            status_code=405)
    
    def test_options_denied(self):
        """
        Check that OPTIONS requests are denied.
        
        """
        self.assertViewBehavior(
            {"options": self.unique()},
            method="options",
            status_code=405)
    
    def test_post_denied(self):
        """
        Check that POST requests are denied.
        
        """
        self.assertViewBehavior(
            {"post": self.unique()},
            method="post",
            status_code=405)
    
    def test_put_denied(self):
        """
        Check that PUT requests are denied.
        
        """
        self.assertViewBehavior(
            {"put": self.unique()},
            method="put",
            status_code=405)
    
    def test_delete_denied(self):
        """
        Check that DELETE requests are denied.
        
        """
        self.assertViewBehavior(
            {"delete": self.unique()},
            method="delete",
            status_code=405)


class RequirePOSTTestCase(base.TestCase):
    """
    Tests for the RequirePOST view behavior.
    
    """
    view_classes = (http.RequirePOST, generic.View,)
    
    def test_post_allowed(self):
        """
        Check that POST requests are allowed.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"post": content},
            method="post",
            status_code=200,
            content=content)
    
    def test_get_allowed(self):
        """
        Check that GET requests are allowed.
        
        """
        self.assertViewBehavior(
            {"get": self.unique()},
            status_code=405)
    
    def test_head_denied(self):
        """
        Check that HEAD requests are denied.
        
        """
        self.assertViewBehavior(
            {"head": self.unique()},
            method="head",
            status_code=405)
    
    def test_options_denied(self):
        """
        Check that OPTIONS requests are denied.
        
        """
        self.assertViewBehavior(
            {"options": self.unique()},
            method="options",
            status_code=405)
    
    def test_put_denied(self):
        """
        Check that PUT requests are denied.
        
        """
        self.assertViewBehavior(
            {"put": self.unique()},
            method="put",
            status_code=405)
    
    def test_delete_denied(self):
        """
        Check that DELETE requests are denied.
        
        """
        self.assertViewBehavior(
            {"delete": self.unique()},
            method="delete",
            status_code=405)


class RequireSafeTestCase(base.TestCase):
    """
    Tests for the RequireSafe view behavior.
    
    """
    view_classes = (http.RequireSafe, generic.View,)
    
    def test_get_allowed(self):
        """
        Check that GET requests are allowed.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content},
            status_code=200,
            content=content)
    
    def test_head_denied(self):
        """
        Check that HEAD requests are allowed.
        
        """
        self.assertViewBehavior(
            {"head": self.unique()},
            method="head",
            status_code=200,
            content="")
    
    def test_options_denied(self):
        """
        Check that OPTIONS requests are denied.
        
        """
        self.assertViewBehavior(
            {"options": self.unique()},
            method="options",
            status_code=405)
    
    def test_post_denied(self):
        """
        Check that POST requests are denied.
        
        """
        self.assertViewBehavior(
            {"post": self.unique()},
            method="post",
            status_code=405)
    
    def test_put_denied(self):
        """
        Check that PUT requests are denied.
        
        """
        self.assertViewBehavior(
            {"put": self.unique()},
            method="put",
            status_code=405)
    
    def test_delete_denied(self):
        """
        Check that DELETE requests are denied.
        
        """
        self.assertViewBehavior(
            {"delete": self.unique()},
            method="delete",
            status_code=405)


class ConditionTestCase(base.TestCase):
    """
    Tests for the Condition view behavior.
    
    Note that this does not confirm all possible ETag and Last-Modified
    behaviors. It just shows that the decorator is wired in correctly.
    
    """
    view_classes = (http.Condition, generic.View,)
    
    def test_etag(self):
        """
        Check that the ETag header is set on the response.
        
        """
        etag = self.unique()
        content = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertViewBehavior(
            {"condition_etag": condition_etag, "get": content},
            status_code=200,
            content=content,
            headers_exact={"ETag": self.format_etag(etag)})
    
    def test_etag_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        when no valid ETag header is sent and that an ETag header is not set on
        the response.
        
        """
        etag = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertViewBehavior(
            {"condition_etag": condition_etag},
            status_code=405,
            headers_exclude="ETag")
    
    def test_etag_match_not_modified(self):
        """
        Check for a not modified response on ETag match.
        
        """
        etag = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertViewBehavior(
            {"condition_etag": condition_etag, "get": self.unique()},
            headers={"HTTP_IF_NONE_MATCH": self.format_etag(etag)},
            status_code=304,
            content="",
            headers_exact={"ETag": self.format_etag(etag)})
    
    def test_etag_match_precdence(self):
        """
        Check that the default HTTP method name protection takes precedence
        upon ETag match and than an ETag header is not set on the response.
        
        """
        etag = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertViewBehavior(
            {"condition_etag": condition_etag},
            headers={"HTTP_IF_NONE_MATCH": self.format_etag(etag)},
            status_code=405,
            headers_exclude="ETag")
    
    def test_etag_fail(self):
        """
        Check for a precondition fail response for an ETag mismatch.
        
        """
        etag = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertViewBehavior(
            {"condition_etag": condition_etag, "get": self.unique()},
            headers={"HTTP_IF_MATCH": self.format_etag(self.unique())},
            status_code=412,
            headers_exact={"ETag": self.format_etag(etag)})
    
    def test_etag_fail_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        upon ETag mismatch and that an ETag header is not set on the response.
        
        """
        etag = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertViewBehavior(
            {"condition_etag": condition_etag},
            headers={"HTTP_IF_MATCH": self.format_etag(self.unique())},
            status_code=405,
            headers_exclude="ETag")
    
    def test_etag_miss(self):
        """
        Check the ETag header is updated upon miss.
        
        """
        etag = self.unique()
        content = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertViewBehavior(
            {"condition_etag": condition_etag, "get": content},
            headers={"HTTP_IF_NONE_MATCH": self.format_etag(self.unique())},
            status_code=200,
            content=content,
            headers_exact={"ETag": self.format_etag(etag)})
    
    def test_etag_miss_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        upon ETag header miss and that the ETag header is not set on
        the response.
        
        """
        etag = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertViewBehavior(
            {"condition_etag": condition_etag},
            headers={"HTTP_IF_NONE_MATCH": self.format_etag(self.unique())},
            status_code=405,
            headers_exclude="ETag")
    
    def test_last_modified(self):
        """
        Check that the last modified header is set.
        
        """
        last_modified = datetime.datetime.now()
        content = self.unique()
        def condition_last_modified(self, request, *args, **kwargs):
            return last_modified
        self.assertViewBehavior({
                "condition_last_modified": condition_last_modified,
                "get": content},
            status_code=200,
            content=content,
            headers_exact={
                "Last-Modified": self.format_datetime(last_modified)})
    
    def test_last_modified_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        when no valid last modified header is sent and that a last modified
        header is not set on the response.
        
        """
        last_modified = datetime.datetime.now()
        def condition_last_modified(self, request, *args, **kwargs):
            return last_modified
        self.assertViewBehavior(
            {"condition_last_modified": condition_last_modified},
            status_code=405,
            headers_exclude="Last-Modified")
    
    def test_last_modified_match_not_modified(self):
        """
        Check for a not modified response on last modified match.
        
        """
        last_modified = datetime.datetime.now()
        def condition_last_modified(self, request, *args, **kwargs):
            return last_modified
        self.assertViewBehavior({
                "condition_last_modified": condition_last_modified,
                "get": self.unique()},
            headers={
                "HTTP_IF_MODIFIED_SINCE":
                    self.format_datetime(
                        last_modified + datetime.timedelta(hours=1))},
            status_code=304,
            headers_exact={
                "Last-Modified": self.format_datetime(last_modified)})
    
    def test_last_modified_match_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        upon last modified match and that a last modified header is not set on
        the response.
        
        """
        last_modified = datetime.datetime.now()
        def condition_last_modified(self, request, *args, **kwargs):
            return last_modified
        self.assertViewBehavior(
            {"condition_last_modified": condition_last_modified},
            headers={
                "HTTP_IF_MODIFIED_SINCE":
                    self.format_datetime(
                        last_modified + datetime.timedelta(hours=1))},
            status_code=405,
            headers_exclude="Last-Modified")
    
    def test_last_modified_miss(self):
        """
        Check that the last modified header is updated upon miss.
        
        """
        last_modified = datetime.datetime.now()
        content = self.unique()
        def condition_last_modified(self, request, *args, **kwargs):
            return last_modified + datetime.timedelta(hours=1)
        self.assertViewBehavior({
                "condition_last_modified": condition_last_modified,
                "get": content},
            headers={
                "HTTP_IF_MODIFIED_SINCE": self.format_datetime(last_modified)},
            status_code=200,
            content=content,
            headers_exact={
                "Last-Modified":
                    self.format_datetime(
                        last_modified + datetime.timedelta(hours=1))})
    
    def test_last_modified_miss_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        upon last modified header miss and that a last modified header is
        not set on the response.
        
        """
        last_modified = datetime.datetime.now()
        def condition_last_modified(self, request, *args, **kwargs):
            return last_modified + datetime.timedelta(hours=1)
        self.assertViewBehavior(
            {"condition_last_modified": condition_last_modified},
            headers={
                "HTTP_IF_MODIFIED_SINCE": self.format_datetime(last_modified)},
            status_code=405,
            headers_exclude="Last-Modified")
