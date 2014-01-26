from __future__ import unicode_literals

from .. import base
from . import client


__all__ = ("TestCase",)


class TestCase(base.TestCase):
    """
    A test case for testing views without using the URL resolution framework
    by employing a customized test client and request handler.
    
    See daydreamer.test.views.client and daydreamer.test.views.handler
    for implementation details.
    
    """
    client_class = client.Client
    
    def unique_path(self):
        """
        Returns a unique path for use in testing views.
        
        While operating outside of the URL resolution framework, this should be
        used to generate a path to pass to the client to verify that a view's
        behavior is independent of the request's path.
        
        """
        return "/{unique:s}/".format(unique=self.unique())
