"""Traversal strategies for template embodiment.

This module provides different strategies for traversing and embodying templates:
- RecursiveVisitorEngine: Dynamic traversal using the Visitor pattern
- CompiledPathEngine: Pre-compiled path-based traversal for performance
"""

from typing import Any, Dict, Set, Optional
from embody.substitution import substitute
from embody.util import (
    flatten_to_tuples, unflatten_from_tuples, detect_cycle, CycleError
)


class KeyCollisionError(Exception):
    """Raised when dynamic keys resolve to the same value."""
    pass


class BaseEmbodimentEngine:
    """Base class for embodiment engines."""

    def __init__(
        self,
        syntax: str = 'dollar_brace',
        strict: bool = False,
        key_collision: str = 'error'
    ):
        """Initialize an embodiment engine.

        Args:
            syntax: Template variable syntax
            strict: If True, raise errors for missing parameters
            key_collision: How to handle key collisions: 'error', 'last_wins', 'namespace'
        """
        self.syntax = syntax
        self.strict = strict
        self.key_collision = key_collision

    def embody(self, template: Any, params: Dict[str, Any]) -> Any:
        """Embody a template with parameters.

        Args:
            template: The template to embody
            params: Parameters for substitution

        Returns:
            Embodied object
        """
        raise NotImplementedError


class RecursiveVisitorEngine(BaseEmbodimentEngine):
    """Dynamic traversal strategy using the Visitor pattern.

    This engine recursively walks the template structure at runtime,
    visiting each node and performing substitutions. It's best for:
    - One-off templates
    - Dynamic templates with conditional logic
    - Templates where structure changes based on parameters

    Examples:
        >>> engine = RecursiveVisitorEngine()
        >>> template = {'greeting': 'Hello ${name}', 'count': '${num}'}
        >>> engine.embody(template, {'name': 'Alice', 'num': 42})
        {'greeting': 'Hello Alice', 'count': 42}
    """

    def embody(
        self,
        template: Any,
        params: Dict[str, Any],
        visited: Optional[Set[int]] = None
    ) -> Any:
        """Recursively embody a template.

        Args:
            template: Template to embody
            params: Parameters for substitution
            visited: Set of visited object IDs (for cycle detection)

        Returns:
            Embodied object

        Raises:
            CycleError: If a circular reference is detected
        """
        if visited is None:
            visited = set()

        # Cycle detection for container types
        if isinstance(template, (dict, list, tuple)):
            obj_id = id(template)
            if obj_id in visited:
                raise CycleError("Circular reference detected during embodiment")
            visited = visited | {obj_id}  # Create new set to avoid mutation

        # Visit based on type
        if isinstance(template, dict):
            return self._visit_dict(template, params, visited)
        elif isinstance(template, list):
            return self._visit_list(template, params, visited)
        elif isinstance(template, tuple):
            return tuple(self._visit_list(list(template), params, visited))
        elif isinstance(template, str):
            return self._visit_string(template, params)
        else:
            # Scalar values returned as-is
            return template

    def _visit_string(self, template: str, params: Dict[str, Any]) -> Any:
        """Visit a string template and perform substitution.

        This uses type-preserving substitution from the substitution module.
        """
        return substitute(template, params, syntax=self.syntax, strict=self.strict)

    def _visit_list(
        self,
        template: list,
        params: Dict[str, Any],
        visited: Set[int]
    ) -> list:
        """Visit a list template and recursively embody each item."""
        return [
            self.embody(item, params, visited)
            for item in template
        ]

    def _visit_dict(
        self,
        template: dict,
        params: Dict[str, Any],
        visited: Set[int]
    ) -> dict:
        """Visit a dict template and recursively embody keys and values.

        This is the most complex case because both keys and values can be templated.
        We must:
        1. Build a new dict (can't modify dict during iteration)
        2. Handle dynamic keys (keys that contain variables)
        3. Detect and handle key collisions
        """
        # Build list of (embodied_key, embodied_value) pairs
        items = []
        for key, value in template.items():
            # Embody both key and value
            embodied_key = self.embody(key, params, visited)
            embodied_value = self.embody(value, params, visited)
            items.append((embodied_key, embodied_value))

        # Check for key collisions
        keys = [k for k, v in items]
        unique_keys = set(keys)

        if len(keys) != len(unique_keys):
            # We have collisions
            if self.key_collision == 'error':
                # Find the duplicate keys
                seen = set()
                duplicates = set()
                for k in keys:
                    if k in seen:
                        duplicates.add(k)
                    seen.add(k)
                raise KeyCollisionError(
                    f"Dynamic keys resolved to same value: {duplicates}"
                )
            elif self.key_collision == 'last_wins':
                # Just use dict() which will use last value for duplicate keys
                pass
            elif self.key_collision == 'namespace':
                # Add suffix to make keys unique
                key_counts = {}
                new_items = []
                for k, v in items:
                    if k in key_counts:
                        # This is a duplicate, add suffix
                        key_counts[k] += 1
                        unique_key = f"{k}_{key_counts[k]}"
                        new_items.append((unique_key, v))
                    else:
                        key_counts[k] = 0
                        new_items.append((k, v))
                items = new_items

        return dict(items)


class CompiledPathEngine(BaseEmbodimentEngine):
    """Pre-compiled path-based traversal strategy.

    This engine flattens the template into a path map, performs substitutions,
    and then reconstructs the structure. It's best for:
    - Templates embodied repeatedly (e.g., API responses)
    - Static templates with known structure
    - Performance-critical paths

    The compilation happens once, then embodiment is a linear scan.

    Examples:
        >>> engine = CompiledPathEngine()
        >>> template = {'a': {'b': '${x}'}, 'c': '${y}'}
        >>> compiled = engine.compile(template)
        >>> engine.embody_compiled(compiled, {'x': 1, 'y': 2})
        {'a': {'b': 1}, 'c': 2}
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._compiled_cache = {}

    def compile(self, template: Any) -> Dict:
        """Compile a template into a flat path map.

        Args:
            template: Template to compile

        Returns:
            Compiled template data

        Examples:
            >>> engine = CompiledPathEngine()
            >>> template = {'a': {'b': '${x}'}}
            >>> compiled = engine.compile(template)
            >>> compiled['flat']
            {('a', 'b'): '${x}'}
        """
        # Flatten template to tuple paths
        flat = flatten_to_tuples(template)

        # Identify which paths need substitution
        templated_paths = {}
        for path, value in flat.items():
            if isinstance(value, str):
                # Check if it contains template markers
                from embody.substitution import extract_template_vars
                vars_in_val = extract_template_vars(value, self.syntax)
                if vars_in_val:
                    templated_paths[path] = value

        return {
            'flat': flat,
            'templated_paths': templated_paths,
            'original_template': template
        }

    def embody_compiled(
        self,
        compiled: Dict,
        params: Dict[str, Any]
    ) -> Any:
        """Embody a pre-compiled template.

        Args:
            compiled: Compiled template from compile()
            params: Parameters for substitution

        Returns:
            Embodied object
        """
        flat = compiled['flat'].copy()

        # Substitute all templated paths
        for path, template_str in compiled['templated_paths'].items():
            embodied_value = substitute(
                template_str,
                params,
                syntax=self.syntax,
                strict=self.strict
            )
            flat[path] = embodied_value

        # Reconstruct the nested structure
        return unflatten_from_tuples(flat)

    def embody(self, template: Any, params: Dict[str, Any]) -> Any:
        """Embody a template (compiles on first use, caches compilation).

        Args:
            template: Template to embody
            params: Parameters for substitution

        Returns:
            Embodied object
        """
        # Use template id as cache key
        template_id = id(template)

        if template_id not in self._compiled_cache:
            self._compiled_cache[template_id] = self.compile(template)

        compiled = self._compiled_cache[template_id]
        return self.embody_compiled(compiled, params)


class IterativeStackEngine(BaseEmbodimentEngine):
    """Iterative stack-based traversal strategy.

    This engine uses an explicit stack instead of recursion, which is more
    memory-efficient for very deep structures and avoids Python's recursion limit.

    Best for:
    - Very deeply nested structures (>100 levels)
    - When recursion depth is a concern
    """

    def embody(self, template: Any, params: Dict[str, Any]) -> Any:
        """Embody using iterative stack-based traversal.

        Args:
            template: Template to embody
            params: Parameters for substitution

        Returns:
            Embodied object
        """
        # Stack of (object, parent, key) tuples
        # We'll build the result bottom-up
        stack = [(template, None, None)]
        results = {}  # Map id(obj) -> embodied result
        visited = set()

        while stack:
            obj, parent, key = stack.pop()
            obj_id = id(obj)

            # Cycle detection
            if isinstance(obj, (dict, list)) and obj_id in visited:
                raise CycleError("Circular reference detected")

            if isinstance(obj, str):
                # Leaf: substitute
                result = substitute(obj, params, syntax=self.syntax, strict=self.strict)
                results[obj_id] = result

            elif isinstance(obj, dict):
                visited.add(obj_id)
                # Check if all children are processed
                all_children_done = all(
                    id(k) in results and id(v) in results
                    for k, v in obj.items()
                )

                if all_children_done:
                    # Build the dict with embodied children
                    embodied_dict = {
                        results[id(k)]: results[id(v)]
                        for k, v in obj.items()
                    }
                    results[obj_id] = embodied_dict
                else:
                    # Re-add to stack (will process after children)
                    stack.append((obj, parent, key))
                    # Add children to stack
                    for k, v in obj.items():
                        if id(k) not in results:
                            stack.append((k, obj, 'key'))
                        if id(v) not in results:
                            stack.append((v, obj, 'value'))

            elif isinstance(obj, list):
                visited.add(obj_id)
                # Check if all items are processed
                all_items_done = all(id(item) in results for item in obj)

                if all_items_done:
                    embodied_list = [results[id(item)] for item in obj]
                    results[obj_id] = embodied_list
                else:
                    # Re-add to stack
                    stack.append((obj, parent, key))
                    # Add items to stack
                    for item in obj:
                        if id(item) not in results:
                            stack.append((item, obj, 'item'))

            else:
                # Scalar, return as-is
                results[obj_id] = obj

        return results[id(template)]


# Registry of available strategies
STRATEGIES = {
    'recursive': RecursiveVisitorEngine,
    'compiled': CompiledPathEngine,
    'iterative': IterativeStackEngine,
}


def get_engine(strategy: str = 'recursive', **kwargs) -> BaseEmbodimentEngine:
    """Get an embodiment engine by name.

    Args:
        strategy: Name of strategy ('recursive', 'compiled', 'iterative')
        **kwargs: Arguments to pass to engine constructor

    Returns:
        Embodiment engine instance

    Examples:
        >>> engine = get_engine('recursive', syntax='brace')
        >>> isinstance(engine, RecursiveVisitorEngine)
        True
    """
    engine_class = STRATEGIES.get(strategy, RecursiveVisitorEngine)
    return engine_class(**kwargs)
