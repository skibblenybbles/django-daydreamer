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

Next in the hierarchy is `Null`, inheriting from `Core`. Its `dispatch()`
method always returns a 405 method not allowed response. Next, two classes
named `Deny` and `Allow` inherit from `Null`. Their purpose is to choose a
request handler to deny or allow the request.

Finally, `HttpMethodDeny` and `HttpMethodAllow` inherit from `Deny` and
`Allow`, respectively. In turn, these are used to define the base generic view,
`daydreamer.views.generic.View`.

The `core` view framework enforces the semantics that denial should always
happen before approval. It also provides fine-grained control over the
ordering of denial checks and the processing of allowed requests. To use it
effectively, your view classes should not override `dispatch()`. Instead,
they should use one of the object-oriented hooks described below.

##### `class Core(django.views.generic.View)`

This is the base view class for all of `daydreamer`'s views. Generally,
you will not not inherit from it directly, but you will automatically inherit
its functionality from other `daydreamer` views. `Core` provides several
useful methods:

* `reverse()` reverses a named URL pattern, taking the arguments for
    `django.core.urlresovlers.reverse()` plus these additional arguments:
    * `qualified=False` if truthy, the reversed URL will be fully-qualified,
        using the request's host and URL scheme
    * `scheme=None` when `qualified` is truthy, set this to override the
        URL scheme, i.e. "http" or "https"
* `attachment()` returns an attachment response for the required arguments:
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

##### `class Null(daydreamer.views.core.Core)`

This view class always returns a 405 method not allowed response from
its `dispatch()` method. It exists to serve as a safety net at the top
of the `super()` chain for the `dispatch()` method. You will probably
never need to inherit directly from `Null`.

##### `class Allow(daydreamer.views.core.Null)`

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

##### `class Deny(daydreamer.views.core.Null)`

Provides a way to select a handler to deny a request. To hook into the
selection process, override the `get_deny_handler()` method.

###### `def get_deny_handler(self)`

This method should either return a callable that accepts the
`(request, *args, **kwargs)` arguments, or it should defer to `super()`.
This method will typically check for a certain condition and return a
request handler that denies the request with a redirect, error, etc.

```python
def get_deny_handler(self):
    if not self.some_condition():
        return self.deny_some_condition_handler
    else:
        return super(SomeView, self).get_deny_handler()
```

##### `class HttpMethodAllow(daydreamer.views.core.Allow)`
##### `class HttpMethodDeny(daydreamer.views.core.Deny)`

These view classes re-implement the basic behavior of
`django.views.generic.View`, leveraging the framework provided by
`Allow` and `Deny`. When the request's method is in `http_method_names` and the
view has a matching method name, i.e. `get()`, the request is allowed.
Otherwise, it is denied with a 405 method not allowed response.

##### `class Denial(daydreamer.views.core.Deny)`

This abstract view class implements a declarative API for controlling request
denial behavior. It provides the `deny()` method, whose behavior is controlled
by attributes set on the class. The `deny()` method should be called with a
name prefix, which it will use to look up the controlling attributes. The
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

If `<prefix>_raise` is truthy, an exception will be raised immediately and
the other attributes will be ignored. Otherwise, `deny()` will check if
`<prefix>_message` has been set to decide whether to enqueue a message
using the `django.core.contrib.messages` framework. Finally, it will return
a redirect response based on the the `<prefix>_redirect_url` settings.

To calculate any of these attributes dynamically, you can write them as
`@property` methods. For more advanced usage, study the object-oriented hooks
in the source code and override any methods as necessary.

The views in `daydreamer.views.behaviors.auth` make extensive use of this API.
See the source code for usage examples. Denial behaviors based on login state,
account status, a user's groups, a user's permissions and generic tests are
all provided, so the chances are good that you won't have to subclass `Denial`.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

#### `daydreamer.views.behaviors`

The `behaviors` package provides a rich set of view classes for checking
authentication status along with class-based replacements for all
of Django's view decorators.

Behaviors may inherit from `View`, `Deny` or `Allow`, which determines
whether and when they take effect when `dispatch()` is called. Behaviors
inheriting from `View` have the highest priority, which we'll call *dispatch*
priority. Behaviors inheriting from `Deny` have the next highest priority,
which we'll call *deny* priority. Finally, behaviors inheriting from `Allow`
have the lowest priority, which we'll call *allow* priority. The consequence of
this design is that, even if you inherit from *dispatch*, *deny* and *allow*
behaviors and mix them in the wrong order, the effect of the behaviors will
still be ordered correctly.

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

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

#### `daydreamer.views.behaviors.clickjacking`

The view behaviors in the `clickjacking` package replace the view decorators
from `django.views.decorators.clickjacking`. They all have *dispatch* priority,
so that they can add or remove clickjacking headers for every response.

##### `class XFrameOptionsDeny(daydreamer.views.generic.View)`

Replaces the `django.views.decorators.clickjacking.xframe_options_deny()`
view decorator. It adds an `X-Frame-Options` header with a value of `DENY` to
every response. You can disable its functionality by setting the
`xframe_options_deny` attribute to a falsy value (`True` by default).

##### `class XFrameOptionsSameOrigin(daydreamer.views.generic.View)`

Replaces the
`django.views.decorators.clickjacking.xframe_options_same_origin()` view
decorator. It adds an `X-Frame-Options` header with a value of `SAMEORIGIN` to
every response. You can disable its functionality by setting the
`xframe_options_same_origin` attribute to a falsy value (`True` by default).

##### `class XFrameOptionsExempt(daydreamer.views.generic.View)`

Replaces the `django.views.decorators.clickjacking.xframe_options_exempt()`
view decorator. It prevents the clickjacking middleware from adding an
`X-Frame-Options` header to the response. You can disable its functionality
by setting the `xframe_options_exempt` attribute to a falsy value (`True`
by default).

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

#### `daydreamer.views.behaviors.csrf`

The view behaviors in the `csrf` package replace the view function decorators
from `django.views.decorators.csrf`. They all have *dispatch* priority, so that
the CSRF middleware can deny a request as early as possible.

##### `class CsrfProtect(daydreamer.views.generic.View)`

Replaces the `django.views.decorators.csrf.csrf_protect()` view decorator.
This is generally only useful if the CSRF middleware is not installed.
Otherwise, the middleware protects all of your views. When CSRF middleware is
not installed, you can disable the view behavior's functionality by setting
the `csrf_protect` attribute to a falsy value (`True` by default).

##### `class RequiresCsrfToken(daydreamer.views.generic.View)`

Replaces the `django.views.decorators.csrf.requires_csrf_token()` view
decorator. This is generally only useful if the CSRF middleware is not
installed. It ensures that `csrf_token` will be available in the context
for template rendering, but only when a `RequestContext` is created. When
CSRF middleware is installed, this functionality is automatic. When CSRF
middleware is not installed, you can disabled the view behavior's functionality
by setting the `requires_csrf_token` attribute to a falsy value (`True`
by default).

##### `class EnsureCsrfCookie(daydreamer.views.generic.View)`

Replaces the `django.views.decorators.csrf.ensure_csrf_cookie()` view
decorator. This ensures that the CSRF cookie will always be set on the
response, regardless of whether a `csrf_token` was rendered in the template.
The view behavior's functionality can be disabled by setting the
`ensure_csrf_cookie` attribute to a falsy value (`True` by default). Note that
this won't prevent the cookie from being written through the normal process.

For sites that have CSRF-protected AJAX functionality, mix this view behavior
into all of your normal page views to eliminate headaches where the CSRF cookie
is randomly unavailable for AJAX requests.

##### `class CsrfExempt(daydreamer.views.generic.View)`

Replaces the `django.views.decorators.csrf.csrf_exempt()` view decorator.
This disables the CSRF middleware so that a view will not be CSRF-protected.
The view behavior's functionality can be disabled by setting the `csrf_exempt`
attribute to a falsy value (`True` by default).

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

#### `daydreamer.views.behaviors.debug`

The view behaviors in the `debug` package replace the view function decorators
from `django.views.decorators.debug`. They all have *dispatch* priority,
because they need to add attributes to the view function returned by Django's
URL resolution framework.

##### `class SensitiveVariables(daydreamer.views.generic.View)`

Replaces the `django.views.decorators.debug.sensitive_variables()` view
decorator. Set the `sensitive_variables` attribute to a string or an iterable
of strings to protect particular sensitive variable names. Set it to an
otherwise truthy value to protect all variable names. Otherwise, set it to a
falsy value to disable the view behavior's functionality. Its value is `True`
by default to protect all variable names.

This behavior affects logging when `settings.DEBUG` is turned off. The values
of protected variable names will be obfuscated in error traceback logs.

##### `class SensitivePostParameters(daydreamer.views.generic.View)`

Replaces the `django.views.decorators.debug.sensitive_post_parameters()` view
decorator. Set the `sensitive_post_paramters` attribute to a string or an
iterable of strings to protect particular POST request parameters. Set it to
an otherwise truthy value to protect all POST request parameters. Otherwise,
set it to a falsy value to disable the view behavior's functionality. Its
value is `True` by default to protect all POST request parameters.

This behavior affects logging when `settings.DEBUG` is turned off. The values
of protected POST request parameters will be obfuscated in request error logs.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

#### `daydreamer.views.behaviors.gzip`

The view behaviors in the `gzip` package replace the view function decorators
from `django.views.decorators.gzip`. They all have *dispatch* priority, because
they modify any kind of response from the view.

##### `class GZipPage(daydreamer.views.generic.View)`

Replaces the `django.views.decorators.gzip.gzip_page()` view decorator. When
the response meets certain criteria for content size, content type and
the request's `User-Agent` headers, the behavior gzips the response. To disable
the view behavior's functionality, set the `gzip_page` attribute to a
falsy value.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

#### `daydreamer.views.behaviors.auth`

All of the authentication view behaviors leverage the denial framework
provided by `daydreamer.views.core.Denial`, so each behavior can be controlled
with attributes such as `login_required_raise` for the `LoginRequired`
behavior. See the `Denial` documentation above for details.

##### `class LoginRequired(daydreamer.views.core.Denial)`

Replaces the `django.views.decorators.auth.login_required()` view decorator
and provides additional functionality. This view behavior inherits from
`Denial` and uses a prefix of `login_required`, so you can control the login
requirement behavior with attributes like `login_required_raise`,
`login_required_message`, etc.

Like the `@login_required` decorator, this behavior does not check whether
the user is active (`is_active == True`). See the `ActiveRequired` view
behavior class for that capability.

To change the behavior upon a failed login requirement test, you can override
the `login_required_denied(self, request, *args, **kwargs)` method. The
base implementation simply calls `self.deny("login_required")`.

You can disable the view behavior's functionality by setting the
`login_required` attribute to a falsy value (`True` by default).

##### `class ActiveRequired(daydreamer.views.core.Denial)`

Requires that `self.request.user.is_active` is `True`. This view behavior
inherits from `Denial` and uses a prefix of `active_required`, so you can
control the active requirement behavior with attributes like
`active_required_raise`, `active_required_message`, etc.

To change the behavior upon a failed active requirement test, you can override
the `active_required_denied(self, request, *args, **kwargs)` method. The
base implementation simply calls `self.deny("active_required")`.

You can disable the view behavior's functionality by setting the
`active_required` attribute to a falsy value (`True` by default).

##### `class StaffRequired(daydreamer.views.core.Denial)`

Requires that `self.request.user.is_staff` is `True`. This view behavior
inherits from `Denial` and uses a prefix of `staff_required`, so you can
control the staff requirement behavior with attributes like
`staff_required_raise`, `staff_required_message`, etc.

To change the behavior upon a failed staff requirement test, you can override
the `staff_required_denied(self, request, *args, **kwargs)` method. The
base implementation simply calls `self.deny("staff_required")`.

You can disable the view behavior's functionality by setting the
`staff_required` attribute to a falsy value (`True` by default).

##### `class SuperuserRequired(daydreamer.views.core.Denial)`

Requires that `self.request.user.is_superuser` is `True`. This view behavior
inherits from `Denial` and uses a prefix of `superuser_required`, so you can
control the superuser requirement behavior with attributes like
`superuser_required_raise`, `superuser_required_message`, etc.

To change the behavior upon a failed superuser requirement test, you can
override the `superuser_required_denied(self, request, *args, **kwargs)`
method. The base implementation simply calls `self.deny("superuser_required")`.

You can disable the view behavior's functionality by setting the
`superuser_required` attribute to a falsy value (`True` by default).

##### `class GroupsRequired(daydreamer.views.core.Denial)`

Requires that `self.request.user` is in all of the specified groups. This view
behavior inherits from `Denial` and uses a prefix of `groups_required`, so you
can control the groups requirement behavior with attributes like
`groups_required_raise`, `groups_required_message`, etc.

The required groups are specified with the `groups_required` attribute. It may
be a group name, a `django.contrib.auth.models.Group` object or an iterable
mixing group names and `Group` objects. Any group names must exist in the
database or an `ImproperlyConfigured` exception will be raised.

To change the behavior upon a failed groups requirement test, you can
override the `groups_required_denied(self, request, *args, **kwargs)`
method. The base implementation simply calls `self.deny("groups_required")`.

You can disable the view behavior's functionality by setting the
`groups_required` attribute to a falsy value (`None` by default).

##### `class PermissionsRequired(daydreamer.views.core.Denial)`

Requires that `self.request.user` has all of the specified permissions. This
view behavior inherits from `Denial` and uses a prefix of
`permissions_required`, so you can control the permissions requirement behavior
with attributes like `permissions_required_raise`,
`permissions_required_message`, etc.

The required permissions are specified with the `permissions_required`
attribute. It may be a permission name or an iterable of permission names. For
efficiency, no value checks are performed to confirm that the permissions
exist, so be mindful of typos.

To change the behavior upon a failed permissions requirement test, you can
override the `permissions_required_denied(self, request, *args, **kwargs)`
method. The base implementation simply calls
`self.deny("permissions_required")`.

You can disable the view behavior's functionality by setting the
`permissions_required` attribute to a falsy value (`None` by default).

##### `class ObjectPermissionsRequired(daydreamer.views.core.Denial)`

This view behavior works the same way as `PermissionsRequired`, but the
permissions check is for a specific object, and the prefix is
`object_permissions_required`. Additionally, you must specify an
`object_permissions_required_object` attribute, most likely implemented
as a `@property` method, to specify the object for the test. Of course,
to change its behavior upon test failure, override the
`object_permissions_required_denied(self, request, *args, **kwargs)` method.
The base implementation simply calls
`self.deny("object_permissions_required")`.

You can disable the view behavior's functionality by setting either
`object_permissions_required` or `object_permissions_required_object` to a
falsy value.

This view behavior will not work out-of-the-box and requires an authentication
backend that implements object permissions, i.e. "row-level" permissions. This
is the only view that has incomplete tests (`@unittest.expectedFailure`),
so you should double-check the implementation before trying to use it.

##### `class TestRequired(daydreamer.views.core.Denial)`

Requires that a specified test predicate returns a truthy value. This
view behavior inherits from `Denial` and uses a prefix of `test_required`,
so you can control the test requirement behavior with attributes like
`test_required_raise`, `test_required_message`, etc.

To require a test, define a `test_required(self)` method, which returns
a truthy value when `self.request` (or some other view properties) are
satisfactory. When it returns a falsy value, the request will be denied.

To change the behavior upon a failed test, you can override the
`test_required_denied(self, request, *args, **kwargs)` method. The base
implementation simply calls `self.deny("test_required")`.

You can disable the view behavior's functionality by setting the
`test_required` attribute to a falsy value (`None` by default).

This view behavior can be used to fill in any custom request checks that
aren't covered by the other `auth` view behaviors.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

#### `daydreamer.views.behaviors.http`

The view behaviors in the `http` package replace the view function decorators
from `django.views.decorators.http`. They all have *deny* priority, except
for `Condtion`, which has the lowest *allow* priority.

##### `class RequireGET(daydreamer.views.core.HttpMethodDeny)`

Replaces the `django.views.decorators.http.require_GET()` view decorator. The
implementation is trivial, as it simply sets the `http_method_names` attribute
to `("get",)`. This behavior class is probably not very useful, but it is
provided for completeness.

##### `class RequirePOST(daydreamer.views.core.HttpMethodDeny)`

Replaces the `django.views.decorators.http.require_POST()` view decorator. Like
`RequireGET`, its implementation is trivial, setting the `http_method_names`
attribute to `("post",)`.

##### `class RequireSafe(daydreamer.views.core.HttpMethodDeny)`

Replaces the `django.views.decorators.http.require_safe()` view decorator.
Again, it is implemented trivially by setting the `http_method_names` attribute
to `("get", "head",)`.

##### `class Condition(daydreamer.views.core.HttpMethodAllow)`

Replaces the `django.views.decorators.http.condition()` view decorator. You may
define a `condition_etag()` method to compute the ETag string for the requested
resource. You may also define a `condition_last_modified()` method to compute
the last modified `datetime` for the requested resource. Both methods should
take the request, arguments and keyword arguments from the URL resolver, i.e.
`(request, *args, **kwargs)`. If neither method is defined, the behavior will
be disabled.

`ETag` and `Last-Modified` headers provide a way to short-circuit a view by
immediately returning a 304 not modified response. When implemented with a bit
of clever caching, you can arrange to avoid all database queries and processing
time to render a response, significantly speeding up your application servers'
response times.

Finally, note that the `etag()` and `last_modified()` view decorators from
`django.views.decorators.http` are not provided as view behavior classes. You
can achieve the same functionality as these decorators by defining only one
of `condtion_etag()` or `condition_last_modified()` on a `Condition` subclass.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

#### `daydreamer.views.behaviors.cache`

The view behaviors in the `cache` package replace the view function decorators
from `django.views.decorators.cache`. They all have the lowest *allow*
priority, as caching should only be performed on requests that have not
been denied.

##### `class CachePage(daydreamer.views.core.HttpMethodAllow)`

Replaces the `django.views.decorators.cache.cache_page()` view decorator.
You can set any of the `cache_page_timeout`, `cache_page_cache` or
`cache_page_key_prefix` attributes to override Django's defaults for the
timeout, cache name or key prefix used for caching. You can disable the view
behavior's functionality by setting the `cache_page` attribute to a
falsy value.

This view behavior is tempting to use, just like the decorator. But, caching
is affected by the `Vary` and `Cache-Control` response headers, which may not
get set to their final values until the response middleware runs, which will
happen after this behavior has been applied.

Take extra care when using this behavior to make sure that it caches the
response at the correct time. It's probably safer to use the two-part caching
middleware, which you can find in Django's caching docs. For relatively safe
usage of this behavior, set `settings.CACHE_MIDDLEWARE_ANONYMOUS_ONLY` to
`True`, which will prevent accidental caching of resources that may only be
accessible to authenticated users.

For experienced developers, this behavior could be used in concert with
`daydreamer.views.behaviors.CacheControl` and `daydreamer.views.behaviors.Vary`
to implement safe, page-level caching even for authenticated users. However,
please read and understand Django's implementation of the `cache_page()`
view decorator and the underlying `CacheMiddleware` before making such
an attempt.

##### `class CacheControl(daydreamer.views.core.HttpMethodAllow)`

Replaces the `django.views.decorators.cache.cache_control()` view decorator.
This view behavior adds a `Cache-Control` header to the response setting one
or more values. The behavior is configured by these attributes:

* `cache_control_public` if `None`, doesn't affect the header. If truthy, adds
    `public` to the header. If falsy (and not `None`), adds `private` to
    the header
* `cache_control_no_cache` if truthy, adds `no-cache` to the header
* `cache_control_no_transform` if truthy, adds `no-transform` to the header
* `cache_control_must_revalidate` if truthy, adds `must-revalidate` to
    the header
* `cache_control_proxy_revalidate` if truthy, adds `proxy-revalidate` to
    the header
* `cache_control_max_age` if not falsy, it must be a number specifying the
    `max-age` value to add to the header
* `cache_control_s_maxage` if not falsy, it must be a number specifying the
    `s-maxage` value to add to the header

This low-level view behavior manages upstream caching of responses, so be sure
you know what you're doing if you choose to use it. Otherwise, Django's
middleware will handle these details in a minimal and correct way by default.
You can disable the view behavior's functionality by setting the
`cache_control` attribute to a falsy value (`True` by default) or by setting
all of the `cache_control_*` attributes to `None`.

##### `class NeverCache(daydreamer.views.core.HttpMethodAllow)`

Replaces the `django.views.decorators.cache.never_cache()` view decorator.
This view behavior adds a `Cache-Control` header with the value `max-age=0`
to the response. You can disable the view behavior's functionality by setting
the `never_cache` attribute to a falsy value (`True` by default).

As a side note, if `CachePage` is also inherited from and it appears *before*
`NeverCache` in the inheritance order, caching will be disabled. Otherwise,
the page will be cached before the `NeverCache` behavior is applied. Combining
these behaviors is probably a bad idea.

* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

#### `daydreamer.views.behaviors.vary`

The view behaviors in the `vary` package replace the view function decorators
from `django.views.decorators.vary`. They all have the lowest *allow* priority,
as these headers probably don't make sense for error or redirect responses.

##### `class VaryOnHeaders(daydreamer.views.core.HttpMethodAllow)`

Replaces the `django.views.decorators.vary.vary_on_headers()` view decorator.
This view behavior adds the string or iterable of strings specified in the
`vary_on_headers` attribute to the response's `Vary` header. You can disable
the view behavior's functionality by setting `vary_on_headers` to a falsy
value (`None` by default).

##### `class VaryOnCookie(daydreamer.views.core.HttpMethodAllow)`

Replaces the `django.views.decorators.vary.vary_on_cookie()` view decorator.
It is equivalent to using `VaryOnHeaders` with the `vary_on_headers` attribute
set to `"Cookie"`. You can disable the view behavior's functionality by setting
`vary_on_cookie` to a falsy value (`True` by default).

## Miscellaneous

You can find some cool things in `daydreamer.test`, like
`daydreamer.test.views.generic.TestCase`, which lets you test a view class
using the full Django handler stack, without any need to set up an urlconf.

In `daydreamer.core.urlresolvers`, you can find extensions to Django's
`resolve()` and `reverse()` functions, which add features for dealing with
fully-qualified URLs when a request object is provided or when the
`django.contrib.sites` framework is properly set up. It also includes handy
utilities for safely adding query parameters to a URL with `update_query()`
and for simplifying a redirect URL with respect to a source URL with
`simplify_redirect()`.

An object-oriented refactor of the `get_response()` mega-method from Django's
base request handler, defined in `django.core.handlers.base.BaseHandler`, 
can be found in `daydreamer.core.handlers.base.Handler`. It organizes the
flow of code in `get_response()` so that it has useful object-oriented hooks.
This is leveraged by the custom test client request handler in
`daydreamer.test.views.handler.ClientHandler`.

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

* Initial release
* Includes base view class enhancements and authentication view
    behaviors
* View code has 100% test coverage

##### 0.0.2a

* Refactors the base view class implementation into an inheritance structure
    which enforces the rule that all attempts to deny a request should occur before
    all attempts to allow and process the request
* Implements a view behavior class for every view function decorator provided
    by Django
* Includes a major refactor of the test code, designed for future testing
    flexibility and potentially for use as a library
* View code has 100% test coverage

## Why?

First of all, I find using the `@method_decorator` syntax to be ugly and
awkward, especially when multiple decorators are required. Once you get over
the learning curve, class-based views save so much work, and for me, they've
breathed new life into the Django coding experience. I think they really
deserve more love than an ugly adapter for function views. Additionally, view
decorators need to be applied in a relatively obscure and undocumented order,
which I believe discourages their use.

Beyond that, libraries like 
<a href="https://github.com/brack3t/django-braces" target="_blank">django-braces</a>
are quickly growing in popularity. The django-braces project is very helpful,
but looking closely at its implementation, you can see that some subtle bugs
can be accidentally written.

Consider these two view classes:

```python
from braces import views as braces
from django.views import generic

class GoodView(braces.CsrfExempt, generic.TemplateView):
    template_name = "some_template.html"
    
    def post(self, request, *args, **kwargs):
        # This will be exempt from CSRF checks.
        # ...

class BadView(braces.CsrfExempt, generic.TemplateView)
    template_name = "some_template.html"
    
    def post(self, request, *args, **kwargs):
        # This will NOT be exempt from CSRF checks.
        # ...
    
    def dispatch(self, request, *args, **kwargs):
        # Do something novel.
        # ...
        return super(BadView, self).dispatch(request, *args, **kwargs)
```

When we create a view from `GoodView` with `GoodView.as_view()`, the returned
view function will have a `csrf_exempt` attribute set on it with a value of
`True`. This is the effect of the `@csrf_exempt` decorator. It's how the
CSRF middleware is informed that the view does not need CSRF protection.

When we create a view from `BadView` with `BadView.as_view()`, the returned
view function will be missing the `csrf_exempt` attribute, and the CSRF
middleware will apply CSRF protection to the view, despite inheritance
from `braces.CsrfExempt`.

The reason why, is that `braces.CsrfExempt` is implemented by adding a
`@method_decorator(csrf_exempt)` decorator to a `dispatch()` method that it
defines. When we override `dispatch()` in `BadView`, the effect of the
decorator is lost, because method attributes are not inherited.

The `daydreamer` library works around this problem by overriding the
`as_view()` class method and decorating the view function returned by its
`super()`. The Django view decorators use the `@functools.wraps` decorator
properly, so view attributes are passed through, even when multiple decorators
are applied with this technique.

This points out one of the inherent weaknesses in the `@method_decorator`
technique, and it shows that a view class library like this needs to be
written and tested very carefully, with a thorough understanding of the
underlying Django code.

Finally, I found the lack of completeness in libraries like django-braces
to be disappointing. The `daydreamer` library remedies this problem by
implementing the full suite of Django's view decorators as view behavior
classes that can be mixed and matched with a higher degree of confidence.
It also provides a ton of object-oriented hooks that you can use to make
minor or major adjustments to the decisions implemented by the library.

## Editorial

Depending on your perspective, you may love or hate the object-oriented design
for the view classes provided by `daydreamer`. The library encourages the use
of a lot of multiple inheritance supported by `super()` chaining.

If you want Python to be Java, where you have single inheritance and some
"mixins" that work kind of like interfaces, you'll probably hate this design.

If you want Python to be C++, where methods with the same name, inherited from
multiple base classes need to be manually resolved, you'll probably find the
design horribly confusing.

If you're like me, and you want Python to be Common Lisp, where cooperative
"next method" chaining is a common and powerful design pattern, you'll probably
love this design.

Python inherited its `super()` functionality and method resolution order
algorithm from Dylan with the release of Python 2.3. Dylan got the idea from
Common Lisp. I believe that all high-level languages have Common Lisp
envy. By embracing the Lisp tools that have trickled into Python, a new world
of code design patterns emerges. If you're interested in learning more about
Python's method resolution order (MRO), check out
<a href="http://python-history.blogspot.com/2010/06/method-resolution-order.html" target="_blank">
    Guido's article on the history of MRO
</a>.
If you are interested in learning where these ideas came from, pick up a copy of
<a href="http://www.amazon.com/ANSI-Common-LISP-Paul-Graham/dp/0133708756/" target="_blank">
    Paul Graham's *ANSI Common Lisp*
</a>,
or if you're feeling more adventurous and want to see how to actually build
these things, try tackling
<a href="http://www.paulgraham.com/onlisptext.html" target="_blank">
    Paul Graham's incredible *On Lisp*
</a>.
