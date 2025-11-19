"""Utility functions for embody: flattening, unflattening, and cycle detection.

This module provides helper functions for working with nested data structures,
including path-based operations and cycle detection for safe traversal.
"""

from typing import Any, Union, Tuple, List, Dict, Set
from collections.abc import Mapping, Sequence


class CycleError(Exception):
    """Raised when a circular reference is detected in a data structure."""
    pass


class PathNotFoundError(Exception):
    """Raised when a path doesn't exist in a data structure."""
    pass


def detect_cycle(obj: Any, visited: Set[int] = None, path: List[str] = None) -> None:
    """Detect cycles in a nested data structure.

    Args:
        obj: The object to check for cycles
        visited: Set of object IDs already visited
        path: Current path in the structure (for error reporting)

    Raises:
        CycleError: If a cycle is detected

    Examples:
        >>> d = {'a': 1, 'b': [2, 3]}
        >>> detect_cycle(d)  # No cycle, returns None

        >>> circular = {'a': 1}
        >>> circular['self'] = circular
        >>> try:
        ...     detect_cycle(circular)
        ... except CycleError as e:
        ...     print("Cycle detected")
        Cycle detected
    """
    if visited is None:
        visited = set()
    if path is None:
        path = []

    obj_id = id(obj)

    # Only check for cycles in container types
    if isinstance(obj, (dict, list, tuple, set)):
        if obj_id in visited:
            path_str = ' -> '.join(path) if path else 'root'
            raise CycleError(
                f"Circular reference detected at path: {path_str}"
            )

        visited.add(obj_id)

        try:
            if isinstance(obj, dict):
                for key, value in obj.items():
                    detect_cycle(value, visited, path + [str(key)])
            elif isinstance(obj, (list, tuple, set)):
                for i, item in enumerate(obj):
                    detect_cycle(item, visited, path + [f'[{i}]'])
        finally:
            # Remove from visited after checking (allows diamond structures)
            visited.discard(obj_id)


def flatten_dict(
    nested_dict: Dict[str, Any],
    separator: str = '.',
    parent_key: str = ''
) -> Dict[str, Any]:
    """Flatten a nested dictionary into a single-level dictionary with path keys.

    Args:
        nested_dict: Nested dictionary to flatten
        separator: String to use for separating path components
        parent_key: Key of the parent (used in recursion)

    Returns:
        Flattened dictionary with path keys

    Examples:
        >>> d = {'a': {'b': {'c': 1}}, 'd': 2}
        >>> flatten_dict(d)
        {'a.b.c': 1, 'd': 2}

        >>> d = {'user': {'name': 'Alice', 'age': 30}}
        >>> flatten_dict(d)
        {'user.name': 'Alice', 'user.age': 30}

        >>> d = {'items': [1, 2, 3]}
        >>> flatten_dict(d)
        {'items.0': 1, 'items.1': 2, 'items.2': 3}
    """
    items = []
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(flatten_dict(value, separator, new_key).items())
        elif isinstance(value, list):
            for i, item in enumerate(value):
                list_key = f"{new_key}{separator}{i}"
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, separator, list_key).items())
                else:
                    items.append((list_key, item))
        else:
            items.append((new_key, value))

    return dict(items)


def flatten_to_tuples(
    obj: Any,
    parent_path: Tuple = ()
) -> Dict[Tuple, Any]:
    """Flatten a nested structure using tuple paths (unambiguous).

    This avoids the ambiguity of string separators. A tuple path like
    ('a', 'b', 0) is unambiguous, while 'a.b.0' could mean multiple things
    if keys contain dots.

    Args:
        obj: Object to flatten
        parent_path: Current path as tuple

    Returns:
        Dictionary mapping tuple paths to values

    Examples:
        >>> d = {'a': {'b': [1, 2]}}
        >>> flatten_to_tuples(d)
        {('a', 'b', 0): 1, ('a', 'b', 1): 2}
    """
    if isinstance(obj, dict):
        items = []
        for key, value in obj.items():
            current_path = parent_path + (key,)
            if isinstance(value, (dict, list)):
                items.extend(flatten_to_tuples(value, current_path).items())
            else:
                items.append((current_path, value))
        return dict(items)
    elif isinstance(obj, list):
        items = []
        for i, item in enumerate(obj):
            current_path = parent_path + (i,)
            if isinstance(item, (dict, list)):
                items.extend(flatten_to_tuples(item, current_path).items())
            else:
                items.append((current_path, item))
        return dict(items)
    else:
        # Scalar value
        return {parent_path: obj} if parent_path else {}


def unflatten_dict(
    flat_dict: Dict[str, Any],
    separator: str = '.'
) -> Dict[str, Any]:
    """Unflatten a dictionary with path keys into a nested structure.

    Args:
        flat_dict: Flattened dictionary with path keys
        separator: String used for separating path components

    Returns:
        Nested dictionary structure

    Examples:
        >>> flat = {'a.b.c': 1, 'd': 2}
        >>> unflatten_dict(flat)
        {'a': {'b': {'c': 1}}, 'd': 2}

        >>> flat = {'items.0': 'a', 'items.1': 'b'}
        >>> unflatten_dict(flat)
        {'items': ['a', 'b']}
    """
    result = {}

    for key, value in flat_dict.items():
        parts = key.split(separator)
        current = result

        for i, part in enumerate(parts[:-1]):
            # Check if next part is a number (indicates list)
            next_part = parts[i + 1]
            is_next_numeric = next_part.isdigit()

            if part not in current:
                # Create list or dict based on next part
                current[part] = [] if is_next_numeric else {}

            current = current[part]

        # Set the final value
        final_key = parts[-1]
        if isinstance(current, list):
            # Extend list if necessary
            idx = int(final_key)
            while len(current) <= idx:
                current.append(None)
            current[idx] = value
        else:
            current[final_key] = value

    return result


def unflatten_from_tuples(flat_dict: Dict[Tuple, Any]) -> Any:
    """Unflatten a dictionary with tuple paths into a nested structure.

    Args:
        flat_dict: Dictionary with tuple paths as keys

    Returns:
        Nested structure (dict or list)

    Examples:
        >>> flat = {('a', 'b', 0): 1, ('a', 'b', 1): 2}
        >>> unflatten_from_tuples(flat)
        {'a': {'b': [1, 2]}}
    """
    if not flat_dict:
        return {}

    result = {}

    for path, value in flat_dict.items():
        if not path:
            continue

        current = result
        for i, key in enumerate(path[:-1]):
            # Determine if next level should be list or dict
            next_key = path[i + 1]
            is_next_numeric = isinstance(next_key, int)

            if key not in current:
                current[key] = [] if is_next_numeric else {}

            current = current[key]

        # Set final value
        final_key = path[-1]
        if isinstance(current, list):
            idx = final_key
            while len(current) <= idx:
                current.append(None)
            current[idx] = value
        else:
            current[final_key] = value

    return result


def get_by_path(
    obj: Any,
    path: Union[str, Tuple],
    separator: str = '.',
    default: Any = None
) -> Any:
    """Get a value from a nested structure by path.

    Args:
        obj: Nested structure
        path: Path as string or tuple
        separator: Separator for string paths
        default: Default value if path not found

    Returns:
        Value at the path, or default if not found

    Examples:
        >>> d = {'a': {'b': {'c': 42}}}
        >>> get_by_path(d, 'a.b.c')
        42
        >>> get_by_path(d, ('a', 'b', 'c'))
        42
        >>> get_by_path(d, 'a.b.x', default='not found')
        'not found'
    """
    if isinstance(path, str):
        path = tuple(path.split(separator))

    current = obj
    for key in path:
        try:
            if isinstance(current, (dict, Mapping)):
                current = current[key]
            elif isinstance(current, (list, tuple, Sequence)):
                current = current[int(key)]
            else:
                return default
        except (KeyError, IndexError, ValueError, TypeError):
            return default

    return current


def set_by_path(
    obj: Dict,
    path: Union[str, Tuple],
    value: Any,
    separator: str = '.',
    create_intermediate: bool = True
) -> None:
    """Set a value in a nested structure by path (modifies in place).

    Args:
        obj: Nested structure to modify
        path: Path as string or tuple
        value: Value to set
        separator: Separator for string paths
        create_intermediate: If True, create intermediate dicts/lists as needed

    Examples:
        >>> d = {}
        >>> set_by_path(d, 'a.b.c', 42)
        >>> d
        {'a': {'b': {'c': 42}}}
    """
    if isinstance(path, str):
        path = tuple(path.split(separator))

    if not path:
        raise ValueError("Path cannot be empty")

    current = obj
    for key in path[:-1]:
        if key not in current:
            if create_intermediate:
                current[key] = {}
            else:
                raise PathNotFoundError(f"Path not found: {key}")
        current = current[key]

    current[path[-1]] = value


def max_depth(obj: Any, current_depth: int = 0) -> int:
    """Calculate the maximum depth of a nested structure.

    Args:
        obj: Object to measure
        current_depth: Current depth (used in recursion)

    Returns:
        Maximum depth

    Examples:
        >>> max_depth({'a': 1})
        1
        >>> max_depth({'a': {'b': {'c': 1}}})
        3
        >>> max_depth([1, [2, [3, 4]]])
        3
    """
    if isinstance(obj, dict):
        if not obj:
            return current_depth
        return max(max_depth(v, current_depth + 1) for v in obj.values())
    elif isinstance(obj, (list, tuple)):
        if not obj:
            return current_depth
        return max(max_depth(item, current_depth + 1) for item in obj)
    else:
        return current_depth


def count_template_markers(obj: Any, syntax: str = 'dollar_brace') -> int:
    """Count the number of template markers in a nested structure.

    Args:
        obj: Object to count markers in
        syntax: Template syntax to look for

    Returns:
        Number of template markers found

    Examples:
        >>> count_template_markers({'a': '${x}', 'b': '${y}'})
        2
        >>> count_template_markers(['${a}', 'literal', '${b} and ${c}'])
        3
    """
    from embody.substitution import extract_template_vars

    count = 0
    if isinstance(obj, str):
        count += len(extract_template_vars(obj, syntax))
    elif isinstance(obj, dict):
        for key, value in obj.items():
            count += count_template_markers(key, syntax)
            count += count_template_markers(value, syntax)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            count += count_template_markers(item, syntax)

    return count
