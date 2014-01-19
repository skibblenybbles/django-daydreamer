from __future__ import unicode_literals

from django.utils import six

from daydreamer.core import lang
from daydreamer.test import messages as test_messages, views as test_views


class TestCase(test_messages.TestCase, test_views.TestCase):
    """
    Common utilities for testing auth decorated views.
    
    Specify a view class to use for the test cases and a prefix to use
    for the prefixedattrs passed to self.view().
    
    """
    view_class = None
    prefix = None
    
    def prefixed(self, prefix, data):
        """
        Returns a copy of the data dictionary with all its keys prefixed
        by prefix.
        
        """
        return dict(
            ("_".join((prefix, key)), value)
            for key, value in six.iteritems(data))
    
    def view(self, prefixedattrs=None, staticattrs=None, **kwargs):
        """
        Mixes the specified attributes that should be prefixed into the static
        attributes dictionary and defers to super().
        
        """
        return super(TestCase, self).view(
            self.view_class, staticattrs=lang.updated(
                staticattrs or {},
                self.prefixed(self.prefix, prefixedattrs or {})),
            **kwargs)
