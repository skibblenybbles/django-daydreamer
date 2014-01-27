from __future__ import unicode_literals

from daydreamer.tests.views.generic import base


class TestCase(base.TestCase):
    """
    Common utilities for testing debug view behaviors.
    
    """
    def unique_variable(self):
        """
        Returns a unique variable name.
        
        """
        return "".join(("_", self.unique().replace("-", "_"),))
