from __future__ import unicode_literals

from django.test import client

from daydreamer.core import handlers


class ClientHandler(client.ClientHandler, handlers.base.Handler):
    """
    A customized test client handler that keeps track of the most recently
    generated request.
    
    """
    def __init__(self, *args, **kwargs):
        super(ClientHandler, self).__init__(*args, **kwargs)
        self.last_request = None
    
    @property
    def last_request(self):
        return self._last_request
    
    @last_request.setter
    def last_request(self, request):
        self._last_request = request
    
    def get_response(self, request):
        self.last_request = request
        return super(ClientHandler, self).get_response(request)
