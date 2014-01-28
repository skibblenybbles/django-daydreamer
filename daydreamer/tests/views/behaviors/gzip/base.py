from __future__ import unicode_literals

from django.utils.text import compress_string

from daydreamer.tests.views import generic


class TestCase(generic.TestCase):
    """
    Common utilities for testing gzip view behaviors.
    
    """
    def compress(self, text):
        """
        Returns a compressed version of the given text, using the same
        function as Django's gzip decorator and middleware.
        
        """
        return compress_string(text)
    
    def unique_gzip(self):
        """
        Returns a unique string that satisifies the requirements for Django's
        gzip compression middleware.
        
        """
        # Content must have a length of at least 200, and it must be shorter
        # when gzipped.
        content = self.unique()
        while (
            len(content) < 200 or
            len(content) < len(self.compress(content))):
            content *= 2
        return content
