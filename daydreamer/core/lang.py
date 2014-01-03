from __future__ import unicode_literals

import copy as copying

from django.utils import six


__all__ = ("extended", "updated",)


def extended(destination, source, copy=False):
    """
    Extends the destination list with the given source iterable. Optionally
    makes a shallow copy of the destination before the update. Returns the
    extended list.
    
    """
    if copy:
        destination = copying.copy(destination)
    if callable(getattr(destination, "extend", None)):
        destination.extend(source)
    else:
        for value in source:
            destination.append(value)
    return destination


def updated(destination, source, copy=False):
    """
    Updates the destination dictionary or dictionary-like object with the
    source dictionary. Optionally makes a shallow copy of the destination
    before the update. Returns the updated dictionary.
    
    """
    if copy:
        if callable(getattr(destination, "copy", None)):
            destination = destination.copy()
        else:
            destination = copying.copy(destination)
    if callable(getattr(destination, "update", None)):
        destination.update(source)
    else:
        for key, value in six.iteritems(source):
            destination[key] = value
    return destination
