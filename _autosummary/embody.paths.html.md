# embody.paths

Path addressing for nested data structures.

This module provides utilities for working with paths in nested structures,
supporting:

- JSON Pointer (RFC 6901)
- Dot notation
- Tuple paths
- Path parsing and resolution

### Functions

| [`parse_path`](#embody.paths.parse_path)(path[, format])                  | Parse a path in various formats.   |
|----------------------------------------------------------------------------------------------|------------------------------------|
| [`resolve_path`](#embody.paths.resolve_path)(data, path[, default, format]) | Resolve a path against data.       |
| [`set_path`](#embody.paths.set_path)(data, path, value[, format, ...])  | Set a value at a path.             |

### Classes

| [`DotPath`](#embody.paths.DotPath)(path[, separator])   | Dot notation path handler (e.g., 'user.address.city').             |
|-------------------------------------------------------------------------------|--------------------------------------------------------------------|
| [`JSONPointer`](#embody.paths.JSONPointer)(pointer)         | JSON Pointer implementation (RFC 6901).                            |
| [`TuplePath`](#embody.paths.TuplePath)(parts)             | Tuple-based path (unambiguous, e.g., ('user', 'address', 'city')). |

### Exceptions

| [`InvalidPathError`](#embody.paths.InvalidPathError)   | Raised when a path is malformed or invalid.   |
|---------------------------------------------------------------------|-----------------------------------------------|

### *class* embody.paths.DotPath(path, separator='.')

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Dot notation path handler (e.g., ‘user.address.city’).

### Examples

```pycon
>>> data = {'user': {'address': {'city': 'NYC'}}}
>>> path = DotPath('user.address.city')
>>> path.resolve(data)
'NYC'
```

#### resolve(data, default=None)

Resolve the path against data.

* **Parameters:**
  * **data** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Data to resolve against
  * **default** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Default value if resolution fails
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  Resolved value or default

#### to_json_pointer()

Convert to a JSON Pointer.

* **Return type:**
  [`JSONPointer`](#embody.paths.JSONPointer)
* **Returns:**
  JSONPointer instance

### *exception* embody.paths.InvalidPathError

Bases: [`Exception`](https://docs.python.org/3/builtins/exceptions.html#Exception)

Raised when a path is malformed or invalid.

### *class* embody.paths.JSONPointer(pointer)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

JSON Pointer implementation (RFC 6901).

JSON Pointer defines a string syntax for identifying a specific value
within a JSON document. Example: /foo/bar/0 refers to the first element
of the ‘bar’ array in the ‘foo’ object.

### Examples

```pycon
>>> data = {'foo': {'bar': [1, 2, 3]}}
>>> ptr = JSONPointer('/foo/bar/0')
>>> ptr.resolve(data)
1
```

```pycon
>>> data = {'user': {'name': 'Alice', 'age': 30}}
>>> JSONPointer('/user/name').resolve(data)
'Alice'
```

#### *classmethod* from_parts(parts)

Create a JSON Pointer from path components.

* **Parameters:**
  **parts** ([`List`](https://docs.python.org/3/library/typing.html#typing.List)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]) – List of path components
* **Return type:**
  [`JSONPointer`](#embody.paths.JSONPointer)
* **Returns:**
  JSONPointer instance

### Examples

```pycon
>>> ptr = JSONPointer.from_parts(['foo', 'bar', '0'])
>>> ptr.pointer
'/foo/bar/0'
```

#### resolve(data, default=None)

Resolve the pointer against data.

* **Parameters:**
  * **data** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Data to resolve against
  * **default** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Default value if resolution fails
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  Resolved value or default

### Examples

```pycon
>>> data = {'a': {'b': [1, 2, 3]}}
>>> JSONPointer('/a/b/1').resolve(data)
2
>>> JSONPointer('/a/x').resolve(data, default='not found')
'not found'
```

#### set(data, value, create_intermediate=False)

Set a value at the pointer location.

* **Parameters:**
  * **data** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Data to modify (in place)
  * **value** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Value to set
  * **create_intermediate** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, create intermediate structures
* **Raises:**
  [**InvalidPathError**](#embody.paths.InvalidPathError) – If path cannot be set

### Examples

```pycon
>>> data = {'a': {'b': {}}}
>>> JSONPointer('/a/b/c').set(data, 42)
>>> data
{'a': {'b': {'c': 42}}}
```

### *class* embody.paths.TuplePath(parts)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Tuple-based path (unambiguous, e.g., (‘user’, ‘address’, ‘city’)).

### Examples

```pycon
>>> data = {'user': {'address': {'city': 'NYC'}}}
>>> path = TuplePath(('user', 'address', 'city'))
>>> path.resolve(data)
'NYC'
```

#### resolve(data, default=None)

Resolve the path against data.

* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)

#### to_json_pointer()

Convert to a JSON Pointer.

* **Return type:**
  [`JSONPointer`](#embody.paths.JSONPointer)

### embody.paths.parse_path(path, format='auto')

Parse a path in various formats.

* **Parameters:**
  * **path** ([`Union`](https://docs.python.org/3/library/typing.html#typing.Union)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Tuple`](https://docs.python.org/3/library/typing.html#typing.Tuple), [`List`](https://docs.python.org/3/library/typing.html#typing.List)]) – Path in any supported format
  * **format** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Format hint (‘auto’, ‘json_pointer’, ‘dot’, ‘tuple’)
* **Return type:**
  [`Union`](https://docs.python.org/3/library/typing.html#typing.Union)[[`JSONPointer`](#embody.paths.JSONPointer), [`DotPath`](#embody.paths.DotPath), [`TuplePath`](#embody.paths.TuplePath)]
* **Returns:**
  Path object

### Examples

```pycon
>>> parse_path('/user/name')
<embody.paths.JSONPointer object at ...>
```

```pycon
>>> parse_path('user.name')
<embody.paths.DotPath object at ...>
```

```pycon
>>> parse_path(('user', 'name'))
<embody.paths.TuplePath object at ...>
```

### embody.paths.resolve_path(data, path, default=None, format='auto')

Resolve a path against data.

* **Parameters:**
  * **data** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Data to resolve against
  * **path** ([`Union`](https://docs.python.org/3/library/typing.html#typing.Union)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Tuple`](https://docs.python.org/3/library/typing.html#typing.Tuple), [`List`](https://docs.python.org/3/library/typing.html#typing.List)]) – Path in any supported format
  * **default** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Default value if resolution fails
  * **format** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Format hint
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  Resolved value or default

### Examples

```pycon
>>> data = {'user': {'name': 'Alice', 'age': 30}}
>>> resolve_path(data, '/user/name')
'Alice'
>>> resolve_path(data, 'user.age')
30
>>> resolve_path(data, ('user', 'name'))
'Alice'
```

### embody.paths.set_path(data, path, value, format='auto', create_intermediate=True)

Set a value at a path.

* **Parameters:**
  * **data** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Data to modify
  * **path** ([`Union`](https://docs.python.org/3/library/typing.html#typing.Union)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Tuple`](https://docs.python.org/3/library/typing.html#typing.Tuple), [`List`](https://docs.python.org/3/library/typing.html#typing.List)]) – Path in any supported format
  * **value** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Value to set
  * **format** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Format hint
  * **create_intermediate** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, create intermediate structures

### Examples

```pycon
>>> data = {}
>>> set_path(data, '/user/name', 'Alice')
>>> data
{'user': {'name': 'Alice'}}
```
