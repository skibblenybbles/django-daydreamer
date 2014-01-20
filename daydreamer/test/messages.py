from . import base


class TestCase(base.TestCase):
    """
    A test case for making assertions about messsages from
    django.contrib.messages in the context of a response.
    
    """
    def assertMessage(self, response, content, level=None, tags=None, limit=None):
        """
        Asserts that the response has a particular message in its context.
        
        If limit is provided, checks that there are at most the specified
        number of messages.
        
        If level or tags are specified, checks for existence of message having the
        given content and the level and/or tags. Otherwise, it only checks
        for a message with the given content.
        
        """
        # Normalize the space-separated tags to a set of strings.
        tags = set(tag.strip() for tag in (tags or "").split(" ") if tag)
        
        self.assertTrue(
            hasattr(response, "context") and response.context,
            "The response must have a truthy context attribute.")
        
        messages = list(response.context.get("messages", []))
        self.assertTrue(
            bool(messages),
            "The response's context must contain at least one message.")
        
        if limit:
            self.assertGreaterEqual(
                limit, len(messages),
                "The response's context must have at most {limit:d} "
                "messages, but it has {actual:d} messages.".format(
                    limit=limit, actual=len(messages)))
        
        self.assertTrue(
            any((
                message.message == content and
                (not level or message.level == level) and
                (not tags or (
                    set(tag.strip() 
                        for tag in (message.tags or "").split(" ")
                        if tag) == tags)))
                for message in messages),
            "A message matching the content, level and tags was not found in "
            "the response's context.")
    
    def assertNoMessages(self, response):
        """
        Asserts that the resopnse does not have any messages in its context.
        
        """
        if getattr(response, "context", None):
            self.assertEqual(
                len(list(response.context.get("messages", []))), 0,
                "The response's context must not contain any messages.")
