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
