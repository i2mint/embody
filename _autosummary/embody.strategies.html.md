# embody.strategies

Traversal strategies for template embodiment.

This module provides different strategies for traversing and embodying templates:

- RecursiveVisitorEngine: Dynamic traversal using the Visitor pattern
- CompiledPathEngine: Pre-compiled path-based traversal for performance

### Functions

| [`get_engine`](#embody.strategies.get_engine)([strategy])   | Get an embodiment engine by name.   |
|---------------------------------------------------------------------------|-------------------------------------|

### Classes

| [`BaseEmbodimentEngine`](#embody.strategies.BaseEmbodimentEngine)([syntax, strict, ...])   | Base class for embodiment engines.                    |
|------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| [`CompiledPathEngine`](#embody.strategies.CompiledPathEngine)(\*args, \*\*kwargs)        | Pre-compiled path-based traversal strategy.           |
| [`IterativeStackEngine`](#embody.strategies.IterativeStackEngine)([syntax, strict, ...])   | Iterative stack-based traversal strategy.             |
| [`RecursiveVisitorEngine`](#embody.strategies.RecursiveVisitorEngine)([syntax, strict, ...]) | Dynamic traversal strategy using the Visitor pattern. |

### Exceptions

| [`KeyCollisionError`](#embody.strategies.KeyCollisionError)   | Raised when dynamic keys resolve to the same value.   |
|----------------------------------------------------------------------|-------------------------------------------------------|

### *class* embody.strategies.BaseEmbodimentEngine(syntax='dollar_brace', strict=False, key_collision='error')

Bases: [`object`](https://docs.python.org/3/builtins/functions.html#object)

Base class for embodiment engines.

#### embody(template, params)

Embody a template with parameters.

* **Parameters:**
  * **template** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – The template to embody
  * **params** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Parameters for substitution
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  Embodied object

### *class* embody.strategies.CompiledPathEngine(\*args, \*\*kwargs)

Bases: [`BaseEmbodimentEngine`](#embody.strategies.BaseEmbodimentEngine)

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

### *class* embody.strategies.IterativeStackEngine(syntax='dollar_brace', strict=False, key_collision='error')

Bases: [`BaseEmbodimentEngine`](#embody.strategies.BaseEmbodimentEngine)

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

### *exception* embody.strategies.KeyCollisionError

Bases: [`Exception`](https://docs.python.org/3/builtins/exceptions.html#Exception)

Raised when dynamic keys resolve to the same value.

### *class* embody.strategies.RecursiveVisitorEngine(syntax='dollar_brace', strict=False, key_collision='error')

Bases: [`BaseEmbodimentEngine`](#embody.strategies.BaseEmbodimentEngine)

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
  [**CycleError**](embody.html.md#embody.CycleError) – If a circular reference is detected

### embody.strategies.get_engine(strategy='recursive', \*\*kwargs)

Get an embodiment engine by name.

* **Parameters:**
  * **strategy** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Name of strategy (‘recursive’, ‘compiled’, ‘iterative’)
  * **\*\*kwargs** – Arguments to pass to engine constructor
* **Return type:**
  [`BaseEmbodimentEngine`](#embody.strategies.BaseEmbodimentEngine)
* **Returns:**
  Embodiment engine instance

### Examples

```pycon
>>> engine = get_engine('recursive', syntax='brace')
>>> isinstance(engine, RecursiveVisitorEngine)
True
```
