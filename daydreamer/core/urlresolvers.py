from __future__ import unicode_literals

import urlparse

from django.contrib.sites.models import RequestSite, Site
from django.core import urlresolvers
from django.utils.functional import lazy


__all__ = ("reverse", "reverse_lazy", "resolve",)


def reverse(viewname, qualified=False, scheme=None, request=None, **kwargs):
    """
    Reverses the URL of the given view name with other optional arguments to
    django.core.urlresolvers.reverse(). If qualified is True, the URL will be
    fully qualified. The URL scheme may be specified with the scheme argument,
    defaulting to 'http'. By default, the hostname will come from the current
    django.contrib.sites.models.Site object. Alternatively, the scheme and
    hostname may be specified by a django.http.request.HttpRequest object
    passed in the request argument.
    
    If qualfied is True, no request is specified and the django.contrib.sites
    app is not installed and configured, an exception will be raised.
    
    If qualified is True and both a scheme and request are specified, the
    passed scheme will take precedence over the request's scheme.
    
    """
    url = urlresolvers.reverse(viewname, **kwargs)
    if qualified:
        path = "{scheme:s}://{host:s}{url:s}".format(
            scheme=scheme \
                if scheme is not None \
                else "http" \
                    if request is None \
                    else "https" \
                        if request.is_secure() \
                        else "http",
            host=RequestSite(request).domain \
                if request is not None \
                else Site.objects.get_current().domain,
            url=url)
    return url


reverse_lazy = lazy(reverse, str)


def resolve(url, scheme=None, request=None, **kwargs):
    """
    Resolves the given URL by passing its path and other optional arguments to
    django.core.urlresolvers.resolve(). For fully qualified URLs, the URL
    scheme and hostname will be checked, and a ValueError will be raised upon
    mismatch. The URL scheme may be specified with the scheme argument,
    defaulting to 'http'. By default, the hostname will come from the current
    django.contrib.sites.models.Site object. Alternatively, the scheme and
    hostname may be specified by a django.http.request.HttpRequest object
    passed in the request argument.
    
    For fully qualified URLs, if no request is specified and the
    django.contrib.sites app is not installed and configured, an exception
    will be raised.
    
    For fully qualified URLs, if both a scheme and a request are specified,
    the passed scheme will take precedence over the request's scheme.
    
    """
    parts = urlparse.urlparse(url)
    if (parts.scheme and \
        parts.scheme != (scheme \
            if scheme is not None \
            else "http" \
                if request is None \
                else "https" \
                    if request.is_secure() \
                    else "http")) or \
        (parts.netloc and \
        parts.netloc != (RequestSite(request).domain \
            if request is not None \
            else Site.objects.get_current().domain)):
        raise ValueError(
            "The fully qualified URL's scheme and host are invalid for "
            "this host.")
    return urlresolvers.resolve(parts.path)
