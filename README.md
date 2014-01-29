django-daydreamer
=================

A Django class-based view utility library.

## Quickstart

Install django-daydreamer with pip.

```
pip install django-daydreamer
```

Do stuff like this:

```python
from daydreamer.core import urlresolvers
from daydreamer.views import behaviors, generic

class ProtectedResourceView(behaviors.LoginRequired, behaviors.ActiveRequired,
        behaviors.PermissionsRequired, behaviors.TestRequired,
        generic.TemplateView):
    
    template_name = "resources/detail.html"
    
    login_required = True
    
    active_required = True
    active_required_message = "Your account has been deactivated."
    active_required_redirect_url = urlresolvers.reverse_lazy("users:deactivated")
    
    permissions_required = "resources.resource_read"
    permissions_required_raise = True
    
    def test_required(self):
        return self.requst.user.is_special()
    test_required_message = "Do you want to join the special group?"
    test_required_redirect_url = urlresolvers.reverse_lazy("users:special_signup")
    
    def get_context_data(self, **context):
        # Retrieve the protected resource.
        # ...
```

The resulting view will perform a sequence of authentication checks before its
`get()` method is called. The order of the authentication checks is controlled
by the order of the inherited `behaviors` base classes. In this case, the view:

* checks if the user is logged in, redirecting to the login page upon
    failure, just like Django's `@login_required` decorator
* checks if the user's account is active, redirecting to the deactivated
    user information page and messaging the user about the account status
    upon failure
* checks if the user has one or more permissions, raising a
    `PermissionDenied` exception on failure
* checks if the user satisfies a test predicate, redirecting to the
    special signup page and messaging the user about the
    special group when the predicate returns a falsy value

Of course, you won't want to repeat all of these attributes on your view
classes, so set up a few base classes that provide the common behaviors you
need and inherit from them throughout your view codebase.

A rich suite of authentication view behaviors are provided as base classes.
Additionally, all of Django's view decorators are implemented as base classes,
whose inheritance structure is designed to help you avoid mistakes that can be
easily made with view function decorators. See the documentation for details.

## Documentation

Some features are described more thoroughly than others. For definitive
documentation, please browse the source code.

#### `daydreamer.views.core`

The `core` package provides view base classes that define an inheritance
structure and a framework for denying or allowing a request.

The top-level base class is `Core`, which inherits from
`django.views.generic.View`. It adds some useful features to all
`daydreamer` views.

Next in the hierarchy is `Null`, inheriting from `Core`. It `dispatch()` method
always returns a 405 method not allowed response. Next, two classes named
`Deny` and `Allow` inherit from `Null`. Their purpose is to choose a request
handler to deny or allow the request.

Finally, `HttpMethodDeny` and `HttpMethodAllow` inherit from `Deny` and
`Allow`, respectively. In turn, these are used to define the base generic view,
`daydreamer.views.generic.View`.

The `core` view framework enforces the semantics that denial should always
happen before approval. It also provides fine-grained control over the
ordering of denial checks and the processing of allowed requests. To use it
effectively, your view classes should not override `dispatch()`. Instead,
they should use one of the object-oriented hooks described below.

##### `class daydreamer.views.core.Core(django.views.generic.View)`

This is the base view class for all of `daydreamer`'s views. Generally,
you will not not inherit from it directly, but you will automatically inherit
its functionality from other `daydreamer` views. `Core` provides several
useful methods:

* `reverse()` reverses a named URL pattern, taking the arguments for
    `django.core.urlresovlers.reverse()` plus these additional arguments:
    * `qualified=False` if truthy, the reversed URL will be fully-qualified,
        using the request's host and URL scheme
    * `scheme=None` when `qualified` is truthy, set this to override the
        URL scheme, i.e. to "http" or "https"
* `attachment()` returns an attachment response:
    * `data` the raw data to use for the attachment
    * `content_type` the attachment's content type (MIME type)
    * `filename` the attachment's filename
* `redirect()` redirects to a named URL pattern, deferring to the `reverse()`
    method with one additional argument:
    * `permanent=False` if truthy, the redirect will be a permanent 301
        redirect instead of the default temporary 302 redirect
* `gone()` returns a 410 gone response
* `not_found()` raises the 404 response exception
* `permission_denied()` raises the 403 response exception
* `suspicious_operation()` raises the 400 response exception

The `not_found()`, `permission_denied()` and `suspicious_operation()` methods
raise exceptions rather than return responses, but for stylistic consistency,
returning their values is fine. Just be careful not to wrap these calls in
a masking exception handler. Here's an example:

```python
def get_thing_for(self, owner):
    try:
        return Thing.objects.get(owner=owner)
    except Thing.DoesNotExist:
        return self.not_found()
```

##### `class daydreamer.views.core.Null(daydreamer.views.core.Core)`

This view class always returns a 405 method not allowed response from
its `dispatch()` method. It exists to serve as a safety net at the top
of the `super()` chain for the `dispatch()` method. You will probably
never need to inherit directly from `Null`.

##### `class daydreamer.views.core.Allow(daydreamer.views.core.Null)`

Provides a way to select a handler for a request that has been allowed,
i.e. not denied. To hook into the selection process, override the
`get_allow_handler()` method.

###### `def get_allow_handler(self)`

This method should either return a callable that accepts the
`(request, *args, **kwargs)` arguments, or it should defer to `super()`.
For example, you may want to provide a request handler only when a certain
condition is met:

```python
def get_allow_handler(self):
    if self.some_condition():
        return self.allow_some_condition_handler
    else:
        return super(SomeView, self).get_allow_handler()
```

##### `class daydreamer.views.core.Deny(daydreamer.views.core.Null)`

Provides a way to select a handler to deny a request. To hook into the
selection process, override the `get_deny_handler()` method.

###### `def get_deny_handler(self)`

This method should either return a callable that accepts the
`(request, *args, **kwargs)` arguments, or it should defer to `super()`.
This method will typically check for a certain condition and provide a
request handler that denies the request with a redirect, error, etc.

```python
def get_deny_handler(self):
    if not self.some_condition():
        return self.deny_some_condition_handler
    else:
        return super(SomeView, self).get_deny_handler()
```

##### `class daydreamer.views.core.HttpMethodAllow(daydreamer.views.core.Allow)`
##### `class daydreamer.views.core.HttpMethodDeny(daydreamer.views.core.Deny)`

These view classes re-implement the basic behavior of
`django.views.generic.View`, leveraging the framework provided by
`Allow` and `Deny`. When the request's method is in `http_method_names` and the
view has a matching method name, i.e. `get()`, the request is allowed.
Otherwise, it is denied with a 405 method not allowed response.

##### `class daydreamer.views.core.Denial(daydreamer.views.core.Deny)`

This view class implements a declarative API for controlling request denial
behavior. It provides the `deny()` method, whose behavior is controlled by
attributes set on the class. The `deny()` method should be called with a name
prefix, which it will use to look up the controlling attributes. The
controlling attributes are:

* `<prefix>_raise` whether an exception should be raised
* `<prefix>_exception` a custom exception to be raised, defaulting to
    `django.core.exceptions.PermissionDenied`
* `<prefix>_message` a message to enqueue
* `<prefix>_message_level` the message's level, defaults to
    `django.contrib.messages.WARNING`
* `<prefix>_message_tags` the message's tags, defaults to `""`
* `<prefix>_redirect_url` the URL to redirect to upon test failure,
    defaults to `settings.LOGIN_URL`
* `<prefix>_redirect_next_url` the return URL value to add to the redirect
    URL's query string, defaulting to the request's fully-qualified URL
* `<prefix>_redirect_next_name` the return URL parameter name to add to the
    redirect URL's query string, defaulting to `"next"`. If set to
    a falsy value, no return URL query parameter will be included in the
    redirect URL.

If `<prefix_raise>` is truthy, an exception will be raised immediately and
the other attributes will be ignored. Otherwise, `deny()` will check if
`<prefix_message>` has been set to determine whether to enqueue a message
using the `django.core.contrib.messages` framework. Finally, it will return
a redirect response based on the the `<prefix>_redirect_url` settings.

To calculate any of these attributes dynamically, you can write them as
`@property` methods. For more advanced usage, study the object-oriented hooks
in the source code and override any methods as necessary.

The views in `daydreamer.views.behaviors.auth` make extensive use of this API.
See the source code for usage examples. Denial behaviors based on login state,
account status, a user's groups, a user's permissions and generic tests are
all provided, so the chances are good that you won't have to subclass `Denial`.

#### `daydreamer.views.behaviors`

The `behaviors` package provides a rich set of view classes for checking
authentication status along with class-based replacements for all
of Django's view decorators.

Behaviors may inherit from `Deny`, `Allow` or `View`, which will determine
whether and when they take effect with a call to `dispatch()`. Behaviors
inheriting from `View` have the highest priority, which we'll call *dispatch*
priority. Behaviors inheriting from `Deny` have the next highest priority,
which we'll call *deny* priority. Finally, behaviors inheriting from `Allow`
have the lowest priority, which we'll call *allow* priority.

The consequence of this design is that, even if you inherit from *dispatch*,
*deny* and *allow*  behaviors and mix them in the wrong order, the effect of
the behaviors will still be ordered correctly.

For example, `CachePage` has *allow* priority and `LoginRequired` has *deny*
priority. If we were to set up a view like this:

```python
from daydreamer.views import behaviors, generic

class View(behaviors.CachePage, behaviors.LoginRequired, generic.View):
    # ...
```

Even though `CachePage` appears first in the base class list, the framework
will order the effects of the behaviors correctly so that the response will not
be cached when `LoginRequired` returns a redirect or error (note that
`CachePage` will actually only cache 200 OK responses, but the framework will
actually skip calling `CachePage`'s behavior when `LoginRequired` handles
the request).

While this inheritance structure can help you avoid some simple mistakes, when
inheriting from multiple base classes, it's still possible to create an
indeterminate method resolution order. To avoid that problem, you should
inherit from *dispatch* behaviors first, then *deny* behaviors, then *allow*
behaviors and finally from a basic view class like
`daydreamer.views.generic.TemplateView`.

##### Why Are They Called "Behaviors?"

The view classes in `daydreamer.views.behaviors` are meant to be inherited
as base classes, not to wrap a function or class with functionality, so
calling them "decorators" is not really correct. Also, they inherit from view
classes in `daydreamer.views.core`, so they aren't "mixins" in the sense
of being independent classes that only inherit from `object`. They are meant
to modify the behavior of a view by hooking into the cooperative `super()`
call chains provided by `daydreamer.views.core`, so "behaviors" seems an
appropriate name.

#### `daydreamer.views.behaviors.clickjacking`

#### `daydreamer.views.behaviors.csrf`

#### `daydreamer.views.behaviors.debug`

#### `daydreamer.views.behaviors.gzip`

#### `daydreamer.views.behaviors.auth`

All of the authentication behavior views leverage the denial framework
provided by `daydreamer.views.core.Denial`, so each behavior can be controlled
with attributes such as `login_required_raise` for the `LoginRequired`
behavior. See the `Denial` documentation above for details.

#### `daydreamer.views.behaviors.http`

#### `daydreamer.views.behaviors.cache`

#### `daydreamer.views.behaviors.vary`

### Miscellaneous

You can also find some cool things in `daydreamer.test`, like
`daydreamer.test.views.generic.TestCase`, which lets you test a view class
using the full Django handler stack, without any need for a
urls.py configuration.

More stuff is on the way.

## Status

This project now provides some useful and well-tested tools for writing
class-based views, so I'm making releases as I flesh things out.

The documentation summarizes the tools provided, but it doesn't provide
details about all of the object-oriented hooks designed into the system.
See the source code for implementation details and hooks.

The project is in alpha, so public interfaces and behaviors may change
dramatically. If you decide to use this software "as-is", it would be wise
to use a specific version and read the changelog before attempting to upgrade.

## Changelog

##### 0.0.1a

Initial release. Includes base view class enhancements and authentication view
behaviors. View code has 100% test coverage.
