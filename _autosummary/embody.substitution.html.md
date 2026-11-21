# embody.substitution

Pattern matching and type-preserving substitution logic for templates.

This module provides the core substitution functionality for embody, supporting
multiple syntaxes (${var}, {var}) with type preservation.

### Functions

| [`extract_template_vars`](#embody.substitution.extract_template_vars)(template[, syntax])        | Extract all template variable names from a string.                     |
|---------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| [`is_exact_match`](#embody.substitution.is_exact_match)(template[, syntax])               | Check if template is exactly one variable placeholder (no other text). |
| [`safe_format`](#embody.substitution.safe_format)(template, \*\*params)                | Safely format a string, leaving undefined placeholders unchanged.      |
| [`substitute`](#embody.substitution.substitute)(template, params[, syntax, strict])   | Perform type-preserving substitution on a template value.              |
| [`substitute_all_syntaxes`](#embody.substitution.substitute_all_syntaxes)(template, params[, ...]) | Apply substitution for multiple syntax styles.                         |

### Classes

| [`SafeFormatter`](#embody.substitution.SafeFormatter)()      | A string formatter that doesn't raise errors for missing keys.   |
|-----------------------------------------------------------------------|------------------------------------------------------------------|
| [`SubstitutionSyntax`](#embody.substitution.SubstitutionSyntax)() | Defines the syntax patterns for template variable substitution.  |

### *class* embody.substitution.SafeFormatter

Bases: [`Formatter`](https://docs.python.org/3/library/string.html#string.Formatter)

A string formatter that doesn’t raise errors for missing keys.

### *class* embody.substitution.SubstitutionSyntax

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

### embody.substitution.extract_template_vars(template, syntax='dollar_brace')

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

### embody.substitution.is_exact_match(template, syntax='dollar_brace')

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

### embody.substitution.safe_format(template, \*\*params)

Safely format a string, leaving undefined placeholders unchanged.

* **Parameters:**
  * **template** ([`str`](https://docs.python.org/3/builtins/stdtypes.html#str)) – Template string
  * **\*\*params** – Parameters for substitution
* **Return type:**
  [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)
* **Returns:**
  Formatted string

### Examples

```pycon
>>> safe_format('Hello {name}, you are {age}', name='Alice')
'Hello Alice, you are {age}'
```

### embody.substitution.substitute(template, params, syntax='dollar_brace', strict=False)

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

### embody.substitution.substitute_all_syntaxes(template, params, syntaxes=None, strict=False)

Apply substitution for multiple syntax styles.

Useful when you want to support mixed syntax in templates.

* **Parameters:**
  * **template** ([`Any`](https://docs.python.org/3/library/typing.html#typing.Any)) – The template value
  * **params** ([`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)]) – Dictionary of parameters
  * **syntaxes** ([`list`](https://docs.python.org/3/builtins/stdtypes.html#list)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]) – List of syntaxes to try (default: [‘dollar_brace’, ‘brace’])
  * **strict** ([`bool`](https://docs.python.org/3/builtins/functions.html#bool)) – If True, raise errors for missing variables
* **Return type:**
  [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* **Returns:**
  The substituted value

### Examples

```pycon
>>> substitute_all_syntaxes('${name} is {age}', {'name': 'Alice', 'age': 30})
'Alice is 30'
```
