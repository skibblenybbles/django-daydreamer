from __future__ import unicode_literals

from django.views import generic

from daydreamer.views import core


__all__ = ("View", "TemplateView", "RedirectView",)


class View(core.HttpMethodDeny, core.HttpMethodAllow):
    """
    A replacement for django.views.generic.View. Implements a dispatch system
    with improved tools for denying or allowing a request to be processed.
    
    """
    pass


class TemplateView(generic.TemplateView, View):
    """
    Extends Django's TemplateView class with features from
    daydreamer.views.generic.View.
    
    """
    pass


class RedirectView(generic.RedirectView, View):
    """
    Extends Django's RedirectView class with features from
    daydreamer.views.generic.View.
    
    """
    pass
