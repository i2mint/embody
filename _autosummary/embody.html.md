# embody

Generate templated objects with advanced structural embodiment features.

This package provides powerful tools for template-based object generation,
supporting:

- Multiple syntax styles (${var}, {var}, [[var]])
- Type-preserving substitution
- Multiple traversal strategies (recursive, compiled, iterative)
- Cycle detection
- Mapping interfaces with various access patterns
- Path-based addressing (JSON Pointer, dot notation, tuple paths)

Basic usage:

```pycon
>>> from embody import embody
>>> template = {'name': '${name}', 'age': '${age}'}
>>> result = embody(template, {'name': 'Alice', 'age': 30})
>>> result
{'name': 'Alice', 'age': 30}
```

Advanced usage:

```pycon
>>> from embody import Embodier, Context
>>> template = {'greeting': 'Hello ${name}', 'count': '${num}'}
>>> embodier = Embodier(template, syntax='dollar_brace', strict=True)
>>> embodier({'name': 'Alice', 'num': 42})
{'greeting': 'Hello Alice', 'count': 42}
```

### Functions

| [`embody`](#embody.embody)(template[, params])                      | Convenience function for template embodiment.                              |
|--------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| [`get_engine`](#embody.get_engine)([strategy])                          | Get an embodiment engine by name.                                          |
| [`substitute`](#embody.substitute)(template, params[, syntax, strict])  | Perform type-preserving substitution on a template value.                  |
| [`extract_template_vars`](#embody.extract_template_vars)(template[, syntax])       | Extract all template variable names from a string.                         |
| [`is_exact_match`](#embody.is_exact_match)(template[, syntax])              | Check if template is exactly one variable placeholder (no other text).     |
| [`flatten_dict`](#embody.flatten_dict)(nested_dict[, separator, ...])     | Flatten a nested dictionary into a single-level dictionary with path keys. |
| [`unflatten_dict`](#embody.unflatten_dict)(flat_dict[, separator])          | Unflatten a dictionary with path keys into a nested structure.             |
| [`flatten_to_tuples`](#embody.flatten_to_tuples)(obj[, parent_path])           | Flatten a nested structure using tuple paths (unambiguous).                |
| [`unflatten_from_tuples`](#embody.unflatten_from_tuples)(flat_dict)                | Unflatten a dictionary with tuple paths into a nested structure.           |
| [`detect_cycle`](#embody.detect_cycle)(obj[, visited, path])              | Detect cycles in a nested data structure.                                  |
| [`get_by_path`](#embody.get_by_path)(obj, path[, separator, default])    | Get a value from a nested structure by path.                               |
| [`set_by_path`](#embody.set_by_path)(obj, path, value[, separator, ...]) | Set a value in a nested structure by path (modifies in place).             |
| [`max_depth`](#embody.max_depth)(obj[, current_depth])                 | Calculate the maximum depth of a nested structure.                         |
| [`count_template_markers`](#embody.count_template_markers)(obj[, syntax])           | Count the number of template markers in a nested structure.                |
| [`as_mapping`](#embody.as_mapping)(data[, style])                       | Convert data to a Mapping with the specified style.                        |
| [`parse_path`](#embody.parse_path)(path[, format])                      | Parse a path in various formats.                                           |
| [`resolve_path`](#embody.resolve_path)(data, path[, default, format])     | Resolve a path against data.                                               |
| [`set_path`](#embody.set_path)(data, path, value[, format, ...])      | Set a value at a path.                                                     |

### Classes

| [`Embodier`](#embody.Embodier)(template[, strategy, syntax, ...])       | Main class for embodying templates with parameters.                  |
|----------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| [`Context`](#embody.Context)([params, parent, resolvers, auto_call])   | Parameter store for template embodiment with support for resolvers.  |
| [`TemplateWrapper`](#embody.TemplateWrapper)(template[, syntax, check_cycles]) | Wrapper for template data with introspection capabilities.           |
| `Templater`()                                                                                      |                                                                      |
| [`RecursiveVisitorEngine`](#embody.RecursiveVisitorEngine)([syntax, strict, ...])     | Dynamic traversal strategy using the Visitor pattern.                |
| [`CompiledPathEngine`](#embody.CompiledPathEngine)(\*args, \*\*kwargs)            | Pre-compiled path-based traversal strategy.                          |
| [`IterativeStackEngine`](#embody.IterativeStackEngine)([syntax, strict, ...])       | Iterative stack-based traversal strategy.                            |
| [`SubstitutionSyntax`](#embody.SubstitutionSyntax)()                              | Defines the syntax patterns for template variable substitution.      |
| [`EmbodiedMapping`](#embody.EmbodiedMapping)(data)                             | Read-only Mapping wrapper for embodied objects with lazy evaluation. |
| [`LazyEmbodiedMapping`](#embody.LazyEmbodiedMapping)(template, params, embodier)   | Lazy Mapping that embodies values on access.                         |
| [`FlatMapping`](#embody.FlatMapping)(data[, separator])                    | Mapping with flattened nested structure for path-based access.       |
| [`AttributeMapping`](#embody.AttributeMapping)(data)                            | Mapping that allows attribute access (Box pattern).                  |
| [`FrozenMapping`](#embody.FrozenMapping)(data)                               | Immutable Mapping wrapper.                                           |
| [`MutableEmbodiedMapping`](#embody.MutableEmbodiedMapping)(data)                      | Mutable Mapping wrapper for embodied objects.                        |
| [`PathMapping`](#embody.PathMapping)(data[, separator])                    | Mapping supporting multiple path access styles.                      |
| [`JSONPointer`](#embody.JSONPointer)(pointer)                              | JSON Pointer implementation (RFC 6901).                              |
| [`DotPath`](#embody.DotPath)(path[, separator])                        | Dot notation path handler (e.g., 'user.address.city').               |
| [`TuplePath`](#embody.TuplePath)(parts)                                  | Tuple-based path (unambiguous, e.g., ('user', 'address', 'city')).   |

### Exceptions

| [`MissingParameterError`](#embody.MissingParameterError)   | Raised when a required template parameter is missing.             |
|--------------------------------------------------------------------------|-------------------------------------------------------------------|
| [`KeyCollisionError`](#embody.KeyCollisionError)       | Raised when dynamic keys resolve to the same value.               |
| [`CycleError`](#embody.CycleError)              | Raised when a circular reference is detected in a data structure. |
| [`PathNotFoundError`](#embody.PathNotFoundError)       | Raised when a path doesn't exist in a data structure.             |
| [`InvalidPathError`](#embody.InvalidPathError)        | Raised when a path is malformed or invalid.                       |

### *class* embody.AttributeMapping(data)

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

### *class* embody.CompiledPathEngine(\*args, \*\*kwargs)

Bases: [`BaseEmbodimentEngine`](embody.strategies.html.md#embody.strategies.BaseEmbodimentEngine)

Pre-compiled path-based traversal strategy.

This engine flattens the template into a path map, performs substitutions,
and then reconstructs the structure. It’s best for:

- Templates embodied repeatedly (e.g., API responses)
- Static templates with known structure
- Performance-critical paths

The compilation happens once, then embodiment is a linear scan.

### Examples

```pycon
>>> engine = CompiledPathEngine()
>>> template = {'a': {'b': '${x}'}, 'c': '${y}'}
>>> compiled = engine.compile(template)
>>> engine.embody_compiled(compiled, {'x': 1, 'y': 2})
{'a': {'b': 1}, 'c': 2}
```

#### compile(template)

Compile a template into a flat path map.

* **Parameters:**
  **template** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Template to compile
* **Return type:**
  [`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)
* **Returns:**
  Compiled template data

### Examples

```pycon
>>> engine = CompiledPathEngine()
>>> template = {'a': {'b': '${x}'}}
>>> compiled = engine.compile(template)
>>> compiled['flat']
{('a', 'b'): '${x}'}
```

#### embody(template, params)

Embody a template (compiles on first use, caches compilation).

* **Parameters:**
  * **template** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Template to embody
  * **params** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Parameters for substitution
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  Embodied object

#### embody_compiled(compiled, params)

Embody a pre-compiled template.

* **Parameters:**
  * **compiled** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)) – Compiled template from compile()
  * **params** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Parameters for substitution
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  Embodied object

### *class* embody.Context(params=None, parent=None, resolvers=None, auto_call=True)

Bases: [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)

Parameter store for template embodiment with support for resolvers.

The Context holds parameters for substitution and supports:

- Hierarchical scoping (global → local overrides)
- Resolver functions (lazy evaluation)
- Callable values that are invoked on access

### Examples

```pycon
>>> ctx = Context({'name': 'Alice', 'age': 30})
>>> ctx['name']
'Alice'
```

```pycon
>>> import datetime
>>> ctx = Context({'now': lambda: datetime.datetime.now()})
>>> ctx['now']
datetime.datetime(...)
```

```pycon
>>> ctx = Context({'base': 10}, parent={'base': 5, 'other': 20})
>>> ctx['base']  # Local overrides parent
10
>>> ctx['other']  # Falls back to parent
20
```

#### child(params=None)

Create a child context with this context as parent.

* **Parameters:**
  **params** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Parameters for the child context
* **Return type:**
  [`Context`](embody.base.html.md#embody.base.Context)
* **Returns:**
  New Context with this as parent

#### get(key, default=None)

Get a parameter with a default value.

* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)

#### register_resolver(name, func)

Register a named resolver function.

* **Parameters:**
  * **name** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of the resolver
  * **func** ([`Callable`](https://docs.python.org/3/library/typing.html#typing.Callable)) – Callable that returns the resolved value

### Examples

```pycon
>>> import os
>>> ctx = Context()
>>> ctx.register_resolver('env', lambda: os.environ.get('USER', 'unknown'))
```

#### to_dict()

Convert to a plain dictionary (resolving all values).

* **Return type:**
  [`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]
* **Returns:**
  Dictionary with all parameters resolved

#### update(params)

Create a new context with updated parameters.

* **Parameters:**
  **params** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Parameters to add/override
* **Return type:**
  [`Context`](embody.base.html.md#embody.base.Context)
* **Returns:**
  New Context with updated parameters

### *exception* embody.CycleError

Bases: [`Exception`](https://docs.python.org/3/builtins/exceptions.html#Exception)

Raised when a circular reference is detected in a data structure.

### *class* embody.DotPath(path, separator='.')

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
  [`JSONPointer`](embody.paths.html.md#embody.paths.JSONPointer)
* **Returns:**
  JSONPointer instance

### *class* embody.EmbodiedMapping(data)

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

### *class* embody.Embodier(template, strategy='auto', syntax='dollar_brace', strict=False, check_cycles=True, key_collision='error')

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Main class for embodying templates with parameters.

This is the primary API for the embody framework. It supports:

- Multiple traversal strategies (recursive, compiled, auto)
- Multiple syntax styles
- Strict or lenient parameter checking
- Cycle detection

### Examples

```pycon
>>> template = {'greeting': 'Hello ${name}', 'age': '${age}'}
>>> embodier = Embodier(template)
>>> embodier({'name': 'Alice', 'age': 30})
{'greeting': 'Hello Alice', 'age': 30}
```

```pycon
>>> template = {'count': '${num}'}
>>> embodier = Embodier(template)
>>> embodier({'num': 42})  # Type preserved
{'count': 42}
```

#### get_signature()

Get the list of parameters required by the template.

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]
* **Returns:**
  List of parameter names

### *class* embody.FlatMapping(data, separator='.')

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

### *class* embody.FrozenMapping(data)

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

### *exception* embody.InvalidPathError

Bases: [`Exception`](https://docs.python.org/3/builtins/exceptions.html#Exception)

Raised when a path is malformed or invalid.

### *class* embody.IterativeStackEngine(syntax='dollar_brace', strict=False, key_collision='error')

Bases: [`BaseEmbodimentEngine`](embody.strategies.html.md#embody.strategies.BaseEmbodimentEngine)

Iterative stack-based traversal strategy.

This engine uses an explicit stack instead of recursion, which is more
memory-efficient for very deep structures and avoids Python’s recursion limit.

Best for:

- Very deeply nested structures (>100 levels)
- When recursion depth is a concern

#### embody(template, params)

Embody using iterative stack-based traversal.

* **Parameters:**
  * **template** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Template to embody
  * **params** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Parameters for substitution
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  Embodied object

### *class* embody.JSONPointer(pointer)

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
  [`JSONPointer`](embody.paths.html.md#embody.paths.JSONPointer)
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
  [**InvalidPathError**](#embody.InvalidPathError) – If path cannot be set

### Examples

```pycon
>>> data = {'a': {'b': {}}}
>>> JSONPointer('/a/b/c').set(data, 42)
>>> data
{'a': {'b': {'c': 42}}}
```

### *exception* embody.KeyCollisionError

Bases: [`Exception`](https://docs.python.org/3/builtins/exceptions.html#Exception)

Raised when dynamic keys resolve to the same value.

### *class* embody.LazyEmbodiedMapping(template, params, embodier)

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

### *exception* embody.MissingParameterError

Bases: [`Exception`](https://docs.python.org/3/builtins/exceptions.html#Exception)

Raised when a required template parameter is missing.

### *class* embody.MutableEmbodiedMapping(data)

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
  [`FrozenMapping`](embody.mappings.html.md#embody.mappings.FrozenMapping)
* **Returns:**
  Frozen version of this mapping

### *class* embody.PathMapping(data, separator='.')

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

### *exception* embody.PathNotFoundError

Bases: [`Exception`](https://docs.python.org/3/builtins/exceptions.html#Exception)

Raised when a path doesn’t exist in a data structure.

### *class* embody.RecursiveVisitorEngine(syntax='dollar_brace', strict=False, key_collision='error')

Bases: [`BaseEmbodimentEngine`](embody.strategies.html.md#embody.strategies.BaseEmbodimentEngine)

Dynamic traversal strategy using the Visitor pattern.

This engine recursively walks the template structure at runtime,
visiting each node and performing substitutions. It’s best for:

- One-off templates
- Dynamic templates with conditional logic
- Templates where structure changes based on parameters

### Examples

```pycon
>>> engine = RecursiveVisitorEngine()
>>> template = {'greeting': 'Hello ${name}', 'count': '${num}'}
>>> engine.embody(template, {'name': 'Alice', 'num': 42})
{'greeting': 'Hello Alice', 'count': 42}
```

#### embody(template, params, visited=None)

Recursively embody a template.

* **Parameters:**
  * **template** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – Template to embody
  * **params** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Parameters for substitution
  * **visited** ([`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)[[`Set`](https://docs.python.org/3/library/typing.html#typing.Set)[[`int`](https://docs.python.org/3/builtins/functions.html#int)]]) – Set of visited object IDs (for cycle detection)
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  Embodied object
* **Raises:**
  [**CycleError**](#embody.CycleError) – If a circular reference is detected

### *class* embody.SubstitutionSyntax

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Defines the syntax patterns for template variable substitution.

#### *classmethod* get_pattern(syntax='dollar_brace')

Get the regex pattern for the specified syntax.

* **Parameters:**
  **syntax** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – One of ‘dollar_brace’, ‘brace’, ‘double_bracket’
* **Return type:**
  [`Pattern`](https://docs.python.org/3/library/typing.html#typing.Pattern)
* **Returns:**
  Compiled regex pattern

### Examples

```pycon
>>> pattern = SubstitutionSyntax.get_pattern('dollar_brace')
>>> pattern.findall('${name} is ${age}')
['name', 'age']
```

### *class* embody.TemplateWrapper(template, syntax='dollar_brace', check_cycles=True)

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Wrapper for template data with introspection capabilities.

This class wraps template data and provides methods to:

- Extract variable dependencies
- Detect cycles
- Parse and validate the template structure

### Examples

```pycon
>>> template = TemplateWrapper({'name': '${user}', 'age': '${years}'})
>>> sorted(template.get_dependencies())
['user', 'years']
```

#### get_dependencies()

Extract all template variables from the template.

* **Return type:**
  [`set`](https://docs.python.org/3/builtins/stdtypes.html#set)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]
* **Returns:**
  Set of variable names used in the template

#### validate_params(params)

Check which template dependencies are missing from params.

* **Parameters:**
  **params** ([`Union`](https://docs.python.org/3/library/typing.html#typing.Union)[[`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict), [`Context`](embody.base.html.md#embody.base.Context)]) – Parameters to check against
* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]
* **Returns:**
  List of missing parameter names

### *class* embody.TuplePath(parts)

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
  [`JSONPointer`](embody.paths.html.md#embody.paths.JSONPointer)

### embody.as_mapping(data, style='basic')

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

### embody.count_template_markers(obj, syntax='dollar_brace')

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

### embody.detect_cycle(obj, visited=None, path=None)

Detect cycles in a nested data structure.

* **Parameters:**
  * **obj** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – The object to check for cycles
  * **visited** ([`Set`](https://docs.python.org/3/library/typing.html#typing.Set)[[`int`](https://docs.python.org/3/builtins/functions.html#int)]) – Set of object IDs already visited
  * **path** ([`List`](https://docs.python.org/3/library/typing.html#typing.List)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]) – Current path in the structure (for error reporting)
* **Raises:**
  [**CycleError**](#embody.CycleError) – If a cycle is detected
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

### embody.embody(template, params=None, \*\*kwargs)

Convenience function for template embodiment.

This is the main entry point for simple embodiment use cases.

* **Parameters:**
  * **template** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – The template to embody
  * **params** ([`Union`](https://docs.python.org/3/library/typing.html#typing.Union)[[`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict), [`Context`](embody.base.html.md#embody.base.Context)]) – Parameters for substitution
  * **\*\*kwargs** – Additional parameters or config options
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  Embodied object

### Examples

```pycon
>>> embody({'name': '${name}'}, {'name': 'Alice'})
{'name': 'Alice'}
```

```pycon
>>> embody({'count': '${n}'}, {'n': 42})
{'count': 42}
```

```pycon
>>> embody(['${a}', '${b}'], {'a': 1, 'b': 2})
[1, 2]
```

### embody.extract_template_vars(template, syntax='dollar_brace')

Extract all template variable names from a string.

* **Parameters:**
  * **template** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Template string containing variables
  * **syntax** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Variable syntax to use
* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]
* **Returns:**
  List of variable names found in the template

### Examples

```pycon
>>> extract_template_vars('Hello ${name}, you are ${age} years old')
['name', 'age']
>>> extract_template_vars('Hello {name}', syntax='brace')
['name']
```

### embody.flatten_dict(nested_dict, separator='.', parent_key='')

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

### embody.flatten_to_tuples(obj, parent_path=())

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

### embody.get_by_path(obj, path, separator='.', default=None)

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

### embody.get_engine(strategy='recursive', \*\*kwargs)

Get an embodiment engine by name.

* **Parameters:**
  * **strategy** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of strategy (‘recursive’, ‘compiled’, ‘iterative’)
  * **\*\*kwargs** – Arguments to pass to engine constructor
* **Return type:**
  [`BaseEmbodimentEngine`](embody.strategies.html.md#embody.strategies.BaseEmbodimentEngine)
* **Returns:**
  Embodiment engine instance

### Examples

```pycon
>>> engine = get_engine('recursive', syntax='brace')
>>> isinstance(engine, RecursiveVisitorEngine)
True
```

### embody.is_exact_match(template, syntax='dollar_brace')

Check if template is exactly one variable placeholder (no other text).

This is crucial for type preservation. If the template is exactly ${var},
we should return the raw value, not convert it to a string.

* **Parameters:**
  * **template** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Template string to check
  * **syntax** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Variable syntax to use
* **Return type:**
  [`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]
* **Returns:**
  Variable name if exact match, None otherwise

### Examples

```pycon
>>> is_exact_match('${name}')
'name'
>>> is_exact_match('Hello ${name}')
```

```pycon
>>> is_exact_match('${count}')
'count'
```

### embody.max_depth(obj, current_depth=0)

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

### embody.parse_path(path, format='auto')

Parse a path in various formats.

* **Parameters:**
  * **path** ([`Union`](https://docs.python.org/3/library/typing.html#typing.Union)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Tuple`](https://docs.python.org/3/library/typing.html#typing.Tuple), [`List`](https://docs.python.org/3/library/typing.html#typing.List)]) – Path in any supported format
  * **format** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Format hint (‘auto’, ‘json_pointer’, ‘dot’, ‘tuple’)
* **Return type:**
  [`Union`](https://docs.python.org/3/library/typing.html#typing.Union)[[`JSONPointer`](embody.paths.html.md#embody.paths.JSONPointer), [`DotPath`](embody.paths.html.md#embody.paths.DotPath), [`TuplePath`](embody.paths.html.md#embody.paths.TuplePath)]
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

### embody.resolve_path(data, path, default=None, format='auto')

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

### embody.set_by_path(obj, path, value, separator='.', create_intermediate=True)

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

### embody.set_path(data, path, value, format='auto', create_intermediate=True)

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

### embody.substitute(template, params, syntax='dollar_brace', strict=False)

Perform type-preserving substitution on a template value.

This is the core substitution function. It handles:

1. Exact match: ${var} -> returns params[‘var’] with type preserved
2. Partial match: “Count is ${var}” -> string interpolation
3. Non-string templates: returned unchanged

* **Parameters:**
  * **template** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – The template value (can be any type)
  * **params** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Dictionary of parameters for substitution
  * **syntax** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Variable syntax to use
  * **strict** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, raise KeyError for missing variables
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  The substituted value with type preservation

### Examples

```pycon
>>> substitute('${count}', {'count': 42})
42
>>> substitute('Count: ${count}', {'count': 42})
'Count: 42'
>>> substitute('${active}', {'active': True})
True
>>> substitute('${items}', {'items': [1, 2, 3]})
[1, 2, 3]
>>> substitute(42, {})
42
```

### embody.unflatten_dict(flat_dict, separator='.')

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

### embody.unflatten_from_tuples(flat_dict)

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

### Modules

| [`base`](embody.base.html.md#module-embody.base)                           | Core classes for embody: Context, Template, and Embodier.                                                      |
|----------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| [`graphviz_template`](embody.graphviz_template.html.md#module-embody.graphviz_template) | Graphviz templates                                                                                             |
| [`mappings`](embody.mappings.html.md#module-embody.mappings)                   | Mapping interface wrappers for embodied objects.                                                               |
| [`naming`](embody.naming.html.md#module-embody.naming)                       | This module is about generating, validating, and operating on (parametrized) fields (i.e. stings, e.g. paths). |
| [`paths`](embody.paths.html.md#module-embody.paths)                         | Path addressing for nested data structures.                                                                    |
| [`strategies`](embody.strategies.html.md#module-embody.strategies)               | Traversal strategies for template embodiment.                                                                  |
| [`substitution`](embody.substitution.html.md#module-embody.substitution)           | Pattern matching and type-preserving substitution logic for templates.                                         |
| [`templater`](embody.templater.html.md#module-embody.templater)                 | Base objects for definding templates                                                                           |
| [`templating`](embody.templating.html.md#module-embody.templating)               | Making templates for various objects                                                                           |
| [`util`](embody.util.html.md#module-embody.util)                           | Utility functions for embody: flattening, unflattening, and cycle detection.                                   |
