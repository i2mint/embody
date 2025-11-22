"""Core classes for embody: Context, Template, and Embodier.

This module provides the foundational classes for the embody framework,
implementing the pattern: obj = embody(template, parameters).
"""

from typing import Any, Dict, Optional, Callable, Union
from collections.abc import Mapping
from embody.substitution import substitute, extract_template_vars
from embody.util import detect_cycle, CycleError


class MissingParameterError(Exception):
    """Raised when a required template parameter is missing."""
    pass


class Context(Mapping):
    """Parameter store for template embodiment with support for resolvers.

    The Context holds parameters for substitution and supports:
    - Hierarchical scoping (global → local overrides)
    - Resolver functions (lazy evaluation)
    - Callable values that are invoked on access

    Examples:
        >>> ctx = Context({'name': 'Alice', 'age': 30})
        >>> ctx['name']
        'Alice'

        >>> import datetime
        >>> ctx = Context({'now': lambda: datetime.datetime.now()})
        >>> ctx['now']  # doctest: +SKIP
        datetime.datetime(...)

        >>> ctx = Context({'base': 10}, parent={'base': 5, 'other': 20})
        >>> ctx['base']  # Local overrides parent
        10
        >>> ctx['other']  # Falls back to parent
        20
    """

    def __init__(
        self,
        params: Dict[str, Any] = None,
        parent: 'Context' = None,
        resolvers: Dict[str, Callable] = None,
        auto_call: bool = True
    ):
        """Initialize a Context.

        Args:
            params: Dictionary of parameters
            parent: Parent context for hierarchical scoping
            resolvers: Named resolver functions
            auto_call: If True, automatically call callable values
        """
        self._params = params or {}
        self._parent = parent
        self._resolvers = resolvers or {}
        self._auto_call = auto_call

    def __getitem__(self, key: str) -> Any:
        """Get a parameter value with resolver and parent fallback."""
        # Try local params first
        if key in self._params:
            value = self._params[key]
            # Auto-call if it's a callable and auto_call is True
            if self._auto_call and callable(value):
                return value()
            return value

        # Try parent context
        if self._parent is not None:
            try:
                return self._parent[key]
            except KeyError:
                pass

        # Try resolvers
        if key in self._resolvers:
            return self._resolvers[key]()

        raise KeyError(f"Parameter not found: {key}")

    def __iter__(self):
        """Iterate over all keys (including parent)."""
        keys = set(self._params.keys())
        if self._parent:
            keys.update(self._parent.keys())
        keys.update(self._resolvers.keys())
        return iter(keys)

    def __len__(self):
        """Return number of unique keys."""
        return len(set(self.keys()))

    def get(self, key: str, default=None) -> Any:
        """Get a parameter with a default value."""
        try:
            return self[key]
        except KeyError:
            return default

    def update(self, params: Dict[str, Any]) -> 'Context':
        """Create a new context with updated parameters.

        Args:
            params: Parameters to add/override

        Returns:
            New Context with updated parameters
        """
        new_params = {**self._params, **params}
        return Context(
            new_params,
            parent=self._parent,
            resolvers=self._resolvers,
            auto_call=self._auto_call
        )

    def register_resolver(self, name: str, func: Callable):
        """Register a named resolver function.

        Args:
            name: Name of the resolver
            func: Callable that returns the resolved value

        Examples:
            >>> import os
            >>> ctx = Context()
            >>> ctx.register_resolver('env', lambda: os.environ.get('USER', 'unknown'))
        """
        self._resolvers[name] = func

    def child(self, params: Dict[str, Any] = None) -> 'Context':
        """Create a child context with this context as parent.

        Args:
            params: Parameters for the child context

        Returns:
            New Context with this as parent
        """
        return Context(params or {}, parent=self)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a plain dictionary (resolving all values).

        Returns:
            Dictionary with all parameters resolved
        """
        result = {}
        for key in self:
            result[key] = self[key]
        return result


class TemplateWrapper:
    """Wrapper for template data with introspection capabilities.

    This class wraps template data and provides methods to:
    - Extract variable dependencies
    - Detect cycles
    - Parse and validate the template structure

    Examples:
        >>> template = TemplateWrapper({'name': '${user}', 'age': '${years}'})
        >>> template.get_dependencies()
        {'user', 'years'}
    """

    def __init__(
        self,
        template: Any,
        syntax: str = 'dollar_brace',
        check_cycles: bool = True
    ):
        """Initialize a TemplateWrapper.

        Args:
            template: The template data
            syntax: Variable syntax to use
            check_cycles: If True, check for circular references

        Raises:
            CycleError: If circular reference detected
        """
        self.template = template
        self.syntax = syntax

        if check_cycles:
            try:
                detect_cycle(template)
            except CycleError as e:
                raise CycleError(f"Template contains circular reference: {e}")

    def get_dependencies(self) -> set[str]:
        """Extract all template variables from the template.

        Returns:
            Set of variable names used in the template
        """
        dependencies = set()
        self._extract_dependencies(self.template, dependencies)
        return dependencies

    def _extract_dependencies(self, obj: Any, deps: set):
        """Recursively extract dependencies from nested structure."""
        if isinstance(obj, str):
            vars_in_str = extract_template_vars(obj, self.syntax)
            deps.update(vars_in_str)
        elif isinstance(obj, dict):
            for key, value in obj.items():
                self._extract_dependencies(key, deps)
                self._extract_dependencies(value, deps)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                self._extract_dependencies(item, deps)

    def validate_params(self, params: Union[Dict, Context]) -> list[str]:
        """Check which template dependencies are missing from params.

        Args:
            params: Parameters to check against

        Returns:
            List of missing parameter names
        """
        required = self.get_dependencies()
        available = set(params.keys())
        missing = required - available
        return list(missing)


class Embodier:
    """Main class for embodying templates with parameters.

    This is the primary API for the embody framework. It supports:
    - Multiple traversal strategies (recursive, compiled, auto)
    - Multiple syntax styles
    - Strict or lenient parameter checking
    - Cycle detection

    Examples:
        >>> template = {'greeting': 'Hello ${name}', 'age': '${age}'}
        >>> embodier = Embodier(template)
        >>> embodier({'name': 'Alice', 'age': 30})
        {'greeting': 'Hello Alice', 'age': 30}

        >>> template = {'count': '${num}'}
        >>> embodier = Embodier(template)
        >>> embodier({'num': 42})  # Type preserved
        {'count': 42}
    """

    def __init__(
        self,
        template: Any,
        strategy: str = 'auto',
        syntax: str = 'dollar_brace',
        strict: bool = False,
        check_cycles: bool = True,
        key_collision: str = 'error'
    ):
        """Initialize an Embodier.

        Args:
            template: The template to embody
            strategy: 'recursive', 'compiled', or 'auto'
            syntax: Variable syntax ('dollar_brace', 'brace', 'double_bracket')
            strict: If True, raise errors for missing parameters
            check_cycles: If True, check for circular references
            key_collision: How to handle key collisions: 'error', 'last_wins', 'namespace'
        """
        self.template_wrapper = TemplateWrapper(template, syntax, check_cycles)
        self.template = template
        self.strategy = strategy
        self.syntax = syntax
        self.strict = strict
        self.key_collision = key_collision

        # Select strategy (will be implemented in strategies.py)
        self._strategy_impl = None
        if strategy == 'compiled':
            # Will use CompiledPathEngine
            pass
        elif strategy == 'auto':
            # Auto-select based on template characteristics
            from embody.util import max_depth, count_template_markers
            depth = max_depth(template)
            marker_count = count_template_markers(template, syntax)
            # Use compiled strategy if deep or many markers
            if depth > 5 or marker_count > 10:
                self.strategy = 'compiled'
            else:
                self.strategy = 'recursive'

    def __call__(self, params: Union[Dict, Context] = None, **kwargs) -> Any:
        """Embody the template with the given parameters.

        Args:
            params: Parameters as dict or Context
            **kwargs: Additional parameters (merged with params)

        Returns:
            Embodied object with parameters substituted

        Raises:
            MissingParameterError: If strict=True and parameters are missing
        """
        # Combine params and kwargs
        if params is None:
            params = kwargs
        elif isinstance(params, dict):
            params = {**params, **kwargs}
        elif isinstance(params, Context):
            if kwargs:
                params = params.update(kwargs)

        # Convert Context to dict if needed (for now)
        if isinstance(params, Context):
            param_dict = params.to_dict()
        else:
            param_dict = params

        # Check for missing parameters if strict
        if self.strict:
            missing = self.template_wrapper.validate_params(param_dict)
            if missing:
                raise MissingParameterError(
                    f"Missing required parameters: {missing}"
                )

        # Use the recursive visitor strategy (strategies.py will provide more options)
        from embody.strategies import RecursiveVisitorEngine

        engine = RecursiveVisitorEngine(
            syntax=self.syntax,
            strict=self.strict,
            key_collision=self.key_collision
        )
        return engine.embody(self.template, param_dict)

    def get_signature(self) -> list[str]:
        """Get the list of parameters required by the template.

        Returns:
            List of parameter names
        """
        return list(self.template_wrapper.get_dependencies())


def embody(template: Any, params: Union[Dict, Context] = None, **kwargs) -> Any:
    """Convenience function for template embodiment.

    This is the main entry point for simple embodiment use cases.

    Args:
        template: The template to embody
        params: Parameters for substitution
        **kwargs: Additional parameters or config options

    Returns:
        Embodied object

    Examples:
        >>> embody({'name': '${name}'}, {'name': 'Alice'})
        {'name': 'Alice'}

        >>> embody({'count': '${n}'}, {'n': 42})
        {'count': 42}

        >>> embody(['${a}', '${b}'], {'a': 1, 'b': 2})
        [1, 2]
    """
    # Extract config kwargs
    config_keys = {'syntax', 'strict', 'strategy', 'check_cycles', 'key_collision'}
    config = {k: v for k, v in kwargs.items() if k in config_keys}
    params_kwargs = {k: v for k, v in kwargs.items() if k not in config_keys}

    embodier = Embodier(template, **config)
    return embodier(params, **params_kwargs)
