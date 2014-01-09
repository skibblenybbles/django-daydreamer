from __future__ import unicode_literals

from django.views import generic

from .base import View


__all__ = (
    "ArchiveIndexView", "YearArchiveView", "MonthArchiveView",
    "WeekArchiveView", "DayArchiveView", "TodayArchiveView", "DateDetailView",)


class ArchiveIndexView(generic.ArchiveIndexView, View):
    """
    Extends Django's ArchiveIndexView class with features from
    daydreamer.views.generic.View.
    
    """
    pass


class YearArchiveView(generic.YearArchiveView, View):
    """
    Extends Django's YearArchiveView class with features from
    daydreamer.views.generic.View.
    
    """
    pass


class MonthArchiveView(generic.MonthArchiveView, View):
    """
    Extends Django's MonthArchiveView class with features from
    daydreamer.views.generic.View.
    
    """
    pass


class WeekArchiveView(generic.WeekArchiveView, View):
    """
    Extends Django's WeekArchiveView class with features from
    daydreamer.views.generic.View.
    
    """
    pass


class DayArchiveView(generic.DayArchiveView, View):
    """
    Extends Django's DayArchiveView class with features from
    daydreamer.views.generic.View.
    
    """
    pass


class TodayArchiveView(generic.TodayArchiveView, View):
    """
    Extends Django's TodayArchiveView class with features from
    daydreamer.views.generic.View.
    
    """
    pass


class DateDetailView(generic.DateDetailView, View):
    """
    Extends Django's DateDetailView class with features from
    daydreamer.views.generic.View.
    
    """
    pass
