from __future__ import unicode_literals

import collections
import copy as copying

from django.utils import six


__all__ = ("updated",)


def updated(destination, source, copy=False):
    """
    Updates the destination dictionary or dictionary-like object with the
    source dictionary. Optionally makes a shallow copy of the destination
    before the update. Returns the updated dictionary.
    
    """
    if copy:
        if isinstance(
            getattr(destination, "copy", None), collections.Callable):
            destination = destination.copy()
        else:
            destination = copying.copy(destination)
    
    if isinstance(destination, collections.MutableMapping):
        destination.update(source)
    else:
        for key, value in six.iteritems(
                source
                    if isinstance(source, collections.Mapping)
                    else dict(source)):
            destination[key] = value
    return destination


def any(values, falsy=False):
    """
    Returns the first truthy value encountered in the values iterable,
    falling back to the given falsy value.
    
    """
    for value in values:
        if value:
            return value
    return falsy


def all(values, truthy=True):
    """
    Returns the first falsy value encountered in the values interable,
    falling back to the given truthy value.
    
    """
    for value in values:
        if not value:
            return value
    return truthy

