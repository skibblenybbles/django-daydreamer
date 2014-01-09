from __future__ import unicode_literals

from django.views import generic

from .base import View


__all__ = ("FormView", "CreateView", "UpdateView", "DeleteView",)


class FormView(generic.FormView, View):
    """
    Extends Django's FormView class with features from
    daydreamer.views.generic.View.
    
    """
    pass


class CreateView(generic.CreateView, View):
    """
    Extends Django's CreateView class with features from
    daydreamer.views.generic.View.
    
    """
    pass


class UpdateView(generic.UpdateView, View):
    """
    Extends Django's UpdateView class with features from
    daydreamer.views.generic.View.
    
    """
    pass


class DeleteView(generic.DeleteView, View):
    """
    Extends Django's DeleteView class with features from
    daydreamer.views.generic.View.
    
    """
    pass

