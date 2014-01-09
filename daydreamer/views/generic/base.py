from __future__ import unicode_literals

from django import http
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from daydreamer.core import lang, urlresolvers


class View(generic.View):
    """
    Extends Django's base view class with helpful features for reversing URLs
    and returning common responses, including file attachments, redirects
    (301 and 302) and gone (410). Helpers that raise appropriate exceptions
    for not found (404), permission denied (403) and suspicious operation (400)
    are also provided.
    
    The not modified (304), not allowed (405) and server error (500) responses
    are not provided, as they are handled automatically by other Django mechanisms.
    
    Even though the not_found(), permission_denied() and suspicious_operation()
    methods raise exceptions, it is recommended to return the responses from
    these calls for stylistic consistency, e.g.:
    
    # Do this:
    if resource.not_available():
        return self.not_found()
    
    # Not this:
    if resource.not_available():
        self.not_found()
    
    Since these methods raise exceptions, rather than return responses, take
    care to avoid catching their exceptions, or Django's special response
    exception handling machinery will be neutralized.
    
    """
    def reverse(self, viewname, qualified=False, scheme=None, **kwargs):
        """
        Reverse a URL from the given viewname and other optional arguments to
        django.contrib.urlresolvers.reverse(). If qualified is True, the result
        will include the URL scheme and host. If the scheme is also specified,
        it will take precedence over the current request's scheme.
        
        """
        return urlresolvers.reverse(viewname, **lang.updated(kwargs, {
            'qualified': True, 'scheme': scheme, 'request': self.request} \
                if qualified \
                else {},
            copy=True))
    
    def attachment(self, data, content_type, filename):
        """
        Returns a file attachment response with the data as its payload
        and the specified content type (MIME type) and filename.
        
        """
        return lang.updated(
            http.HttpResponse(data, content_type=content_type), {
                "Content-Disposition": \
                    "attachment; filename=\"{filename:s}\"".format(
                        filename=filename)})
    
    def redirect(self, viewname, permanent=False, **kwargs):
        """
        Returns a 301 or 302 redirect response with the reversed URL from the
        given viewname and other optional arguments to View.reverse().
        If permanent is True, the redirect will be a permanent 301 redirect.
        Otherwise, it will be a temporary 302 redirect.
        
        """
        return (http.HttpResponsePermanentRedirect \
            if permanent else http.HttpResponseRedirect)(
                self.reverse(viewname, **kwargs))
    
    def gone(self):
        """
        Returns a 410 gone response.
        
        """
        return http.HttpResponseGone()
    
    def not_found(self):
        """
        Raises an Http404 exception to trigger the 404 not found response
        machinery.
        
        """
        raise http.Http404
    
    def permission_denied(self):
        """
        Raises a PermissionDenied exception to trigger the 403 forbidden
        response machinery.
        
        """
        raise exceptions.PermissionDenied
    
    def suspicious_operation(self):
        """
        Raises a SuspiciousOperation exception to trigger the 400 bad request
        response machinery.
        
        """
        raise exceptions.SuspiciousOperation
