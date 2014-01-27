from __future__ import unicode_literals

from django.test import client

from . import handler


MULTIPART_CONTENT = client.MULTIPART_CONTENT


class Client(client.Client):
    """
    A custom test client that uses a request handler that provides
    a way to retrive the request object used for the last HTTP
    request sent by the client.
    
    A custom test client that provides a way to retrieve the request
    object used for the last HTTP request that was sent by the client.
    
    """
    def __init__(self, enforce_csrf_checks=False, **defaults):
        """
        Replace the default handler with the customized request handler.
        
        """
        super(Client, self).__init__(
            enforce_csrf_checks=enforce_csrf_checks, **defaults)
        self.handler = handler.ClientHandler(enforce_csrf_checks)
