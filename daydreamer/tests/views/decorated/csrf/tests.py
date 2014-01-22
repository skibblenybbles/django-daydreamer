from __future__ import unicode_literals

from django import http, template
from django.conf import settings

from daydreamer.views.decorated import csrf as csrf_decorated

from . import base


class CSRFProtectTestCase(base.TestCase):
    """
    Tests for the CSRFProtect view behavior.
    
    CSRF middleware is turned off to enable edge case behavior.
    
    """
    view_classes = csrf_decorated.CSRFProtect
    
    def test_protect_post_no_cookie(self):
        """
        Check that POST requests without a cookie are CSRF protected.
        
        """
        self.assertResponseBehavior(
            {"post": self.unique()},
            method="post",
            status_code=403)
    
    def test_protect_post_cookie(self):
        """
        Check that POST requests with a cookie are CSRF protected.
        
        """
        self.client.set_csrf_cookie()
        self.test_protect_post_no_cookie()
    
    def test_protect_put_no_cookie(self):
        """
        Checks that PUT requests without a cookie are CSRF protected.
        
        """
        self.assertResponseBehavior(
            {"put": self.unique()},
            method="put",
            status_code=403)
    
    def test_protect_put_cookie(self):
        """
        Checks that PUT requsets with a cookie are CSRF protected.
        
        """
        self.client.set_csrf_cookie()
        self.test_protect_put_no_cookie()
    
    def test_protect_patch_no_cookie(self):
        """
        Checks that PATCH requests without a cookie are CSRF protected.
        
        """
        self.assertResponseBehavior(
            {"patch": self.unique()},
            method="patch",
            status_code=403)
    
    def test_protect_patch_cookie(self):
        """
        Checks that PATCH requests with a cookie are CSRF protected.
        
        """
        self.client.set_csrf_cookie()
        self.test_protect_patch_no_cookie()
    
    def test_protect_delete_no_cookie(self):
        """
        Checks that DELETE requests without a cookie are CSRF protected.
        
        """
        self.assertResponseBehavior(
            {"delete": self.unique()},
            method="delete",
            status_code=403)
    
    def test_protect_delete_cookie(self):
        """
        Checks that DELETE requests with a cookie are CSRF protected.
        
        """
        self.client.set_csrf_cookie()
        self.test_protect_delete_no_cookie()
    
    def test_protect_precedence_no_cookie(self):
        """
        Checks that requests without a cookie are CSRF protected, taking
        precedence over the default HTTP method name protection.
        
        """
        self.assertResponseBehavior(
            method="post",
            status_code=403)
    
    def test_protect_precedence_cookie(self):
        """
        Checks that requests with a cookie are CSRF protected, taking
        precedence over the default HTTP method name protection.
        
        """
        self.client.set_csrf_cookie()
        self.test_protect_precedence_no_cookie()
    
    def test_allow_post_data(self):
        """
        Check that POST requests are allowed with a CSRF cookie and appropriate
        POST data.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"post": content},
            method="post",
            data={"csrfmiddlewaretoken": self.client.get_csrf_cookie()},
            status_code=200,
            content=content)
    
    def test_allow_post_header(self):
        """
        Check that POST requests are allowed with a CSRF cookie and an
        appropriate header.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"post": content},
            method="post",
            headers={"HTTP_X_CSRFTOKEN": self.client.get_csrf_cookie()},
            status_code=200,
            content=content)
    
    def test_allow_post_disabled(self):
        """
        Check that POST requests are allowed when the view decorator
        is disabled.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"csrf_protect": False, "post": content},
            method="post",
            status_code=200,
            content=content)
    
    def test_allow_put_header(self):
        """
        Check that PUT requests are allowed with a CSRF cookie and an
        appropriate header.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"put": content},
            method="put",
            headers={"HTTP_X_CSRFTOKEN": self.client.get_csrf_cookie()},
            status_code=200,
            content=content)
    
    def test_allow_put_disabled(self):
        """
        Check that PUT requests are allowed when the view decorator
        is disabled.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"csrf_protect": False, "put": content},
            method="put",
            status_code=200,
            content=content)
    
    def test_allow_patch_header(self):
        """
        Check that PATCH requests are allowed with a CSRF cookie and an
        appropriate header.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"patch": content},
            method="patch",
            headers={"HTTP_X_CSRFTOKEN": self.client.get_csrf_cookie()},
            status_code=200,
            content=content)
    
    def test_allow_patch_disabled(self):
        """
        Check that PATCH requests are allowed when the view decorator
        is disabled.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"csrf_protect": False, "patch": content},
            method="patch",
            status_code=200,
            content=content)
    
    def test_allow_delete_header(self):
        """
        Check that DELETE requests are allowed with a CSRF cookie and an
        appropriate header.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"delete": content},
            method="delete",
            headers={"HTTP_X_CSRFTOKEN": self.client.get_csrf_cookie()},
            status_code=200,
            content=content)
    
    def test_allow_delete_disabled(self):
        """
        Check that DELETE requests are allowed when the view decorator
        is disabled.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"csrf_protect": False, "delete": content},
            method="delete",
            status_code=200,
            content=content)
    
    def test_allow_precedence_data(self):
        """
        Check that a POST request is allowed with a CSRF cookie and appropriate
        POST data and that the default HTTP method name protection
        takes precedence.
        
        """
        self.assertResponseBehavior(
            method="post",
            data={"csrfmiddlewaretoken": self.client.get_csrf_cookie()},
            status_code=405)
    
    def test_allow_precedence_header(self):
        """
        Check that a POST request is allowed with a CSRF cookie and an
        appropriate header and that the default HTTP method name protection
        takes precedence.
        
        """
        self.assertResponseBehavior(
            method="post",
            headers={"HTTP_X_CSRFTOKEN": self.client.get_csrf_cookie()},
            status_code=405)


class RequireCSRFTokenTestCase(base.TestCase):
    """
    Tests for the RequiresCSRFToken view behavior.
    
    CSRF middleware is turned off to enable edge case behavior.
    
    """
    view_classes = csrf_decorated.RequiresCSRFToken
    
    def test_csrf_token(self):
        """
        A csrf_token value should be added to a RequestContext.
        
        """
        content = self.unique()
        def get(self, request, *args, **kwargs):
            return http.HttpResponse(
                template.Template(content).render(
                    template.RequestContext(request, {})))
        self.assertResponseBehavior(
            {"get": get},
            status_code=200,
            content=content,
            include_context="csrf_token")
    
    def test_csrf_token_disabled(self):
        """
        A csrf_token value should be added to a RequestContext even when the
        view decorator is disabled, because of a hard-coded logic path
        in Django's RequestContext code.
        
        This shows that this view behavior is not very useful.
        
        """
        content = self.unique()
        def get(self, request, *args, **kwargs):
            return http.HttpResponse(
                template.Template(content).render(
                    template.RequestContext(request, {})))
        self.assertResponseBehavior(
            {"requires_csrf_token": False, "get": get},
            status_code=200,
            content=content,
            include_context="csrf_token")


class EnsureCSRFCookieTestCase(base.TestCase):
    """
    Tests for the EnsureCSRFCookie view behavior.
    
    CSRF middleware is turned off to enable edge case behavior.
    
    """
    view_classes = csrf_decorated.EnsureCSRFCookie
    
    def test_csrf_cookie(self):
        """
        Check that the CSRF cookie appears in the response.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"get": content},
            status_code=200,
            content=content,
            include_cookies=settings.CSRF_COOKIE_NAME)
    
    def test_csrf_cookie_disabled(self):
        """
        Check that the CSRF cookie does not appear in the response.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"ensure_csrf_cookie": False, "get": content},
            status_code=200,
            content=content,
            exclude_cookies=settings.CSRF_COOKIE_NAME)


class CSRFExemptTestCase(base.TestCase):
    """
    Tests for the CSRFExempt view behavior.
    
    CSRF middleware is turned on to enable edge case behavior.
    
    """
    view_classes = csrf_decorated.CSRFExempt
    csrf_middleware_enabled = True
    
    def test_post_csrf_exempt(self):
        """
        Check that POST requests are CSRF exempt.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"post": content},
            method="post",
            status_code=200,
            content=content)
    
    def test_put_csrf_exempt(self):
        """
        Check that PUT requests are CSRF exempt.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"put": content},
            method="put",
            status_code=200,
            content=content)
    
    def test_patch_csrf_exempt(self):
        """
        Check that PATCH requests are CSRF exempt.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"patch": content},
            method="patch",
            status_code=200,
            content=content)
    
    def test_delete_csrf_exempt(self):
        """
        Check that DELETE requests are CSRF exempt.
        
        """
        content = self.unique()
        self.assertResponseBehavior(
            {"delete": content},
            method="delete",
            status_code=200,
            content=content)
    
    def test_post_csrf_exempt_disabled(self):
        """
        Check that POST requests are protected when the decorator
        is disabled.
        
        """
        self.assertResponseBehavior(
            {"csrf_exempt": False, "post": self.unique()},
            method="post",
            status_code=403)
    
    def test_put_csrf_exempt_disabled(self):
        """
        Check that PUT requests are protected when the decorator
        is disabled.
        
        """
        self.assertResponseBehavior(
            {"csrf_exempt": False, "put": self.unique()},
            method="put",
            status_code=403)
    
    def test_patch_csrf_exempt_disabled(self):
        """
        Check that PATCH requests are protected when the decorator
        is disabled.
        
        """
        self.assertResponseBehavior(
            {"csrf_exempt": False, "patch": self.unique()},
            method="patch",
            status_code=403)
    
    def test_post_csrf_exempt_disabled(self):
        """
        Check that DELETE requests are protected when the decorator
        is disabled.
        
        """
        self.assertResponseBehavior(
            {"csrf_exempt": False, "delete": self.unique()},
            method="delete",
            status_code=403)


class CSRFProtectCSRFExemptTestCase(CSRFExemptTestCase):
    """
    Tests for views inheriting from CSRFProtect followed by CSRFExempt.
    
    CSRF middleware is turned off to enable edge case behavior.
    
    This demonstrates the correct inheritance pattern to follow if you
    want easy control over CSRF protection in an environment with CSRF
    middleware disabled.
    
    """
    view_classes = (csrf_decorated.CSRFProtect, csrf_decorated.CSRFExempt,)
    csrf_middleware_enabled = False
