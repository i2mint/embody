# embody.base

Core classes for embody: Context, Template, and Embodier.

This module provides the foundational classes for the embody framework,
implementing the pattern: obj = embody(template, parameters).

### Functions

| [`embody`](#embody.base.embody)(template[, params])   | Convenience function for template embodiment.   |
|-------------------------------------------------------------------------------|-------------------------------------------------|

### Classes

| [`Context`](#embody.base.Context)([params, parent, resolvers, auto_call])   | Parameter store for template embodiment with support for resolvers.   |
|----------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| [`Embodier`](#embody.base.Embodier)(template[, strategy, syntax, ...])       | Main class for embodying templates with parameters.                   |
| [`TemplateWrapper`](#embody.base.TemplateWrapper)(template[, syntax, check_cycles]) | Wrapper for template data with introspection capabilities.            |

### Exceptions

| [`MissingParameterError`](#embody.base.MissingParameterError)   | Raised when a required template parameter is missing.   |
|--------------------------------------------------------------------------|---------------------------------------------------------|

### *class* embody.base.Context(params=None, parent=None, resolvers=None, auto_call=True)

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
  [`Context`](#embody.base.Context)
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
  [`Context`](#embody.base.Context)
* **Returns:**
  New Context with updated parameters

### *class* embody.base.Embodier(template, strategy='auto', syntax='dollar_brace', strict=False, check_cycles=True, key_collision='error')

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

### *exception* embody.base.MissingParameterError

Bases: [`Exception`](https://docs.python.org/3/builtins/exceptions.html#Exception)

Raised when a required template parameter is missing.

### *class* embody.base.TemplateWrapper(template, syntax='dollar_brace', check_cycles=True)

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
  **params** ([`Union`](https://docs.python.org/3/library/typing.html#typing.Union)[[`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict), [`Context`](#embody.base.Context)]) – Parameters to check against
* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]
* **Returns:**
  List of missing parameter names

### embody.base.embody(template, params=None, \*\*kwargs)

Convenience function for template embodiment.

This is the main entry point for simple embodiment use cases.

* **Parameters:**
  * **template** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – The template to embody
  * **params** ([`Union`](https://docs.python.org/3/library/typing.html#typing.Union)[[`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict), [`Context`](#embody.base.Context)]) – Parameters for substitution
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
