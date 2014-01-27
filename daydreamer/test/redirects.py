from __future__ import unicode_literals

import functools
import urlparse

from django.http import request

from daydreamer.core import lang, urlresolvers

from . import base


class TestCase(base.TestCase):
    """
    A test case for making assertions about redirects.
    
    """
    def assertRedirects(self, response, expected_url, query=None,
            status_code=302, target_status_code=None, host=None,
            msg_prefix=""):
        """
        Asserts that the response was redirected as expected. If provided,
        the query dictionary is added to the expected URL's query string. If
        the target status code is not specified, no assertion of its value
        will be performed.
        
        """
        # If unspecified, make sure the target status code will match the
        # base implementation's expected code.
        if target_status_code is None:
            if getattr(response, "redirect_chain", None):
                target_status_code = response.status_code
            else:
                parts = urlparse.urlparse(response.url)
                target_status_code = response.client.get(
                    parts.path, request.QueryDict(parts.query)).status_code
        
        return super(TestCase, self).assertRedirects(
            response, urlresolvers.update_query(expected_url, query),
            status_code=status_code, target_status_code=target_status_code,
            host=host, msg_prefix=msg_prefix)
    
    def create_redirect_assertions(self, expected_url=None, query=None,
            status_code=302, target_status_code=None):
        """
        Returns a tuple of redirect assertion callbacks for the
        given arguments.
        
        """
        return (
            (functools.partial(self.assertRedirects,
                expected_url=expected_url, query=query,
                status_code=status_code,
                target_status_code=target_status_code),)
                if expected_url is not None
                else ())
    
    def create_response_assertions(self, redirect_url=None,
            redirect_next_url=None, redirect_next_name=None,
            redirect_status_code=None, redirect_target_status_code=None,
            **kwargs):
        """
        Adds redirect assertions to the response assertions.
        
        """
        return (
            self.create_redirect_assertions(
                expected_url=redirect_url,
                query=(
                    {redirect_next_name: redirect_next_url}
                        if redirect_next_name
                        else None),
                status_code=(
                    redirect_status_code
                        if redirect_status_code is not None
                        else 302),
                target_status_code=redirect_target_status_code) +
            super(TestCase, self).create_response_assertions(**kwargs))
