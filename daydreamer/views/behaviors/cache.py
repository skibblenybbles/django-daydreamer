from __future__ import unicode_literals

from django.utils.decorators import classonlymethod
from django.views.decorators import cache

from .. import core


__all__ = ("CachePage", "CacheControl", "NeverCache",)


class CachePage(core.http.HttpMethodAllow):
    """
    A view behavior that caches the response during the allow phase of
    the dispatch.
    
    See the django.views.decorators.cache.cache_page() decorator for details.
    
    """
    cache_page = True
    cache_page_timeout = None
    cache_page_cache = None
    cache_page_key_prefix = None
    
    def get_cache_page(self):
        """
        A hook to override the cache_page value.
        
        """
        return self.cache_page
    
    def get_cache_page_timeout(self):
        """
        A hook to override the cache_page_timeout value.
        
        """
        return self.cache_page_timeout
    
    def get_cache_page_cache(self):
        """
        A hook to override the cache_page_cache value.
        
        """
        return self.cache_page_cache
    
    def get_cache_page_key_prefix(self):
        """
        A hook to override the cache_page_key_prefix value.
        
        """
        return self.cache_page_key_prefix
    
    def get_allow_handler(self):
        """
        When cache_page is truthy, wraps the base handler in the
        django.views.decorators.cache.cache_page() decorator.
        
        """
        allow = super(CachePage, self).get_allow_handler()
        if self.get_cache_page():
            allow = cache.cache_page(
                self.get_cache_page_timeout(),
                cache=self.get_cache_page_cache(),
                key_prefix=self.get_cache_page_key_prefix())(allow)
        return allow


class CacheControl(core.http.HttpMethodAllow):
    """
    A view behavior that adds cache control headers to the response during
    the allow phase of the dispatch.
    
    Set the cache_control attribute to a falsy value to disable the behavior.
    
    Set the optional attributes to values other than None to use them. Rather
    having both a public and a private attribute, set public to True or False
    to set either the public or private header value, respectively.
    
    See the django.views.decorators.cache.cache_control() decorator
    for details.
    
    """
    cache_control = True
    cache_control_public = None
    cache_control_no_cache = None
    cache_control_no_transform = None
    cache_control_must_revalidate = None
    cache_control_proxy_revalidate = None
    cache_control_max_age = None
    cache_control_s_maxage = None
    
    def get_cache_control(self):
        """
        A hook to override the cache_control value.
        
        """
        return self.cache_control
    
    def get_cache_control_public(self):
        """
        A hook to override the cache_control_public value.
        
        """
        return self.cache_control_public
    
    def get_cache_control_no_cache(self):
        """
        A hook to override the cache_control_no_cache value.
        
        """
        return self.cache_control_no_cache
    
    def get_cache_control_no_transform(self):
        """
        A hook to override the cache_control_no_transform value.
        
        """
        return self.cache_control_no_transform
    
    def get_cache_control_must_revalidate(self):
        """
        A hook to override the cache_control_must_revalidate value.
        
        """
        return self.cache_control_must_revalidate
    
    def get_cache_control_proxy_revalidate(self):
        """
        A hook to override the cache_control_proxy_revalidate value.
        
        """
        return self.cache_control_proxy_revalidate
    
    def get_cache_control_max_age(self):
        """
        A hook to override the cache_control_max_age value.
        
        """
        return self.cache_control_max_age
    
    def get_cache_control_s_maxage(self):
        """
        A hook to override the cache_control_s_maxage value.
        
        """
        return self.cache_control_s_maxage
    
    def get_allow_handler(self):
        """
        When cache_control is truthy and at least one cache_control_* value
        is set, wraps the base handler in the
        django.views.decorated.cache.cache_control() decorator.
        
        """
        allow = super(CacheControl, self).get_allow_handler()
        if self.get_cache_control():
            public = self.get_cache_control_public()
            no_cache = self.get_cache_control_no_cache()
            no_transform = self.get_cache_control_no_transform()
            must_revalidate = self.get_cache_control_must_revalidate()
            proxy_revalidate = self.get_cache_control_proxy_revalidate()
            max_age = self.get_cache_control_max_age()
            s_maxage = self.get_cache_control_s_maxage()
            controls = dict(
                ((("public", True,),)
                    if public
                    else ()
                        if public is None
                        else (("private", True,),)) +
                ((("no_cache", True,),)
                    if no_cache
                    else ()) +
                ((("no_transform", True,),)
                    if no_transform
                    else ()) +
                ((("must_revalidate", True,),)
                    if must_revalidate
                    else ()) +
                ((("proxy_revalidate", True,),)
                    if proxy_revalidate
                    else ()) +
                ((("max_age", max_age,),)
                    if max_age
                    else ()) +
                ((("s_maxage", s_maxage,),)
                    if s_maxage
                    else ()))
            if controls:
                allow = cache.cache_control(**controls)(allow)
        return allow


class NeverCache(core.http.HttpMethodAllow):
    """
    A view behavior that sets up cache control headings to never cache during
    the allow phase of the dispatch.
    
    Set the never_cache attribute to falsy value to disable the behavior.
    
    See the django.views.decorators.cache.never_cache() decorator for details.
    
    """
    never_cache = True
    
    def get_never_cache(self):
        """
        A hook to override the never_cache value.
        
        """
        return self.never_cache
    
    def get_allow_handler(self):
        """
        When never_cache is truthy, wraps the base handler in
        django.views.decorators.cache.never_cache().
        
        """
        allow = super(NeverCache, self).get_allow_handler()
        if self.get_never_cache():
            allow = cache.never_cache(allow)
        return allow
