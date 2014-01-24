from __future__ import unicode_literals

import collections

from django.utils import six
from django.utils.decorators import classonlymethod
from django.views.decorators import debug

from .. import generic


__all__ = ("SensitiveVariables", "SensitivePostParameters",)


class SensitiveVariables(generic.View):
    """
    A view behavior that marks specified variable names as sensitive so that
    their values are not displayed by Django's error logging mechanisms in
    production (when settings.DEBUG == False).
    
    Set sensitive_variables to a string or iterable of strings to mark specific
    variable names as sensitive. Set it to a truthy value to mark all variable
    names as sensitive. Set it to a falsy value to disable the behavior. Its
    default value is True to protect all variables.
    
    See the django.views.decorators.debug.sensitive_variables() decorator
    for details.
    
    """
    sensitive_variables = True
    
    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Optionally wrap the base view in
        django.views.decorators.debug.sensitive_variables().
        
        """
        # Normalize the setting.
        variables = cls.sensitive_variables
        if isinstance(variables, six.string_types):
            variables = (variables,)
        elif isinstance(variables, collections.Iterable):
            variables = tuple(variables)
        elif variables:
            variables = ()
        else:
            variables = None
        
        view = super(SensitiveVariables, cls).as_view(**kwargs)
        return (
            debug.sensitive_variables(*variables)(view)
                if variables is not None
                else view)


class SensitivePostParameters(generic.View):
    """
    A view behavior that marks specified POST parameter names as sensitive so
    that their values are not displayed by Django's error logging mechanisms
    in production (when settings.DEBUG == False).
    
    Set sensitive_postt_parameters to a string or iterable of strings to mark
    specific POST parameter names as sensitive. Set it to a truthy value to
    mark all POST parameter names as sensitive. Set it to a falsy value to
    disable the behavior. Its default value is True to protect all
    POST parameters.
    
    See the django.views.decorators.debug.sensitive_post_parameters() decorator
    for details.
    
    """
    sensitive_post_parameters = True
    
    @classonlymethod
    def as_view(cls, **kwargs):
        """
        Optionally wrap the base view in
        django.views.decorators.debug.sensitive_post_parameters().
        
        """
        # Normalize the setting.
        parameters = cls.sensitive_post_parameters
        if isinstance(parameters, six.string_types):
            parameters = (parameters,)
        elif isinstance(parameters, collections.Iterable):
            parameters = tuple(parameters)
        elif parameters:
            parameters = ()
        else:
            parameters = None
        
        view = super(SensitivePostParameters, cls).as_view(**kwargs)
        return (
            debug.sensitive_post_parameters(*parameters)(view)
                if parameters is not None
                else view)
