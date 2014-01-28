from __future__ import unicode_literals

from daydreamer.views.behaviors import debug

from . import base


class SensitiveVariablesTestCase(base.TestCase):
    """
    Tests for the SensitiveVariables view behavior.
    
    """
    view_classes = debug.SensitiveVariables
    
    def test_defaults(self):
        """
        Check that the special marker for all sensitive variables is set on
        the generated view.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content},
            status_code=200,
            content=content,
            view_exact={"sensitive_variables": "__ALL__"})
    
    def test_single(self):
        """
        Check that a single sensitive variable is set on the
        generated view.
        
        """
        content = self.unique()
        variable = self.unique_variable()
        self.assertViewBehavior(
            {"sensitive_variables": variable, "get": content},
            status_code=200,
            content=content,
            view_exact={"sensitive_variables": (variable,)})
    
    def test_multiple(self):
        """
        Check that multiple sensitive variables are set on the
        generated view.
        
        """
        content = self.unique()
        variables = (self.unique_variable(), self.unique_variable(),)
        self.assertViewBehavior(
            {"sensitive_variables": variables, "get": content},
            status_code=200,
            content=content,
            view_exact={"sensitive_variables": variables})
    
    def test_disabled(self):
        """
        Check that sensitive variables are not set on the generated view
        when the behavior is disabled.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"sensitive_variables": None, "get": content},
            status_code=200,
            content=content,
            view_excludes="sensitive_variables")
    
    def test_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        and that sensitive variables are set on the generated view.
        
        """
        self.assertViewBehavior(
            status_code=405,
            view_exact={"sensitive_variables": "__ALL__"})
    
    def test_disabled_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        and that sensitive variables are not set on the generated view when
        the behavior is disabled.
        
        """
        self.assertViewBehavior(
            {"sensitive_variables": None},
            status_code=405,
            view_excludes="sensitive_variables")


class SensitivePostParametersTestCase(base.TestCase):
    """
    Tests for the SensitivePostParameters view behavior.
    
    """
    view_classes = debug.SensitivePostParameters
    
    def test_defaults(self):
        """
        Check that the special marker for all sensitive POST parameters is set
        on the request.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"get": content},
            status_code=200,
            content=content,
            request_exact={"sensitive_post_parameters": "__ALL__"})
    
    def test_single(self):
        """
        Check that a single sensitive POST parameter is set on the
        generated request.
        
        """
        content = self.unique()
        parameter = self.unique_variable()
        self.assertViewBehavior(
            {"sensitive_post_parameters": parameter, "get": content},
            status_code=200,
            content=content,
            request_exact={"sensitive_post_parameters": (parameter,)})
    
    def test_multiple(self):
        """
        Check that multiple sensitive POST parameters are set on the request.
        
        """
        content = self.unique()
        parameters = (self.unique_variable(), self.unique_variable(),)
        self.assertViewBehavior(
            {"sensitive_post_parameters": parameters, "get": content},
            status_code=200,
            content=content,
            request_exact={"sensitive_post_parameters": parameters})
    
    def test_disabled(self):
        """
        Check that sensitive POST parameters are not set on the request when
        the behavior is disabled.
        
        """
        content = self.unique()
        self.assertViewBehavior(
            {"sensitive_post_parameters": None, "get": content},
            status_code=200,
            content=content,
            request_excludes="sensitive_post_parameters")
    
    def test_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        and that sensitive POST parameters are set on the request.
        
        """
        self.assertViewBehavior(
            status_code=405,
            request_exact={"sensitive_post_parameters": "__ALL__"})
    
    def test_disabled_precedence(self):
        """
        Check that the default HTTP method name protection takes precedence
        and that sensitive POST parameters are not set on the request when the
        behavior is disabled.
        
        """
        self.assertViewBehavior(
            {"sensitive_post_parameters": None},
            status_code=405,
            request_excludes="sensitive_post_parameters")
