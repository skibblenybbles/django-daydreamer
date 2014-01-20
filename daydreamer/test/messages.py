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
        
        # There must be a context in the response.
        self.assertTrue(
            hasattr(response, "context") and response.context,
            "The response must have a truthy context attribute.")
        
        # Get the messages from the context. This may be a fragile
        # django.test.utils.ContextList data structure, so we can't
        # call .get() on it.
        messages = list(
            response.context["messages"]
                if "messages" in response.context
                else [])
        
        # Check for at least one message.
        self.assertTrue(
            bool(messages),
            "The response's context must contain at least one message.")
        
        # Check for a message limit.
        if limit:
            self.assertGreaterEqual(
                limit, len(messages),
                "The response's context must have at most {limit:d} "
                "messages, but it has {actual:d} messages.".format(
                    limit=limit, actual=len(messages)))
        
        # Check for a matching message.
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
            
            # The context may be a fragile django.test.utils.ContextList data
            # structure, so we can't call .get() on it.
            self.assertEqual(
                len(list(
                    response.context["messages"]
                        if "messages" in response.context
                        else [])), 0,
                "The response's context must not contain any messages.")
