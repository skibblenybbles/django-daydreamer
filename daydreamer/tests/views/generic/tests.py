from __future__ import unicode_literals

from daydreamer.views import generic

from . import base


class ViewTestCase(base.TestCase):
    """
    Tests for the base view.
    
    """
    view_class = generic.View
    
    def test_ok(self):
        response = self.client.get(self.view())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "OK")
