django-daydreamer
=================

A Django class-based view utility library.

### Quickstart

Install django-daydreamer with pip.

```
pip install django-daydreamer
```

Do stuff like this:

```python
from daydreamer.core import urlresolvers
from daydreamer.views import decorated


class SpookyProtectedResourceView(decorated.AuthRequired):
    login_required = True
    
    active_required = True
    active_required_message = "Your account has been deactivated."
    active_required_redirect_url = urlresolvers.reverse_lazy("users:deactivated")
    
    permissions_required = "resources.resource_read"
    permissions_required_raise = True
    
    def test_required(self):
        return self.user.is_spooky()
    test_required_message = "Join the Spooky program."
    test_required_redirect_url = urlresolvers.reverse_lazy("users:spooky_signup")
    
    def get(self, request, *args, **kwargs):
        # Retrieve the protected resource.
        # ...
```

The resulting view will perform a sequence of authentication checks before its
`get()` method is called:

    * checks if the user is logged in, redirecting to the login page upon
    failure, just like Django's `@login_required` decorator.
    * checks if the user's account is active, redirecting to the deactivated
    user information page and messaging the user about the account status
    upon failure.
    * checks if the user has one or more permissions, raising a
    `PermissionDenied` exception on failure.
    * checks if the user satisfies a test predirect, redirecting to the
    Spooky signup page and messaging the user about the
    Spooky program upon failure.

Of course, you won't want to repeat all of these attributes on your view
classes, so set up a few base classes that provide the common behaviors you
need and inherit from them throughout your view codebase.

For all of the view decorator mixins defined in
`daydreamer.views.decorated.auth` (import accessible at
`daydreamer.views.decorated`), you can control the inherited behavior through
a consistent set of attributes. The attributes are prefixed to match their
class names, except that they use lowercase underscore casing instead of 
camel casing. The values are:

    * `<prefix>_raise` whether an exception should be raised upon test failure
    * `<prefix>_exception` a custom exception to be raised upon test failure,
    defaults to `PermissionDenied`
    * `<prefix>_message` a message to be enqueued upon test failure
    * `<prefix>_message_level` the message's level, defaults to `WARNING`
    * `<prefix>_message_tags` the message's tags, defaults to `""`
    * `<prefix>_redirect_url` the URL to redirect to upon message failure,
    defaults to `settings.LOGIN_URL`
    * `<prefix>_redirect_next_url` the return URL value to add to the redirect
    URL's query string, defaulting to the request's absolute URI.
    * `<prefix>_redirect_next_name` the return URL parameter name to add to the
    redirect URL's query string, defaulting to REDIRECT_FIELD_NAME. If set to
    a falsy value, no return URL query parameter will be included in the
    redirect URL.

You can also find some cool things in `daydreamer.test`, like
`daydreamer.test.views.TestCase`, which lets you test a view class using the
full Django handler stack, without needing to set up a URLs configuration,
i.e. no urls.py.

More stuff is on the way.

### Status

This project now provides some useful and well-tested tools for writing
class-based views, so I've released the first version. At this point, you will
need to read the documentation found in the source code to figure out what's
possible. More documentation will be published once all planned view decorator
mixins have been fleshed out.

### Changelog

##### v0.0.1a

Initial release. Includes base view class enhancements and authentication view decorator mixins. View code has 100% test coverage.