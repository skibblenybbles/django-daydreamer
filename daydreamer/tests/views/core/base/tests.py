from __future__ import unicode_literals

from django import http

from daydreamer.core import urlresolvers
from daydreamer.views import core

from . import base


class CoreTestCase(base.TestCase):
    """
    Tests for the Core view base class.
    
    """
    view_classes = core.Core
    
    def test_attachment(self):
        """
        Check that the attachment method behaves correctly.
        
        """
        content = self.unique()
        content_type = "text/plain"
        filename = "{unique:s}.txt".format(unique=self.unique())
        def get(self, request, *args, **kwargs):
            return self.attachment(content, content_type, filename)
        self.assertViewBehavior(
            {"get": get},
            status_code=200,
            content=content,
            headers_exact={
                "Content-Type": content_type,
                "Content-Disposition":
                    "attachment; filename=\"{filename:s}\"".format(
                        filename=filename)})
    
    def test_redirect(self):
        """
        Check that the redirect method behaves correctly.
        
        """
        def get(self, request, *args, **kwargs):
            return self.redirect("admin:index")
        self.assertViewBehavior(
            {"get": get},
            redirect_url=urlresolvers.reverse("admin:index"))
    
    def test_gone(self):
        """
        Check that the gone method gets a 410 resopnse.
        
        """
        def get(self, request, *args, **kwargs):
            return self.gone()
        self.assertViewBehavior(
            {"get": get},
            status_code=410)
    
    def test_not_found(self):
        """
        Check that the not found method gets a 404 response.
        
        """
        def get(self, request, *args, **kwargs):
            return self.not_found()
        self.assertViewBehavior(
            {"get": get},
            status_code=404)
    
    def test_permission_denied(self):
        """
        Check that the permission denied method gets a 403 response.
        
        """
        def get(self, request, *args, **kwargs):
            return self.permission_denied()
        self.assertViewBehavior(
            {"get": get},
            status_code=403)
    
    def test_suspicious_operation(self):
        """
        Check that the suspicious operation method gets a 400 response.
        
        """
        def get(self, request, *args, **kwargs):
            return self.suspicious_operation()
        self.assertViewBehavior(
            {"get": get},
            status_code=400)


class NullTestCase(base.TestCase):
    """
    Tests for the Null view base class.
    
    """
    view_classes = core.Null
    
    def test_get_not_allowed(self):
        """
        Check that GET requests are not allowed.
        
        """
        self.assertViewBehavior(
            {"get": self.unique()},
            status_code=405)
    
    def test_head_not_allowed(self):
        """
        Check that HEAD requests are not allowed.
        
        """
        self.assertViewBehavior(
            {"head": self.unique()},
            method="head",
            status_code=405)
    
    def test_options_not_allowed(self):
        """
        Check that OPTIONS requests are not allowed.
        
        """
        self.assertViewBehavior(
            {"options": self.unique()},
            method="options",
            status_code=405)
    
    def test_post_not_allowed(self):
        """
        Check that POST requests are not allowed.
        
        """
        self.assertViewBehavior(
            {"post": self.unique()},
            method="post",
            status_code=405)
    
    def test_put_not_allowed(self):
        """
        Check that PUT requests are not allowed.
        
        """
        self.assertViewBehavior(
            {"put": self.unique()},
            method="put",
            status_code=405)
    
    def test_patch_not_allowed(self):
        """
        Check that PATCH requests are not allowed.
        
        """
        self.assertViewBehavior(
            {"patch": self.unique()},
            method="patch",
            status_code=405)
    
    def test_delete_not_allowed(self):
        """
        Check that DELETE requests are not allowed.
        
        """
        self.assertViewBehavior(
            {"delete": self.unique()},
            method="delete",
            status_code=405)


class DenyTestCase(NullTestCase):
    """
    Tests for the Deny view base class.
    
    """
    view_classes = core.Deny
    
    def test_deny_handler(self):
        """
        Check that a custom deny handler takes precedence.
        
        """
        content = self.unique()
        def custom_deny(self, request, *args, **kwargs):
            return http.HttpResponse(content)
        def get_deny_handler(self):
            return self.custom_deny
        self.assertViewBehavior({
                "custom_deny": custom_deny,
                "get_deny_handler": get_deny_handler},
            status_code=200,
            content=content)


class AllowTestCase(NullTestCase):
    """
    Tests for the Allow view base class.
    
    """
    view_classes = core.Allow
    
    def test_allow_handler(self):
        """
        Check that a custom allow handler takes precedence.
        
        """
        content = self.unique()
        def custom_allow(self, request, *args, **kwargs):
            return http.HttpResponse(content)
        def get_allow_handler(self):
            return self.custom_allow
        self.assertViewBehavior({
                "custom_allow": custom_allow,
                "get_allow_handler": get_allow_handler},
            status_code=200,
            content=content)
