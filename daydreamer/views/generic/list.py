from __future__ import unicode_literals

from django.views import generic

from .base import View


__all__ = ("ListView",)


class ListView(generic.ListView, View):
    """
    Extends Django's ListView class with features from
    daydreamer.views.generic.View.
    
    """
    pass
