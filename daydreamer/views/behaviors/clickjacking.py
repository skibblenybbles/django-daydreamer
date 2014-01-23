from __future__ import unicode_literals

from django.utils.decorators import classonlymethod
from django.views.decorators import clickjacking

from .. import generic


__all__ = (
    "XFrameOptionsDeny", "XFrameOptionsSameOrigin", "XFrameOptionsExempt",)


class XFrameOptionsDeny(generic.View):
    """
    A view behavior that adds a DENY X-Frame-Options header to the response
    at the top level of the dispatch.
    
    Set the xframe_options_deny attribute to a falsy value to disable
    the behavior.
    
    See the django.views.decorators.clickjacking.xframe_options_deny()
    decorator for details.
    
    """
    xframe_options_deny = True
    
    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Optionally decorates the base view with the
        django.views.decorators.clickjacking.xframe_options_deny() decorator.
        
        """
        view = super(XFrameOptionsDeny, cls).as_view(**kwargs)
        return (
            clickjacking.xframe_options_deny(view)
                if cls.xframe_options_deny
                else view)


class XFrameOptionsSameOrigin(generic.View):
    """
    A view behavior that adds a SAMEORIGIN X-Frame-Options header to the
    response at the top level of the dispatch.
    
    Set the xframe_options_same_origin attribute to a falsy value to disable
    the behavior.
    
    See the django.views.decorators.clickjacking.xframe_options_sameorigin()
    decorator for details.
    
    """
    xframe_options_same_origin = True
    
    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Optionally decorates the base view with the
        django.views.decorators.clickjacking.xframe_options_sameorigin()
        decorator.
        
        """
        view = super(XFrameOptionsSameOrigin, cls).as_view(**kwargs)
        return (
            clickjacking.xframe_options_sameorigin(view)
                if cls.xframe_options_same_origin
                else view)


class XFrameOptionsExempt(generic.View):
    """
    A view behavior that marks the response as exempt from protection so that
    the middleware does not add an X-Frame-Options header.
    
    Set the xframe_options_exempt attribute to a falsy value to disable
    the behavior.
    
    See the django.views.decorators.clickjacking.xframe_options_exempt()
    decorator for details.
    
    """
    xframe_options_exempt = True
    
    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Optionally decorates the base view with the
        django.views.decorators.clickjacking.xframe_options_exempt() decorator.
        
        """
        view = super(XFrameOptionsExempt, cls).as_view(**kwargs)
        return (
            clickjacking.xframe_options_exempt(view)
                if cls.xframe_options_exempt
                else view)
