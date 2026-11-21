# embody.mappings

Mapping interface wrappers for embodied objects.

This module provides wrappers that convert nested structures into
uniform Mapping interfaces, supporting:

- Lazy evaluation
- Attribute access (Box pattern)
- Flat path-based access
- Immutability (frozen objects)

### Functions

| [`as_mapping`](#embody.mappings.as_mapping)(data[, style])   | Convert data to a Mapping with the specified style.   |
|------------------------------------------------------------------------------|-------------------------------------------------------|

### Classes

| [`AttributeMapping`](#embody.mappings.AttributeMapping)(data)                          | Mapping that allows attribute access (Box pattern).                  |
|--------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| [`EmbodiedMapping`](#embody.mappings.EmbodiedMapping)(data)                           | Read-only Mapping wrapper for embodied objects with lazy evaluation. |
| [`FlatMapping`](#embody.mappings.FlatMapping)(data[, separator])                  | Mapping with flattened nested structure for path-based access.       |
| [`FrozenMapping`](#embody.mappings.FrozenMapping)(data)                             | Immutable Mapping wrapper.                                           |
| [`LazyEmbodiedMapping`](#embody.mappings.LazyEmbodiedMapping)(template, params, embodier) | Lazy Mapping that embodies values on access.                         |
| [`MutableEmbodiedMapping`](#embody.mappings.MutableEmbodiedMapping)(data)                    | Mutable Mapping wrapper for embodied objects.                        |
| [`PathMapping`](#embody.mappings.PathMapping)(data[, separator])                  | Mapping supporting multiple path access styles.                      |

### *class* embody.mappings.AttributeMapping(data)

Bases: [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)

Mapping that allows attribute access (Box pattern).

Allows accessing dictionary keys as attributes for more fluid syntax.

### Examples

```pycon
>>> data = {'user': {'name': 'Alice', 'age': 30}}
>>> attr_map = AttributeMapping(data)
>>> attr_map.user.name
'Alice'
>>> attr_map.user.age
30
>>> attr_map['user']['name']  # Still works as dict
'Alice'
```

#### to_dict()

Convert back to plain dictionary.

* **Return type:**
  [`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)
* **Returns:**
  Plain dictionary

### *class* embody.mappings.EmbodiedMapping(data)

Bases: [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)

Read-only Mapping wrapper for embodied objects with lazy evaluation.

This wrapper provides a Mapping interface around an embodied object,
with support for lazy embodiment (values materialized on access).

### Examples

```pycon
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
```

### *class* embody.mappings.FlatMapping(data, separator='.')

Bases: [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)

Mapping with flattened nested structure for path-based access.

Allows accessing nested values using dot notation as single keys.

### Examples

```pycon
>>> nested = {'user': {'name': 'Alice', 'age': 30}}
>>> flat = FlatMapping(nested)
>>> flat['user.name']
'Alice'
>>> flat['user.age']
30
>>> list(flat.keys())
['user.name', 'user.age']
```

#### get_nested(\*path_parts)

Get a value by path components.

* **Parameters:**
  **\*path_parts** – Path components
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  Value at path

### Examples

```pycon
>>> nested = {'a': {'b': {'c': 42}}}
>>> flat = FlatMapping(nested)
>>> flat.get_nested('a', 'b', 'c')
42
```

### *class* embody.mappings.FrozenMapping(data)

Bases: [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)

Immutable Mapping wrapper.

Provides a frozen (immutable) view of a dictionary.

### Examples

```pycon
>>> data = {'a': 1, 'b': 2}
>>> frozen = FrozenMapping(data)
>>> frozen['a']
1
>>> # Modifications to original don't affect frozen (deep copy)
>>> data['c'] = 3
>>> 'c' in frozen
False
```

### *class* embody.mappings.LazyEmbodiedMapping(template, params, embodier)

Bases: [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)

Lazy Mapping that embodies values on access.

This is useful for large templates where you only need to access
a subset of values. Values are embodied on-demand and cached.

### Examples

```pycon
>>> from embody import Embodier
>>> template = {'a': '${x}', 'b': '${y}', 'c': '${z}'}
>>> params = {'x': 1, 'y': 2, 'z': 3}
>>> embodier = Embodier(template)
>>> lazy = LazyEmbodiedMapping(template, params, embodier)
>>> lazy['a']  # Only 'a' is embodied
1
```

### *class* embody.mappings.MutableEmbodiedMapping(data)

Bases: [`MutableMapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping)

Mutable Mapping wrapper for embodied objects.

Provides full MutableMapping interface for modifying embodied results.

### Examples

```pycon
>>> data = {'a': 1, 'b': 2}
>>> mutable = MutableEmbodiedMapping(data)
>>> mutable['c'] = 3
>>> mutable['a'] = 10
>>> del mutable['b']
>>> dict(mutable)
{'a': 10, 'c': 3}
```

#### freeze()

Convert to an immutable FrozenMapping.

* **Return type:**
  [`FrozenMapping`](#embody.mappings.FrozenMapping)
* **Returns:**
  Frozen version of this mapping

### *class* embody.mappings.PathMapping(data, separator='.')

Bases: [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)

Mapping supporting multiple path access styles.

Supports:

- Regular dict access: mapping[‘key’]
- Dot notation: mapping[‘a.b.c’]
- Tuple paths: mapping[(‘a’, ‘b’, ‘c’)]
- JSON Pointer: mapping[‘/a/b/c’]

### Examples

```pycon
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
```

### embody.mappings.as_mapping(data, style='basic')

Convert data to a Mapping with the specified style.

* **Parameters:**
  * **data** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Data to wrap
  * **style** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Style of mapping (‘basic’, ‘attribute’, ‘flat’, ‘path’, ‘frozen’)
* **Return type:**
  [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)
* **Returns:**
  Mapping instance

### Examples

```pycon
>>> data = {'user': {'name': 'Alice'}}
>>> m = as_mapping(data, 'attribute')
>>> m.user.name
'Alice'
```

```pycon
>>> m = as_mapping(data, 'flat')
>>> m['user.name']
'Alice'
```
