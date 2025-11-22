"""Path addressing for nested data structures.

This module provides utilities for working with paths in nested structures,
supporting:
- JSON Pointer (RFC 6901)
- Dot notation
- Tuple paths
- Path parsing and resolution
"""

from typing import Any, Union, Tuple, List
from urllib.parse import unquote


class InvalidPathError(Exception):
    """Raised when a path is malformed or invalid."""
    pass


class JSONPointer:
    """JSON Pointer implementation (RFC 6901).

    JSON Pointer defines a string syntax for identifying a specific value
    within a JSON document. Example: /foo/bar/0 refers to the first element
    of the 'bar' array in the 'foo' object.

    Examples:
        >>> data = {'foo': {'bar': [1, 2, 3]}}
        >>> ptr = JSONPointer('/foo/bar/0')
        >>> ptr.resolve(data)
        1

        >>> data = {'user': {'name': 'Alice', 'age': 30}}
        >>> JSONPointer('/user/name').resolve(data)
        'Alice'
    """

    def __init__(self, pointer: str):
        """Initialize a JSON Pointer.

        Args:
            pointer: JSON Pointer string (must start with /)

        Raises:
            InvalidPathError: If pointer doesn't start with /
        """
        if not pointer.startswith('/') and pointer != '':
            raise InvalidPathError(
                f"JSON Pointer must start with '/': {pointer}"
            )
        self.pointer = pointer
        self.parts = self._parse(pointer)

    @staticmethod
    def _parse(pointer: str) -> List[str]:
        """Parse a JSON Pointer string into path components.

        Args:
            pointer: JSON Pointer string

        Returns:
            List of path components

        Examples:
            >>> JSONPointer._parse('/foo/bar')
            ['foo', 'bar']
            >>> JSONPointer._parse('')
            []
        """
        if pointer == '':
            return []

        # Remove leading /
        parts = pointer[1:].split('/')

        # Unescape according to RFC 6901
        # ~1 becomes /, ~0 becomes ~
        decoded_parts = []
        for part in parts:
            # URL decode first (in case of %XX encoding)
            part = unquote(part)
            # Then unescape ~1 and ~0
            part = part.replace('~1', '/').replace('~0', '~')
            decoded_parts.append(part)

        return decoded_parts

    @staticmethod
    def _escape(part: str) -> str:
        """Escape a path component for JSON Pointer.

        Args:
            part: Path component to escape

        Returns:
            Escaped component
        """
        # Must escape ~ first, then /
        return part.replace('~', '~0').replace('/', '~1')

    @classmethod
    def from_parts(cls, parts: List[str]) -> 'JSONPointer':
        """Create a JSON Pointer from path components.

        Args:
            parts: List of path components

        Returns:
            JSONPointer instance

        Examples:
            >>> ptr = JSONPointer.from_parts(['foo', 'bar', '0'])
            >>> ptr.pointer
            '/foo/bar/0'
        """
        if not parts:
            return cls('')
        escaped_parts = [cls._escape(part) for part in parts]
        pointer = '/' + '/'.join(escaped_parts)
        return cls(pointer)

    def resolve(self, data: Any, default: Any = None) -> Any:
        """Resolve the pointer against data.

        Args:
            data: Data to resolve against
            default: Default value if resolution fails

        Returns:
            Resolved value or default

        Examples:
            >>> data = {'a': {'b': [1, 2, 3]}}
            >>> JSONPointer('/a/b/1').resolve(data)
            2
            >>> JSONPointer('/a/x').resolve(data, default='not found')
            'not found'
        """
        current = data

        for part in self.parts:
            try:
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, (list, tuple)):
                    # Array index
                    if part == '-':
                        # "-" refers to position after last element (for append)
                        return default
                    try:
                        index = int(part)
                        current = current[index]
                    except (ValueError, IndexError):
                        return default
                else:
                    return default
            except (KeyError, TypeError):
                return default

        return current

    def set(self, data: Any, value: Any, create_intermediate: bool = False):
        """Set a value at the pointer location.

        Args:
            data: Data to modify (in place)
            value: Value to set
            create_intermediate: If True, create intermediate structures

        Raises:
            InvalidPathError: If path cannot be set

        Examples:
            >>> data = {'a': {'b': {}}}
            >>> JSONPointer('/a/b/c').set(data, 42)
            >>> data
            {'a': {'b': {'c': 42}}}
        """
        if not self.parts:
            raise InvalidPathError("Cannot set at root")

        current = data
        for i, part in enumerate(self.parts[:-1]):
            if isinstance(current, dict):
                if part not in current:
                    if create_intermediate:
                        # Determine if next level should be list or dict
                        next_part = self.parts[i + 1]
                        try:
                            int(next_part)
                            current[part] = []
                        except ValueError:
                            current[part] = {}
                    else:
                        raise InvalidPathError(f"Path not found: {part}")
                current = current[part]
            elif isinstance(current, list):
                try:
                    index = int(part)
                    current = current[index]
                except (ValueError, IndexError):
                    raise InvalidPathError(f"Invalid array index: {part}")
            else:
                raise InvalidPathError(f"Cannot traverse through {type(current)}")

        # Set the final value
        final_part = self.parts[-1]
        if isinstance(current, dict):
            current[final_part] = value
        elif isinstance(current, list):
            try:
                index = int(final_part)
                if index == len(current):
                    # Append
                    current.append(value)
                else:
                    current[index] = value
            except ValueError:
                raise InvalidPathError(f"Invalid array index: {final_part}")
        else:
            raise InvalidPathError(f"Cannot set on {type(current)}")


class DotPath:
    """Dot notation path handler (e.g., 'user.address.city').

    Examples:
        >>> data = {'user': {'address': {'city': 'NYC'}}}
        >>> path = DotPath('user.address.city')
        >>> path.resolve(data)
        'NYC'
    """

    def __init__(self, path: str, separator: str = '.'):
        """Initialize a DotPath.

        Args:
            path: Dot-separated path string
            separator: Path separator (default: '.')
        """
        self.path = path
        self.separator = separator
        self.parts = path.split(separator) if path else []

    def resolve(self, data: Any, default: Any = None) -> Any:
        """Resolve the path against data.

        Args:
            data: Data to resolve against
            default: Default value if resolution fails

        Returns:
            Resolved value or default
        """
        current = data

        for part in self.parts:
            try:
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, (list, tuple)):
                    # Try to parse as integer index
                    try:
                        index = int(part)
                        current = current[index]
                    except (ValueError, IndexError):
                        return default
                else:
                    return default
            except (KeyError, TypeError):
                return default

        return current

    def to_json_pointer(self) -> JSONPointer:
        """Convert to a JSON Pointer.

        Returns:
            JSONPointer instance
        """
        return JSONPointer.from_parts(self.parts)


class TuplePath:
    """Tuple-based path (unambiguous, e.g., ('user', 'address', 'city')).

    Examples:
        >>> data = {'user': {'address': {'city': 'NYC'}}}
        >>> path = TuplePath(('user', 'address', 'city'))
        >>> path.resolve(data)
        'NYC'
    """

    def __init__(self, parts: Tuple):
        """Initialize a TuplePath.

        Args:
            parts: Tuple of path components
        """
        self.parts = parts

    def resolve(self, data: Any, default: Any = None) -> Any:
        """Resolve the path against data."""
        current = data

        for part in self.parts:
            try:
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, (list, tuple)):
                    # part should be an integer
                    current = current[part]
                else:
                    return default
            except (KeyError, IndexError, TypeError):
                return default

        return current

    def to_json_pointer(self) -> JSONPointer:
        """Convert to a JSON Pointer."""
        return JSONPointer.from_parts([str(p) for p in self.parts])


def parse_path(
    path: Union[str, Tuple, List],
    format: str = 'auto'
) -> Union[JSONPointer, DotPath, TuplePath]:
    """Parse a path in various formats.

    Args:
        path: Path in any supported format
        format: Format hint ('auto', 'json_pointer', 'dot', 'tuple')

    Returns:
        Path object

    Examples:
        >>> parse_path('/user/name')
        <embody.paths.JSONPointer object at ...>

        >>> parse_path('user.name')
        <embody.paths.DotPath object at ...>

        >>> parse_path(('user', 'name'))
        <embody.paths.TuplePath object at ...>
    """
    if format == 'auto':
        if isinstance(path, (tuple, list)):
            return TuplePath(tuple(path))
        elif isinstance(path, str):
            if path.startswith('/'):
                return JSONPointer(path)
            else:
                return DotPath(path)
        else:
            raise InvalidPathError(f"Cannot parse path: {path}")
    elif format == 'json_pointer':
        if isinstance(path, str):
            return JSONPointer(path)
        else:
            raise InvalidPathError("JSON Pointer must be a string")
    elif format == 'dot':
        if isinstance(path, str):
            return DotPath(path)
        else:
            raise InvalidPathError("Dot path must be a string")
    elif format == 'tuple':
        if isinstance(path, (tuple, list)):
            return TuplePath(tuple(path))
        else:
            raise InvalidPathError("Tuple path must be a tuple or list")
    else:
        raise InvalidPathError(f"Unknown path format: {format}")


def resolve_path(
    data: Any,
    path: Union[str, Tuple, List],
    default: Any = None,
    format: str = 'auto'
) -> Any:
    """Resolve a path against data.

    Args:
        data: Data to resolve against
        path: Path in any supported format
        default: Default value if resolution fails
        format: Format hint

    Returns:
        Resolved value or default

    Examples:
        >>> data = {'user': {'name': 'Alice', 'age': 30}}
        >>> resolve_path(data, '/user/name')
        'Alice'
        >>> resolve_path(data, 'user.age')
        30
        >>> resolve_path(data, ('user', 'name'))
        'Alice'
    """
    path_obj = parse_path(path, format)
    return path_obj.resolve(data, default)


def set_path(
    data: Any,
    path: Union[str, Tuple, List],
    value: Any,
    format: str = 'auto',
    create_intermediate: bool = True
):
    """Set a value at a path.

    Args:
        data: Data to modify
        path: Path in any supported format
        value: Value to set
        format: Format hint
        create_intermediate: If True, create intermediate structures

    Examples:
        >>> data = {}
        >>> set_path(data, '/user/name', 'Alice')
        >>> data
        {'user': {'name': 'Alice'}}
    """
    path_obj = parse_path(path, format)

    if isinstance(path_obj, JSONPointer):
        path_obj.set(data, value, create_intermediate)
    else:
        # Convert to JSON Pointer for setting
        json_pointer = path_obj.to_json_pointer()
        json_pointer.set(data, value, create_intermediate)
