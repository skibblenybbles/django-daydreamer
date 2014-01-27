from __future__ import unicode_literals

from .. import redirects
from . import base


class TestCase(redirects.TestCase, base.TestCase):
    """
    A test case for making assertions about redirects for views.
    
    """
    # Assertions.
    def assertRedirects(self, *args, **kwargs):
        """
        Patches redirect assertion to ensure that the client's base get() method
        and original request handler are used.
        
        """
        with self.client.base_implementation:
            return super(TestCase, self).assertRedirects(*args, **kwargs)
