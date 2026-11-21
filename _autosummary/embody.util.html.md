# embody.util

Utility functions for embody: flattening, unflattening, and cycle detection.

This module provides helper functions for working with nested data structures,
including path-based operations and cycle detection for safe traversal.

### Functions

| [`count_template_markers`](#embody.util.count_template_markers)(obj[, syntax])           | Count the number of template markers in a nested structure.                |
|--------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| [`detect_cycle`](#embody.util.detect_cycle)(obj[, visited, path])              | Detect cycles in a nested data structure.                                  |
| [`flatten_dict`](#embody.util.flatten_dict)(nested_dict[, separator, ...])     | Flatten a nested dictionary into a single-level dictionary with path keys. |
| [`flatten_to_tuples`](#embody.util.flatten_to_tuples)(obj[, parent_path])           | Flatten a nested structure using tuple paths (unambiguous).                |
| [`get_by_path`](#embody.util.get_by_path)(obj, path[, separator, default])    | Get a value from a nested structure by path.                               |
| [`max_depth`](#embody.util.max_depth)(obj[, current_depth])                 | Calculate the maximum depth of a nested structure.                         |
| [`set_by_path`](#embody.util.set_by_path)(obj, path, value[, separator, ...]) | Set a value in a nested structure by path (modifies in place).             |
| [`unflatten_dict`](#embody.util.unflatten_dict)(flat_dict[, separator])          | Unflatten a dictionary with path keys into a nested structure.             |
| [`unflatten_from_tuples`](#embody.util.unflatten_from_tuples)(flat_dict)                | Unflatten a dictionary with tuple paths into a nested structure.           |

### Exceptions

| [`CycleError`](#embody.util.CycleError)        | Raised when a circular reference is detected in a data structure.   |
|--------------------------------------------------------------------|---------------------------------------------------------------------|
| [`PathNotFoundError`](#embody.util.PathNotFoundError) | Raised when a path doesn't exist in a data structure.               |

### *exception* embody.util.CycleError

Bases: [`Exception`](https://docs.python.org/3/builtins/exceptions.html#Exception)

Raised when a circular reference is detected in a data structure.

### *exception* embody.util.PathNotFoundError

Bases: [`Exception`](https://docs.python.org/3/builtins/exceptions.html#Exception)

Raised when a path doesn’t exist in a data structure.

### embody.util.count_template_markers(obj, syntax='dollar_brace')

Count the number of template markers in a nested structure.

* **Parameters:**
  * **obj** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Object to count markers in
  * **syntax** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Template syntax to look for
* **Return type:**
  [`int`](https://docs.python.org/3/builtins/functions.html#int)
* **Returns:**
  Number of template markers found

### Examples

```pycon
>>> count_template_markers({'a': '${x}', 'b': '${y}'})
2
>>> count_template_markers(['${a}', 'literal', '${b} and ${c}'])
3
```

### embody.util.detect_cycle(obj, visited=None, path=None)

Detect cycles in a nested data structure.

* **Parameters:**
  * **obj** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – The object to check for cycles
  * **visited** ([`Set`](https://docs.python.org/3/library/typing.html#typing.Set)[[`int`](https://docs.python.org/3/builtins/functions.html#int)]) – Set of object IDs already visited
  * **path** ([`List`](https://docs.python.org/3/library/typing.html#typing.List)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]) – Current path in the structure (for error reporting)
* **Raises:**
  [**CycleError**](#embody.util.CycleError) – If a cycle is detected
* **Return type:**
  [`None`](https://docs.python.org/3/builtins/constants.html#None)

### Examples

```pycon
>>> d = {'a': 1, 'b': [2, 3]}
>>> detect_cycle(d)  # No cycle, returns None
```

```pycon
>>> circular = {'a': 1}
>>> circular['self'] = circular
>>> try:
...     detect_cycle(circular)
... except CycleError as e:
...     print("Cycle detected")
Cycle detected
```

### embody.util.flatten_dict(nested_dict, separator='.', parent_key='')

Flatten a nested dictionary into a single-level dictionary with path keys.

* **Parameters:**
  * **nested_dict** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Nested dictionary to flatten
  * **separator** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – String to use for separating path components
  * **parent_key** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Key of the parent (used in recursion)
* **Return type:**
  [`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]
* **Returns:**
  Flattened dictionary with path keys

### Examples

```pycon
>>> d = {'a': {'b': {'c': 1}}, 'd': 2}
>>> flatten_dict(d)
{'a.b.c': 1, 'd': 2}
```

```pycon
>>> d = {'user': {'name': 'Alice', 'age': 30}}
>>> flatten_dict(d)
{'user.name': 'Alice', 'user.age': 30}
```

```pycon
>>> d = {'items': [1, 2, 3]}
>>> flatten_dict(d)
{'items.0': 1, 'items.1': 2, 'items.2': 3}
```

### embody.util.flatten_to_tuples(obj, parent_path=())

Flatten a nested structure using tuple paths (unambiguous).

This avoids the ambiguity of string separators. A tuple path like
(‘a’, ‘b’, 0) is unambiguous, while ‘a.b.0’ could mean multiple things
if keys contain dots.

* **Parameters:**
  * **obj** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Object to flatten
  * **parent_path** ([`Tuple`](https://docs.python.org/3/library/typing.html#typing.Tuple)) – Current path as tuple
* **Return type:**
  [`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`Tuple`](https://docs.python.org/3/library/typing.html#typing.Tuple), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]
* **Returns:**
  Dictionary mapping tuple paths to values

### Examples

```pycon
>>> d = {'a': {'b': [1, 2]}}
>>> flatten_to_tuples(d)
{('a', 'b', 0): 1, ('a', 'b', 1): 2}
```

### embody.util.get_by_path(obj, path, separator='.', default=None)

Get a value from a nested structure by path.

* **Parameters:**
  * **obj** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Nested structure
  * **path** ([`Union`](https://docs.python.org/3/library/typing.html#typing.Union)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Tuple`](https://docs.python.org/3/library/typing.html#typing.Tuple)]) – Path as string or tuple
  * **separator** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Separator for string paths
  * **default** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Default value if path not found
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  Value at the path, or default if not found

### Examples

```pycon
>>> d = {'a': {'b': {'c': 42}}}
>>> get_by_path(d, 'a.b.c')
42
>>> get_by_path(d, ('a', 'b', 'c'))
42
>>> get_by_path(d, 'a.b.x', default='not found')
'not found'
```

### embody.util.max_depth(obj, current_depth=0)

Calculate the maximum depth of a nested structure.

* **Parameters:**
  * **obj** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Object to measure
  * **current_depth** ([`int`](https://docs.python.org/3/builtins/functions.html#int)) – Current depth (used in recursion)
* **Return type:**
  [`int`](https://docs.python.org/3/builtins/functions.html#int)
* **Returns:**
  Maximum depth

### Examples

```pycon
>>> max_depth({'a': 1})
1
>>> max_depth({'a': {'b': {'c': 1}}})
3
>>> max_depth([1, [2, [3, 4]]])
3
```

### embody.util.set_by_path(obj, path, value, separator='.', create_intermediate=True)

Set a value in a nested structure by path (modifies in place).

* **Parameters:**
  * **obj** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)) – Nested structure to modify
  * **path** ([`Union`](https://docs.python.org/3/library/typing.html#typing.Union)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Tuple`](https://docs.python.org/3/library/typing.html#typing.Tuple)]) – Path as string or tuple
  * **value** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Value to set
  * **separator** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Separator for string paths
  * **create_intermediate** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, create intermediate dicts/lists as needed
* **Return type:**
  [`None`](https://docs.python.org/3/builtins/constants.html#None)

### Examples

```pycon
>>> d = {}
>>> set_by_path(d, 'a.b.c', 42)
>>> d
{'a': {'b': {'c': 42}}}
```

### embody.util.unflatten_dict(flat_dict, separator='.')

Unflatten a dictionary with path keys into a nested structure.

* **Parameters:**
  * **flat_dict** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Flattened dictionary with path keys
  * **separator** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – String used for separating path components
* **Return type:**
  [`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]
* **Returns:**
  Nested dictionary structure

### Examples

```pycon
>>> flat = {'a.b.c': 1, 'd': 2}
>>> unflatten_dict(flat)
{'a': {'b': {'c': 1}}, 'd': 2}
```

```pycon
>>> flat = {'items.0': 'a', 'items.1': 'b'}
>>> unflatten_dict(flat)
{'items': ['a', 'b']}
```

### embody.util.unflatten_from_tuples(flat_dict)

Unflatten a dictionary with tuple paths into a nested structure.

* **Parameters:**
  **flat_dict** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`Tuple`](https://docs.python.org/3/library/typing.html#typing.Tuple), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Dictionary with tuple paths as keys
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  Nested structure (dict or list)

### Examples

```pycon
>>> flat = {('a', 'b', 0): 1, ('a', 'b', 1): 2}
>>> unflatten_from_tuples(flat)
{'a': {'b': [1, 2]}}
```
