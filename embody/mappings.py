"""Mapping interface wrappers for embodied objects.

This module provides wrappers that convert nested structures into
uniform Mapping interfaces, supporting:
- Lazy evaluation
- Attribute access (Box pattern)
- Flat path-based access
- Immutability (frozen objects)
"""

from typing import Any, Dict, Iterator
from collections.abc import Mapping, MutableMapping
from embody.util import get_by_path, set_by_path, flatten_dict


class EmbodiedMapping(Mapping):
    """Read-only Mapping wrapper for embodied objects with lazy evaluation.

    This wrapper provides a Mapping interface around an embodied object,
    with support for lazy embodiment (values materialized on access).

    Examples:
        >>> from embody import embody
        >>> template = {'name': '${name}', 'age': '${age}'}
        >>> params = {'name': 'Alice', 'age': 30}
        >>> # Embody eagerly first
        >>> data = embody(template, params)
        >>> mapping = EmbodiedMapping(data)
        >>> mapping['name']
        'Alice'
        >>> len(mapping)
        2
    """

    def __init__(self, data: Dict[str, Any]):
        """Initialize an EmbodiedMapping.

        Args:
            data: Dictionary to wrap
        """
        self._data = data

    def __getitem__(self, key: str) -> Any:
        """Get an item by key."""
        return self._data[key]

    def __iter__(self) -> Iterator:
        """Iterate over keys."""
        return iter(self._data)

    def __len__(self) -> int:
        """Return number of items."""
        return len(self._data)

    def __repr__(self) -> str:
        return f"EmbodiedMapping({self._data!r})"


class LazyEmbodiedMapping(Mapping):
    """Lazy Mapping that embodies values on access.

    This is useful for large templates where you only need to access
    a subset of values. Values are embodied on-demand and cached.

    Examples:
        >>> from embody import Embodier
        >>> template = {'a': '${x}', 'b': '${y}', 'c': '${z}'}
        >>> params = {'x': 1, 'y': 2, 'z': 3}
        >>> embodier = Embodier(template)
        >>> lazy = LazyEmbodiedMapping(template, params, embodier)
        >>> lazy['a']  # Only 'a' is embodied
        1
    """

    def __init__(self, template: Dict, params: Dict, embodier: 'Embodier'):
        """Initialize a LazyEmbodiedMapping.

        Args:
            template: Template dictionary
            params: Parameters for embodiment
            embodier: Embodier instance to use
        """
        self._template = template
        self._params = params
        self._embodier = embodier
        self._cache = {}

    def __getitem__(self, key: str) -> Any:
        """Get an item, embodying it if not cached."""
        if key not in self._cache:
            if key not in self._template:
                raise KeyError(key)
            # Embody just this value
            template_value = self._template[key]
            from embody.base import embody
            self._cache[key] = embody(template_value, self._params)
        return self._cache[key]

    def __iter__(self) -> Iterator:
        """Iterate over template keys."""
        return iter(self._template)

    def __len__(self) -> int:
        """Return number of template keys."""
        return len(self._template)


class FlatMapping(Mapping):
    """Mapping with flattened nested structure for path-based access.

    Allows accessing nested values using dot notation as single keys.

    Examples:
        >>> nested = {'user': {'name': 'Alice', 'age': 30}}
        >>> flat = FlatMapping(nested)
        >>> flat['user.name']
        'Alice'
        >>> flat['user.age']
        30
        >>> list(flat.keys())
        ['user.name', 'user.age']
    """

    def __init__(self, data: Dict, separator: str = '.'):
        """Initialize a FlatMapping.

        Args:
            data: Nested dictionary to flatten
            separator: Separator for path components
        """
        self._data = data
        self._separator = separator
        self._flat = flatten_dict(data, separator)

    def __getitem__(self, key: str) -> Any:
        """Get an item by flattened path."""
        return self._flat[key]

    def __iter__(self) -> Iterator:
        """Iterate over flattened keys."""
        return iter(self._flat)

    def __len__(self) -> int:
        """Return number of flattened items."""
        return len(self._flat)

    def get_nested(self, *path_parts) -> Any:
        """Get a value by path components.

        Args:
            *path_parts: Path components

        Returns:
            Value at path

        Examples:
            >>> nested = {'a': {'b': {'c': 42}}}
            >>> flat = FlatMapping(nested)
            >>> flat.get_nested('a', 'b', 'c')
            42
        """
        path = self._separator.join(path_parts)
        return self[path]


class AttributeMapping(Mapping):
    """Mapping that allows attribute access (Box pattern).

    Allows accessing dictionary keys as attributes for more fluid syntax.

    Examples:
        >>> data = {'user': {'name': 'Alice', 'age': 30}}
        >>> attr_map = AttributeMapping(data)
        >>> attr_map.user.name
        'Alice'
        >>> attr_map.user.age
        30
        >>> attr_map['user']['name']  # Still works as dict
        'Alice'
    """

    def __init__(self, data: Dict):
        """Initialize an AttributeMapping.

        Args:
            data: Dictionary to wrap
        """
        self._data = data

    def __getitem__(self, key: str) -> Any:
        """Get an item by key."""
        value = self._data[key]
        # Wrap nested dicts in AttributeMapping for recursive attribute access
        if isinstance(value, dict):
            return AttributeMapping(value)
        return value

    def __getattr__(self, key: str) -> Any:
        """Get an item by attribute access."""
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __iter__(self) -> Iterator:
        """Iterate over keys."""
        return iter(self._data)

    def __len__(self) -> int:
        """Return number of items."""
        return len(self._data)

    def __repr__(self) -> str:
        return f"AttributeMapping({self._data!r})"

    def to_dict(self) -> Dict:
        """Convert back to plain dictionary.

        Returns:
            Plain dictionary
        """
        return dict(self._data)


class FrozenMapping(Mapping):
    """Immutable Mapping wrapper.

    Provides a frozen (immutable) view of a dictionary.

    Examples:
        >>> data = {'a': 1, 'b': 2}
        >>> frozen = FrozenMapping(data)
        >>> frozen['a']
        1
        >>> # Modifications to original don't affect frozen (deep copy)
        >>> data['c'] = 3
        >>> 'c' in frozen
        False
    """

    def __init__(self, data: Dict):
        """Initialize a FrozenMapping.

        Args:
            data: Dictionary to freeze (will be deep copied)
        """
        import copy
        self._data = copy.deepcopy(data)
        # Make it truly immutable by storing as tuple of items
        self._items = tuple(self._data.items())
        self._keys = tuple(self._data.keys())

    def __getitem__(self, key: str) -> Any:
        """Get an item by key."""
        return self._data[key]

    def __iter__(self) -> Iterator:
        """Iterate over keys."""
        return iter(self._keys)

    def __len__(self) -> int:
        """Return number of items."""
        return len(self._items)

    def __repr__(self) -> str:
        return f"FrozenMapping({dict(self._items)!r})"

    def __hash__(self) -> int:
        """Make hashable (required for frozen objects)."""
        return hash(self._items)


class MutableEmbodiedMapping(MutableMapping):
    """Mutable Mapping wrapper for embodied objects.

    Provides full MutableMapping interface for modifying embodied results.

    Examples:
        >>> data = {'a': 1, 'b': 2}
        >>> mutable = MutableEmbodiedMapping(data)
        >>> mutable['c'] = 3
        >>> mutable['a'] = 10
        >>> del mutable['b']
        >>> dict(mutable)
        {'a': 10, 'c': 3}
    """

    def __init__(self, data: Dict):
        """Initialize a MutableEmbodiedMapping.

        Args:
            data: Dictionary to wrap
        """
        self._data = dict(data)  # Make a copy

    def __getitem__(self, key: str) -> Any:
        """Get an item by key."""
        return self._data[key]

    def __setitem__(self, key: str, value: Any):
        """Set an item."""
        self._data[key] = value

    def __delitem__(self, key: str):
        """Delete an item."""
        del self._data[key]

    def __iter__(self) -> Iterator:
        """Iterate over keys."""
        return iter(self._data)

    def __len__(self) -> int:
        """Return number of items."""
        return len(self._data)

    def freeze(self) -> FrozenMapping:
        """Convert to an immutable FrozenMapping.

        Returns:
            Frozen version of this mapping
        """
        return FrozenMapping(self._data)


class PathMapping(Mapping):
    """Mapping supporting multiple path access styles.

    Supports:
    - Regular dict access: mapping['key']
    - Dot notation: mapping['a.b.c']
    - Tuple paths: mapping[('a', 'b', 'c')]
    - JSON Pointer: mapping['/a/b/c']

    Examples:
        >>> data = {'a': {'b': {'c': 42}}}
        >>> pm = PathMapping(data)
        >>> pm['a.b.c']
        42
        >>> pm[('a', 'b', 'c')]
        42
        >>> pm['/a/b/c']  # JSON Pointer
        42
        >>> pm['a']  # Regular access
        {'b': {'c': 42}}
    """

    def __init__(self, data: Dict, separator: str = '.'):
        """Initialize a PathMapping.

        Args:
            data: Nested dictionary
            separator: Separator for dot notation paths
        """
        self._data = data
        self._separator = separator

    def __getitem__(self, key) -> Any:
        """Get an item by various path formats."""
        if isinstance(key, tuple):
            # Tuple path
            return get_by_path(self._data, key)
        elif isinstance(key, str):
            if key.startswith('/'):
                # JSON Pointer format
                # Remove leading / and split
                parts = key[1:].split('/')
                return get_by_path(self._data, tuple(parts))
            elif self._separator in key:
                # Dot notation path
                return get_by_path(self._data, key, separator=self._separator)
            else:
                # Simple key
                return self._data[key]
        else:
            raise TypeError(f"Invalid key type: {type(key)}")

    def __iter__(self) -> Iterator:
        """Iterate over top-level keys."""
        return iter(self._data)

    def __len__(self) -> int:
        """Return number of top-level keys."""
        return len(self._data)

    def __contains__(self, key) -> bool:
        """Check if path exists."""
        try:
            self[key]
            return True
        except (KeyError, IndexError):
            return False


def as_mapping(data: Any, style: str = 'basic') -> Mapping:
    """Convert data to a Mapping with the specified style.

    Args:
        data: Data to wrap
        style: Style of mapping ('basic', 'attribute', 'flat', 'path', 'frozen')

    Returns:
        Mapping instance

    Examples:
        >>> data = {'user': {'name': 'Alice'}}
        >>> m = as_mapping(data, 'attribute')
        >>> m.user.name
        'Alice'

        >>> m = as_mapping(data, 'flat')
        >>> m['user.name']
        'Alice'
    """
    styles = {
        'basic': EmbodiedMapping,
        'attribute': AttributeMapping,
        'flat': FlatMapping,
        'path': PathMapping,
        'frozen': FrozenMapping,
    }
    mapping_class = styles.get(style, EmbodiedMapping)
    return mapping_class(data)
