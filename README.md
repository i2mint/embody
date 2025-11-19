# embody

**Structural Object Embodiment for Python** - Transform skeletal templates into fully realized, type-safe objects through recursive hydration.

[![Documentation](https://img.shields.io/badge/docs-i2mint-blue)](https://i2mint.github.io/embody/)
[![PyPI version](https://img.shields.io/pypi/v/embody.svg)](https://pypi.org/project/embody/)
[![Python](https://img.shields.io/pypi/pyversions/embody.svg)](https://pypi.org/project/embody/)

## What is Embody?

Embody is a powerful library for **templated object generation** that goes beyond simple string formatting. It provides **structural embodiment** - the recursive hydration of nested data structures with type preservation, cycle detection, and intelligent traversal strategies.

### Key Features

- **🎯 Type Preservation**: Variables like `${count}` preserve their types (int, bool, list, dict) instead of converting everything to strings
- **🔄 Multiple Strategies**: Choose between recursive visitor, compiled path, or iterative stack traversal
- **🎨 Multiple Syntaxes**: Support for `${var}`, `{var}`, and `[[var]]` template syntaxes
- **🛡️ Cycle Detection**: Automatically detect and prevent circular references
- **📍 Path Addressing**: Access nested data via JSON Pointer, dot notation, or tuple paths
- **🗺️ Mapping Interfaces**: Uniform interfaces for attribute access, flattening, and path-based operations
- **⚡ Performance**: Auto-selects optimal strategy based on template complexity
- **🔒 Type Safety**: Full integration with Pydantic and other validation libraries

## Installation

```bash
pip install embody
```

## Quick Start

### Basic Usage

```python
from embody import embody

# Simple template embodiment
template = {
    'name': '${name}',
    'age': '${age}',
    'greeting': 'Hello ${name}!'
}

result = embody(template, {'name': 'Alice', 'age': 30})
# {'name': 'Alice', 'age': 30, 'greeting': 'Hello Alice!'}
```

### Type Preservation

Unlike traditional templating, embody preserves types:

```python
template = {
    'count': '${num}',        # Will be int, not string!
    'active': '${flag}',       # Will be bool
    'items': '${list}',        # Will be list
    'message': 'Count: ${num}' # Will be string (interpolation)
}

result = embody(template, {
    'num': 42,
    'flag': True,
    'list': [1, 2, 3]
})

assert isinstance(result['count'], int)    # True - type preserved!
assert isinstance(result['active'], bool)  # True
assert isinstance(result['items'], list)   # True
```

### Nested Structures

Embody handles deep nesting naturally:

```python
template = {
    'user': {
        'profile': {
            'name': '${name}',
            'settings': {
                'theme': '${theme}',
                'notifications': '${notify}'
            }
        }
    }
}

result = embody(template, {
    'name': 'Bob',
    'theme': 'dark',
    'notify': True
})
```

## Advanced Features

### Context with Resolvers

```python
from embody import Context
import datetime

ctx = Context({
    'now': lambda: datetime.datetime.now(),
    'user': 'Alice'
})

# Callables are invoked on access
print(ctx['now'])   # Current time
print(ctx['user'])  # 'Alice'
```

### Mapping Interfaces

```python
from embody.mappings import AttributeMapping, PathMapping

# Attribute access (Box pattern)
attr_map = AttributeMapping({'user': {'name': 'Alice'}})
print(attr_map.user.name)  # 'Alice'

# Path-based access
path_map = PathMapping({'a': {'b': {'c': 42}}})
print(path_map['a.b.c'])        # Dot notation
print(path_map['/a/b/c'])       # JSON Pointer
print(path_map[('a', 'b', 'c')]) # Tuple path
```

### Path Addressing

```python
from embody.paths import JSONPointer, resolve_path

data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}

# JSON Pointer (RFC 6901)
ptr = JSONPointer('/users/0/name')
print(ptr.resolve(data))  # 'Alice'

# Convenience function
print(resolve_path(data, 'users.0.name'))  # 'Alice'
```

### Traversal Strategies

```python
from embody import Embodier

template = {'data': '${value}'}

# Recursive visitor (default, best for one-off templates)
embodier1 = Embodier(template, strategy='recursive')

# Compiled path (best for repeated embodiment)
embodier2 = Embodier(template, strategy='compiled')

# Auto-select based on template complexity
embodier3 = Embodier(template, strategy='auto')

result = embodier1({'value': 42})
```

## Examples

### Configuration Management

```python
from embody import embody
import os

config_template = {
    'database': {
        'host': '${db_host}',
        'port': '${db_port}',
        'name': '${db_name}'
    },
    'api': {
        'base_url': '${api_url}',
        'timeout': '${timeout}'
    }
}

config = embody(config_template, {
    'db_host': os.getenv('DB_HOST', 'localhost'),
    'db_port': int(os.getenv('DB_PORT', '5432')),
    'db_name': 'myapp',
    'api_url': 'https://api.example.com',
    'timeout': 30
})
```

### API Response Templates

```python
from embody import Embodier

response_template = {
    'status': 'success',
    'data': {
        'user_id': '${id}',
        'name': '${name}',
        'timestamp': '${ts}'
    }
}

embodier = Embodier(response_template, strategy='compiled')

# Efficiently generate many responses
for user in users:
    response = embodier({
        'id': user.id,
        'name': user.name,
        'ts': datetime.now()
    })
```

## Backwards Compatibility

The original `Templater` API is fully preserved:

```python
from embody.templater import Templater

template = {
    'hello': '{name}',
    'how are you': ['{verb}', 2, '{name} and {verb} again']
}

g = Templater.template_func(template=template)
result = g(name='NAME', verb="VERB")
# {'hello': 'NAME', 'how are you': ['VERB', 2, 'NAME and VERB again']}
```

## Documentation

- [Full Documentation](https://i2mint.github.io/embody/)
- [Advanced Examples](./EXAMPLES.md)
- [API Reference](https://i2mint.github.io/embody/api/)

## Contributing

Contributions are welcome! Please see our [contributing guidelines](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) file for details.
