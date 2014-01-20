from __future__ import unicode_literals

from daydreamer.core import urlresolvers
from daydreamer.views import generic

from . import base


class SecuredViewTestCase(base.TestCase):
    """
    Tests for the SecuredView base class.
    
    """
    view_class = generic.base.SecuredView
    
    def test_not_implemented(self):
        """
        Check that a simple request handler is not implemented.
        
        """
        self.assertResponseBehavior(
            self.unique(),
            view_kwargs={"get": self.unique()},
            exception=NotImplementedError)


class CommonResponseViewTestCase(base.TestCase):
    """
    Tests for the CommonResponseView base class.
    
    """
    view_class = generic.base.CommonResponseView
    
    def test_attachment(self):
        """
        Check that the attachment method behaves correctly.
        
        """
        content = self.unique()
        content_type = "text/plain"
        filename = "{unique:s}.txt".format(unique=self.unique())
        def get(self, request, *args, **kwargs):
            return self.attachment(content, content_type, filename)
        self.assertResponseBehavior(
            self.unique(),
            view_attrs={"get": get},
            status_code=200,
            content=content,
            headers={
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
        self.assertResponseBehavior(
            self.unique(),
            view_attrs={"get": get},
            redirect_url=urlresolvers.reverse("admin:index"))
    
    def test_gone(self):
        """
        Check that the gone method gets a 410 resopnse.
        
        """
        def get(self, request, *args, **kwargs):
            return self.gone()
        self.assertResponseBehavior(
            self.unique(),
            view_attrs={"get": get},
            status_code=410)
    
    def test_not_found(self):
        """
        Check that the not found method gets a 404 response.
        
        """
        def get(self, request, *args, **kwargs):
            return self.not_found()
        self.assertResponseBehavior(
            self.unique(),
            view_attrs={"get": get},
            status_code=404)
    
    def test_permission_denied(self):
        """
        Check that the permission denied method gets a 403 response.
        
        """
        def get(self, request, *args, **kwargs):
            return self.permission_denied()
        self.assertResponseBehavior(
            self.unique(),
            view_attrs={"get": get},
            status_code=403)
    
    def test_suspicious_operation(self):
        """
        Check that the suspicious operation method gets a 400 response.
        
        """
        def get(self, request, *args, **kwargs):
            return self.suspicious_operation()
        self.assertResponseBehavior(
            self.unique(),
            view_attrs={"get": get},
            status_code=400)


class ViewTestCase(base.TestCase):
    """
    Tests for the View base class.
    
    """
    view_class = generic.View
    
    def test_ok(self):
        """
        Check a simple request.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            self.unique(),
            view_kwargs={"get": content},
            status_code=200,
            content=content)
    
    def test_method_missing(self):
        """
        Check that missing methods get a 405 response.
        
        """
        self.assertResponseBehavior(
            self.unique(),
            status_code=405)
    
    def test_method_not_allowed(self):
        """
        Check that disallowed methods get a 405 response.
        
        """
        self.assertResponseBehavior(
            self.unique(),
            view_attrs={"http_method_names": ()},
            view_kwargs={"get": self.unique()})
