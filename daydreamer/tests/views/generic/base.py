from __future__ import unicode_literals

from daydreamer.core import lang
from daydreamer.test import views as test_views


class TestCase(test_views.TestCase):
    """
    Common utilities for testing base views.
    
    Specify a view class to use for the test cases.
    
    """
    view_class = None
    
    def view(self, *args, **kwargs):
        """
        Hardcodes self.view_class.
        
        """
        return super(TestCase, self).view(self.view_class, *args, **kwargs)
