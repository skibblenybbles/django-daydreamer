from __future__ import unicode_literals

import datetime

from daydreamer.views.decorated import http as http_decorated

from . import base


class RequireGETTestCase(base.TestCase):
    """
    Tests for the RequireGET view decorator mixin.
    
    """
    view_classes = http_decorated.RequireGET
    
    def test_get_allowed(self):
        """
        Check that GET requests are allowed.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"get": content},
            status_code=200,
            content=content)
    
    def test_head_not_allowed(self):
        """
        Check that HEAD requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"head": self.unique()},
            method="head",
            status_code=405)
    
    def test_options_not_allowed(self):
        """
        Check that OPTIONS requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"options": self.unique()},
            method="options",
            status_code=405)
    
    def test_post_not_allowed(self):
        """
        Check that POST requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"post": self.unique()},
            method="post",
            status_code=405)
    
    def test_put_not_allowed(self):
        """
        Check that PUT requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"put": self.unique()},
            method="put",
            status_code=405)
    
    def test_delete_not_allowed(self):
        """
        Check that DELETE requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"delete": self.unique()},
            method="delete",
            status_code=405)


class RequirePOSTTestCase(base.TestCase):
    """
    Tests for the RequirePOST view decorator mixin.
    
    """
    view_classes = http_decorated.RequirePOST
    
    def test_post_allowed(self):
        """
        Check that POST requests are allowed.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"post": content},
            method="post",
            status_code=200,
            content=content)
    
    def test_get_allowed(self):
        """
        Check that GET requests are allowed.
        
        """
        self.assertResponseBehavior(
            {"get": self.unique()},
            status_code=405)
    
    def test_head_not_allowed(self):
        """
        Check that HEAD requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"head": self.unique()},
            method="head",
            status_code=405)
    
    def test_options_not_allowed(self):
        """
        Check that OPTIONS requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"options": self.unique()},
            method="options",
            status_code=405)
    
    def test_put_not_allowed(self):
        """
        Check that PUT requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"put": self.unique()},
            method="put",
            status_code=405)
    
    def test_delete_not_allowed(self):
        """
        Check that DELETE requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"delete": self.unique()},
            method="delete",
            status_code=405)


class RequireSafeTestCase(base.TestCase):
    """
    Tests for the RequireSafe view decorator mixin.
    
    """
    view_classes = http_decorated.RequireSafe
    
    def test_get_allowed(self):
        """
        Check that GET requests are allowed.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"get": content},
            status_code=200,
            content=content)
    
    def test_head_not_allowed(self):
        """
        Check that HEAD requests are allowed.
        
        """
        self.assertResponseBehavior(
            {"head": self.unique()},
            method="head",
            status_code=200,
            content="")
    
    def test_options_not_allowed(self):
        """
        Check that OPTIONS requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"options": self.unique()},
            method="options",
            status_code=405)
    
    def test_post_not_allowed(self):
        """
        Check that POST requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"post": self.unique()},
            method="post",
            status_code=405)
    
    def test_put_not_allowed(self):
        """
        Check that PUT requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"put": self.unique()},
            method="put",
            status_code=405)
    
    def test_delete_not_allowed(self):
        """
        Check that DELETE requests are not allowed.
        
        """
        self.assertResponseBehavior(
            {"delete": self.unique()},
            method="delete",
            status_code=405)


class ConditionTestCase(base.TestCase):
    """
    Tests for the Condition view decorator mixin.
    
    Note that this does not confirm all possible ETag and Last-Modified
    behaviors. It just shows that the decorator is wired in correctly.
    
    """
    view_classes = http_decorated.Condition
    
    def test_etag_set(self):
        """
        Check that the ETag header is set.
        
        """
        etag = self.unique()
        content = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertResponseBehavior(
            {"condition_etag": condition_etag, "get": content},
            status_code=200,
            content=content,
            exact_headers={"ETag": self.format_etag(etag)})
    
    def test_etag_set_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        when no valid ETag header is sent and that an ETag is set on
        the response.
        
        """
        etag = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertResponseBehavior(
            {"condition_etag": condition_etag},
            status_code=405,
            exact_headers={"ETag": self.format_etag(etag)})
    
    def test_etag_not_modified(self):
        """
        Check for a not modified response on ETag match.
        
        """
        etag = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertResponseBehavior(
            {"condition_etag": condition_etag, "get": self.unique()},
            headers={"HTTP_IF_NONE_MATCH": self.format_etag(etag)},
            status_code=304,
            content="",
            exact_headers={"ETag": self.format_etag(etag)})
    
    def test_etag_fail(self):
        """
        Check for a precondition fail response for an ETag mismatch.
        
        """
        etag = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertResponseBehavior(
            {"condition_etag": condition_etag, "get": self.unique()},
            headers={"HTTP_IF_MATCH": self.format_etag(self.unique())},
            status_code=412,
            exact_headers={"ETag": self.format_etag(etag)})
    
    def test_etag_miss(self):
        """
        Check the ETag header is updated upon miss.
        
        """
        etag = self.unique()
        content = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertResponseBehavior(
            {"condition_etag": condition_etag, "get": content},
            headers={"HTTP_IF_NONE_MATCH": self.format_etag(self.unique())},
            status_code=200,
            content=content,
            exact_headers={"ETag": self.format_etag(etag)})
    
    def test_etag_miss_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        upon ETag header miss and that the ETag header is updated.
        
        """
        etag = self.unique()
        def condition_etag(self, request, *args, **kwargs):
            return etag
        self.assertResponseBehavior(
            {"condition_etag": condition_etag},
            headers={"HTTP_IF_NONE_MATCH": self.format_etag(self.unique())},
            status_code=405,
            exact_headers={"ETag": self.format_etag(etag)})
    
    def test_last_modified_set(self):
        """
        Check that the last modified header is set.
        
        """
        last_modified = datetime.datetime.now()
        content = self.unique()
        def condition_last_modified(self, request, *args, **kwargs):
            return last_modified
        self.assertResponseBehavior({
                "condition_last_modified": condition_last_modified,
                "get": content},
            status_code=200,
            content=content,
            exact_headers={
                "Last-Modified": self.format_datetime(last_modified)})
    
    def test_last_modified_set_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        when no valid last modified header is sent and that a last modified
        header is set on the response.
        
        """
        last_modified = datetime.datetime.now()
        def condition_last_modified(self, request, *args, **kwargs):
            return last_modified
        self.assertResponseBehavior(
            {"condition_last_modified": condition_last_modified},
            status_code=405,
            exact_headers={
                "Last-Modified": self.format_datetime(last_modified)})
    
    def test_last_modified_not_modified(self):
        """
        Check for a not modified response on last modified match.
        
        """
        last_modified = datetime.datetime.now()
        def condition_last_modified(self, request, *args, **kwargs):
            return last_modified
        self.assertResponseBehavior({
                "condition_last_modified": condition_last_modified,
                "get": self.unique()},
            headers={
                "HTTP_IF_MODIFIED_SINCE":
                    self.format_datetime(
                        last_modified + datetime.timedelta(hours=1))},
            status_code=304,
            exact_headers={
                "Last-Modified": self.format_datetime(last_modified)})
    
    def test_last_modified_miss(self):
        """
        Check that the last modified header is updated upon miss.
        
        """
        last_modified = datetime.datetime.now()
        content = self.unique()
        def condition_last_modified(self, request, *args, **kwargs):
            return last_modified + datetime.timedelta(hours=1)
        self.assertResponseBehavior({
                "condition_last_modified": condition_last_modified,
                "get": content},
            headers={
                "HTTP_IF_MODIFIED_SINCE": self.format_datetime(last_modified)},
            status_code=200,
            content=content,
            exact_headers={
                "Last-Modified":
                    self.format_datetime(
                        last_modified + datetime.timedelta(hours=1))})
    
    def test_last_modified_miss_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        upon last modified header miss and that a last modified header is
        set on the response.
        
        """
        last_modified = datetime.datetime.now()
        def condition_last_modified(self, request, *args, **kwargs):
            return last_modified + datetime.timedelta(hours=1)
        self.assertResponseBehavior(
            {"condition_last_modified": condition_last_modified},
            headers={
                "HTTP_IF_MODIFIED_SINCE": self.format_datetime(last_modified)},
            status_code=405,
            exact_headers={
                "Last-Modified":
                    self.format_datetime(
                        last_modified + datetime.timedelta(hours=1))})
