from __future__ import unicode_literals

from django.views import generic

from .base import View


__all__ = ("DetailView",)


class DetailView(generic.DetailView, View):
    """
    Extends Django's DetailView class with features from
    daydreamer.views.generic.View.
    
    """
    pass
