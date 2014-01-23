from __future__ import unicode_literals

from django.utils.decorators import classonlymethod
from django.views.decorators import gzip

from .. import generic


__all__ = ("GZipPage",)


class GZipPage(generic.View):
    """
    A view behavior that gzips the response's content at the top level of
    the dispatch.
    
    Set the gzip_page attribute to a falsy value to disable the behavior.
    
    See the django.views.decorators.gzip.gzip_page() for details.
    
    """
    gzip_page = True
    
    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Optionally decorates the base view with
        django.views.decorators.gzip.gzip_page().
        
        """
        view = super(GZipPage, cls).as_view(**kwargs)
        return gzip.gzip_page(view) if cls.gzip_page else view
