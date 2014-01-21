from __future__ import unicode_literals

from django.utils.decorators import classonlymethod
from django.views.decorators import csrf

from .. import generic


__all__ = (
    "CSRFProtect", "RequiresCSRFToken", "EnsureCSRFCookie", "CSRFExempt",)


class CSRFProtect(generic.View):
    """
    A view decorator mixin that adds CSRF protection to a view the same
    way as CsrfViewMiddleware.
    
    Disable the view decorator's functionality by setting the csrf_protect
    attribute to a falsy value. Note that this is not the same as making the
    view exempt from CSRF checks (see CSRFExempt).
    
    """
    csrf_protect = True
    
    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Decorates the returned view function with
        django.views.decorators.csrf.csrf_protect().
        
        """
        view = super(CSRFProtect, cls).as_view(**kwargs)
        return csrf.csrf_protect(view) if cls.csrf_protect else view


class RequiresCSRFToken(generic.View):
    """
    A view decorator mixin that ensures "csrf_token" will be present
    in the request context, but does not enforce CSRF protection.
    
    Disable the view decorator's functionality by setting the
    requires_csrf_token attribute to a falsy value.
    
    """
    requires_csrf_token = True
    
    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Decorates the returned view function with
        django.views.decorators.csrf.requires_csrf_token().
        
        """
        view = super(RequiresCSRFToken, cls).as_view(**kwargs)
        return (
            csrf.requires_csrf_token(view)
                if cls.requires_csrf_token
                else view)


class EnsureCSRFCookie(generic.View):
    """
    A view decorator mixin that ensures a CSRF cookie will be present
    in the response, but does not enforce CSRF protection.
    
    Disable the view decorator's functionality by setting the
    ensure_csrf_cookie attribute to a falsy value.
    
    """
    ensure_csrf_cookie = True
    
    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Decorates the returned view function with
        django.views.decorators.csrf.ensure_csrf_cookie().
        
        """
        view = super(EnsureCSRFCookie, cls).as_view(**kwargs)
        return (
            csrf.ensure_csrf_cookie(view)
                if cls.ensure_csrf_cookie
                else view)


class CSRFExempt(generic.View):
    """
    A view decorator mixin that disables CSRF protection.
    
    Disable the view decorator's functionality by setting the
    csrf_exampt attribute to a falsy value.
    
    """
    csrf_exempt = True
    
    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Decorates the returned view function with
        django.views.decorators.csrf.csrf_exempt().
        
        """
        view = super(CSRFExempt, cls).as_view(**kwargs)
        return csrf.csrf_exempt(view) if cls.csrf_exempt else view
