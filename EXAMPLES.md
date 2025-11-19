# Embody: Advanced Examples

This document showcases the advanced features of the enhanced `embody` library.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Type Preservation](#type-preservation)
3. [Multiple Syntax Styles](#multiple-syntax-styles)
4. [Context and Resolvers](#context-and-resolvers)
5. [Traversal Strategies](#traversal-strategies)
6. [Mapping Interfaces](#mapping-interfaces)
7. [Path Addressing](#path-addressing)
8. [Cycle Detection](#cycle-detection)
9. [Utility Functions](#utility-functions)

## Basic Usage

### Simple Template Embodiment

```python
from embody import embody

template = {
    'name': '${name}',
    'age': '${age}',
    'email': '${email}'
}

result = embody(template, {
    'name': 'Alice',
    'age': 30,
    'email': 'alice@example.com'
})

print(result)
# {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}
```

### Nested Structures

```python
template = {
    'user': {
        'profile': {
            'name': '${name}',
            'age': '${age}'
        },
        'settings': {
            'theme': '${theme}'
        }
    }
}

result = embody(template, {
    'name': 'Bob',
    'age': 25,
    'theme': 'dark'
})

print(result['user']['profile']['name'])  # 'Bob'
```

## Type Preservation

One of the most powerful features is **type preservation** - when a template value is exactly `${var}`, the type is preserved.

```python
from embody import embody

template = {
    'count': '${count}',          # Will be int
    'active': '${active}',        # Will be bool
    'items': '${items}',          # Will be list
    'config': '${config}',        # Will be dict
    'message': 'Count: ${count}'  # Will be string (interpolation)
}

result = embody(template, {
    'count': 42,
    'active': True,
    'items': [1, 2, 3],
    'config': {'key': 'value'}
})

print(type(result['count']))    # <class 'int'>
print(type(result['active']))   # <class 'bool'>
print(type(result['items']))    # <class 'list'>
print(type(result['config']))   # <class 'dict'>
print(result['message'])         # 'Count: 42' (string)
```

## Multiple Syntax Styles

Embody supports multiple template syntaxes:

```python
from embody import embody

# ${var} syntax (default)
template1 = {'greeting': 'Hello ${name}'}
result1 = embody(template1, {'name': 'Alice'})

# {var} syntax (Python str.format style)
template2 = {'greeting': 'Hello {name}'}
result2 = embody(template2, {'name': 'Bob'}, syntax='brace')

# [[var]] syntax
template3 = {'greeting': 'Hello [[name]]'}
result3 = embody(template3, {'name': 'Charlie'}, syntax='double_bracket')
```

## Context and Resolvers

The `Context` class provides advanced parameter management with support for callables and hierarchical scoping.

### Callable Values (Lazy Evaluation)

```python
from embody import embody, Context
import datetime

ctx = Context({
    'now': lambda: datetime.datetime.now(),
    'random': lambda: random.randint(1, 100),
    'static': 'I am static'
})

# Each access calls the function
print(ctx['now'])      # Current time
print(ctx['now'])      # Different time (called again)
print(ctx['static'])   # Same value
```

### Hierarchical Scoping

```python
from embody import Context

# Parent context
parent = Context({
    'base_url': 'https://api.example.com',
    'version': 'v1',
    'timeout': 30
})

# Child context overrides some values
child = parent.child({
    'version': 'v2',     # Override parent
    'api_key': 'secret'  # Add new value
})

print(child['base_url'])  # 'https://api.example.com' (from parent)
print(child['version'])   # 'v2' (overridden)
print(child['api_key'])   # 'secret' (new)
```

## Traversal Strategies

Embody supports multiple strategies for traversing and embodying templates.

### Recursive Visitor (Default)

Best for one-off templates and dynamic structures.

```python
from embody import Embodier

template = {'data': '${value}'}
embodier = Embodier(template, strategy='recursive')
result = embodier({'value': 42})
```

### Compiled Path Engine

Best for templates that are embodied repeatedly. Compiles once, embodies fast.

```python
from embody import Embodier

template = {'user': {'name': '${name}', 'age': '${age}'}}
embodier = Embodier(template, strategy='compiled')

# First call compiles the template
result1 = embodier({'name': 'Alice', 'age': 30})

# Subsequent calls use the compiled version (faster)
result2 = embodier({'name': 'Bob', 'age': 25})
result3 = embodier({'name': 'Charlie', 'age': 35})
```

### Auto Strategy Selection

The 'auto' strategy automatically selects the best strategy based on template characteristics.

```python
from embody import Embodier

# For shallow, simple templates: uses recursive
simple_template = {'a': '${x}', 'b': '${y}'}
embodier1 = Embodier(simple_template, strategy='auto')

# For deep, complex templates: uses compiled
complex_template = {
    'level1': {
        'level2': {
            'level3': {
                'level4': {
                    'data': '${value}'
                }
            }
        }
    }
}
embodier2 = Embodier(complex_template, strategy='auto')
```

## Mapping Interfaces

Embody provides various mapping interfaces for different access patterns.

### Attribute Access (Box Pattern)

```python
from embody import embody
from embody.mappings import AttributeMapping

data = embody({'user': {'name': '${name}', 'age': '${age}'}},
              {'name': 'Alice', 'age': 30})

attr_map = AttributeMapping(data)

# Access using attributes instead of dict keys
print(attr_map.user.name)  # 'Alice'
print(attr_map.user.age)   # 30
```

### Flat Mapping (Dot Notation)

```python
from embody import embody
from embody.mappings import FlatMapping

data = embody({'a': {'b': {'c': '${value}'}}}, {'value': 42})
flat = FlatMapping(data)

print(flat['a.b.c'])  # 42
print(list(flat.keys()))  # ['a.b.c']
```

### Path Mapping (Multiple Access Styles)

```python
from embody.mappings import PathMapping

data = {'user': {'profile': {'name': 'Alice'}}}
pm = PathMapping(data)

# All of these work:
print(pm['user']['profile']['name'])  # Dict access
print(pm['user.profile.name'])         # Dot notation
print(pm[('user', 'profile', 'name')]) # Tuple path
print(pm['/user/profile/name'])        # JSON Pointer
```

### Frozen Mapping (Immutable)

```python
from embody.mappings import FrozenMapping

data = {'a': 1, 'b': 2}
frozen = FrozenMapping(data)

# Cannot modify
try:
    frozen['c'] = 3
except TypeError:
    print("Cannot modify frozen mapping")

# Can be hashed (useful for caching)
print(hash(frozen))
```

## Path Addressing

Embody supports multiple path addressing schemes for nested data.

### JSON Pointer (RFC 6901)

```python
from embody.paths import JSONPointer

data = {
    'users': [
        {'name': 'Alice', 'age': 30},
        {'name': 'Bob', 'age': 25}
    ]
}

# Access first user's name
ptr = JSONPointer('/users/0/name')
print(ptr.resolve(data))  # 'Alice'

# Set a value
ptr = JSONPointer('/users/1/age')
ptr.set(data, 26)
print(data['users'][1]['age'])  # 26
```

### Dot Notation

```python
from embody.paths import DotPath

data = {'a': {'b': {'c': 42}}}

path = DotPath('a.b.c')
print(path.resolve(data))  # 42
```

### Convenience Function

```python
from embody.paths import resolve_path, set_path

data = {'user': {'profile': {'name': 'Alice'}}}

# All formats work:
print(resolve_path(data, '/user/profile/name'))        # JSON Pointer
print(resolve_path(data, 'user.profile.name'))         # Dot notation
print(resolve_path(data, ('user', 'profile', 'name'))) # Tuple

# Setting values
set_path(data, '/user/profile/age', 30)
print(data)  # {'user': {'profile': {'name': 'Alice', 'age': 30}}}
```

## Cycle Detection

Embody automatically detects and prevents circular references.

```python
from embody import embody
from embody.util import CycleError

# Create a circular structure
circular = {'a': 1}
circular['self'] = circular

# Attempting to embody will raise CycleError
try:
    result = embody(circular, {})
except CycleError as e:
    print(f"Cycle detected: {e}")
```

## Utility Functions

### Flattening and Unflattening

```python
from embody.util import flatten_dict, unflatten_dict

# Flatten nested dict
nested = {'a': {'b': {'c': 1}}, 'd': 2}
flat = flatten_dict(nested)
print(flat)  # {'a.b.c': 1, 'd': 2}

# Unflatten back
unflat = unflatten_dict(flat)
print(unflat)  # {'a': {'b': {'c': 1}}, 'd': 2}
```

### Path-based Get/Set

```python
from embody.util import get_by_path, set_by_path

data = {'a': {'b': {'c': 42}}}

# Get value by path
value = get_by_path(data, 'a.b.c')
print(value)  # 42

# Set value by path
set_by_path(data, 'a.b.d', 100)
print(data)  # {'a': {'b': {'c': 42, 'd': 100}}}
```

### Measuring Depth

```python
from embody.util import max_depth

shallow = {'a': 1, 'b': 2}
print(max_depth(shallow))  # 1

deep = {'a': {'b': {'c': {'d': 1}}}}
print(max_depth(deep))  # 4
```

## Advanced Patterns

### Template Store

```python
from embody import Embodier

# Create a store of reusable templates
templates = {
    'user_greeting': {
        'message': 'Hello ${name}, welcome back!',
        'last_login': '${last_login}'
    },
    'error_response': {
        'error': '${error_type}',
        'message': '${error_message}',
        'code': '${error_code}'
    }
}

# Embody different templates as needed
greeting = Embodier(templates['user_greeting'])
error = Embodier(templates['error_response'])

result1 = greeting({'name': 'Alice', 'last_login': '2024-01-15'})
result2 = error({'error_type': 'NotFound', 'error_message': 'User not found', 'error_code': 404})
```

### Configuration Management

```python
from embody import embody, Context
import os

# Environment-aware configuration
config_template = {
    'database': {
        'host': '${db_host}',
        'port': '${db_port}',
        'name': '${db_name}'
    },
    'api': {
        'base_url': '${api_base_url}',
        'timeout': '${api_timeout}'
    }
}

# Create context with environment variables
ctx = Context({
    'db_host': os.getenv('DB_HOST', 'localhost'),
    'db_port': int(os.getenv('DB_PORT', '5432')),
    'db_name': os.getenv('DB_NAME', 'myapp'),
    'api_base_url': os.getenv('API_BASE_URL', 'https://api.example.com'),
    'api_timeout': int(os.getenv('API_TIMEOUT', '30'))
})

config = embody(config_template, ctx)
```

### Dynamic API Responses

```python
from embody import Embodier

# Template for API response
response_template = {
    'status': 'success',
    'data': {
        'user': {
            'id': '${user_id}',
            'name': '${user_name}',
            'email': '${user_email}'
        },
        'metadata': {
            'timestamp': '${timestamp}',
            'version': 'v1'
        }
    }
}

embodier = Embodier(response_template, strategy='compiled')

# Generate responses for multiple users
import datetime

for user in [('1', 'Alice', 'alice@example.com'), ('2', 'Bob', 'bob@example.com')]:
    response = embodier({
        'user_id': user[0],
        'user_name': user[1],
        'user_email': user[2],
        'timestamp': datetime.datetime.now().isoformat()
    })
    print(response)
```

## Integration with Pydantic

Embody can be integrated with Pydantic for validation:

```python
from embody import embody
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    name: str
    age: int
    email: EmailStr

template = {
    'name': '${name}',
    'age': '${age}',
    'email': '${email}'
}

# Embody and validate
raw_data = embody(template, {
    'name': 'Alice',
    'age': 30,
    'email': 'alice@example.com'
})

# Validate with Pydantic
user = User(**raw_data)
print(user.model_dump())
```
