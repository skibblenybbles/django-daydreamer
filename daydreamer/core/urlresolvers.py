from __future__ import unicode_literals

import urlparse

from django.contrib.sites.models import Site
from django.core import urlresolvers
from django.http import request
from django.utils import encoding
from django.utils.functional import lazy

from . import lang


__all__ = (
    "NoReverseMatch", "resolve", "reverse", "reverse_lazy",
    "simplify_redirect", "update_query",)


NoReverseMatch = urlresolvers.NoReverseMatch


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
    if ((
        parts.scheme and
        parts.scheme != (scheme
            if scheme is not None
            else "http"
                if request is None
                else "https"
                    if request.is_secure()
                    else "http")) or (
        parts.netloc and
        parts.netloc != request.get_host()
            if request is not None
            else Site.objects.get_current().domain)):
        raise ValueError(
            "The fully qualified URL's scheme or hostname are invalid for "
            "this host.")
    return urlresolvers.resolve(parts.path)


def reverse(viewname, qualified=False, scheme=None, request=None, **kwargs):
    """
    Reverses the URL of the given view name with other optional arguments to
    django.core.urlresolvers.reverse(). If qualified is True, the URL will be
    fully qualified. The URL scheme may be specified with the scheme argument,
    defaulting to "http". By default, the hostname will come from the current
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
            scheme=(
                scheme
                    if scheme is not None
                    else "http"
                        if request is None
                        else "https"
                            if request.is_secure()
                            else "http"),
            host=(
                request.get_host()
                    if request is not None
                    else Site.objects.get_current().domain),
            url=url)
    return url


reverse_lazy = lazy(reverse, str)


def simplify_redirect(redirect, source, request=None):
    """
    Simplifies a redirect URL with respect to a source URL and returns the
    redirect URL. When both URLs' scheme and host match, the scheme and host
    are stripped from the redirect URL. When a request is specified, its
    scheme and host are also used to simplify the redirect URL.
    
    """
    redirect = urlparse.urlparse(encoding.force_str(redirect))
    source = urlparse.urlparse(encoding.force_str(source))
    empty = ("", "",)
    request = (
        ("https" if request.is_secure() else "http", request.get_host(),)
            if request is not None
            else empty)
    if (redirect[:2] != empty and (
            redirect[:2] == source[:2] or
            (redirect[:2] == request and source[:2] == empty))):
        redirect = empty + redirect[2:]
    return urlparse.urlunparse(redirect)


def update_query(url, data):
    """
    Update a URL's query string with additional data. The data may be a
    dictionary or an instance of django.utils.datastructures.MultiValueDict.
    The URL should be a string or a lazy string.
    
    """
    url = encoding.force_str(url)
    parts = urlparse.urlparse(url)
    return urlparse.urlunparse(
        parts[:4] +
        (lang.updated(
            request.QueryDict(parts.query, mutable=True),
            data or {}).urlencode(safe="/"),) +
        parts[5:])
