"""Manual tests to verify embody implementation."""

from embody import embody, Embodier, Context

print("=" * 60)
print("Testing embody implementation")
print("=" * 60)

# Test 1: Basic embodiment
print("\nTest 1: Basic embodiment")
template = {'name': '${name}', 'age': '${age}'}
result = embody(template, {'name': 'Alice', 'age': 30})
print(f"Result: {result}")
assert result == {'name': 'Alice', 'age': 30}
print("✓ Passed")

# Test 2: Type preservation
print("\nTest 2: Type preservation")
template = {'count': '${num}', 'active': '${flag}'}
result = embody(template, {'num': 42, 'flag': True})
print(f"Result: {result}")
print(f"  count type: {type(result['count'])}")
print(f"  active type: {type(result['active'])}")
assert result['count'] == 42 and isinstance(result['count'], int)
assert result['active'] is True and isinstance(result['active'], bool)
print("✓ Passed")

# Test 3: String interpolation
print("\nTest 3: String interpolation")
template = {'message': 'Hello ${name}, you are ${age} years old'}
result = embody(template, {'name': 'Bob', 'age': 25})
print(f"Result: {result}")
assert result['message'] == 'Hello Bob, you are 25 years old'
print("✓ Passed")

# Test 4: Nested structure
print("\nTest 4: Nested structure")
template = {
    'user': {
        'name': '${name}',
        'profile': {
            'age': '${age}'
        }
    }
}
result = embody(template, {'name': 'Charlie', 'age': 35})
print(f"Result: {result}")
assert result['user']['name'] == 'Charlie'
assert result['user']['profile']['age'] == 35
print("✓ Passed")

# Test 5: Lists
print("\nTest 5: Lists")
template = ['${a}', '${b}', '${c}']
result = embody(template, {'a': 1, 'b': 2, 'c': 3})
print(f"Result: {result}")
assert result == [1, 2, 3]
print("✓ Passed")

# Test 6: Dynamic keys
print("\nTest 6: Dynamic keys")
template = {'${key}': '${value}'}
result = embody(template, {'key': 'mykey', 'value': 'myvalue'})
print(f"Result: {result}")
assert result == {'mykey': 'myvalue'}
print("✓ Passed")

# Test 7: Context
print("\nTest 7: Context")
ctx = Context({'name': 'Dave', 'age': 40})
print(f"Context['name']: {ctx['name']}")
print(f"Context['age']: {ctx['age']}")
assert ctx['name'] == 'Dave'
assert ctx['age'] == 40
print("✓ Passed")

# Test 8: Embodier class
print("\nTest 8: Embodier class")
template = {'greeting': 'Hi ${name}'}
embodier = Embodier(template)
result = embodier({'name': 'Eve'})
print(f"Result: {result}")
assert result == {'greeting': 'Hi Eve'}
print("✓ Passed")

# Test 9: Mixed nested (dicts + lists)
print("\nTest 9: Mixed nested structure")
template = {
    'items': [
        {'name': '${item1}', 'price': '${price1}'},
        {'name': '${item2}', 'price': '${price2}'}
    ]
}
params = {'item1': 'Apple', 'price1': 1.50, 'item2': 'Banana', 'price2': 0.75}
result = embody(template, params)
print(f"Result: {result}")
assert result['items'][0]['name'] == 'Apple'
assert result['items'][0]['price'] == 1.50
print("✓ Passed")

# Test 10: Backwards compatibility with old API
print("\nTest 10: Backwards compatibility")
from embody.templater import Templater
template = {
    'hello': '{name}',
    'how are you': ['{verb}', 2, '{name} and {verb} again']
}
g = Templater.template_func(template=template)
result = g(name='NAME', verb="VERB")
print(f"Result: {result}")
assert result == {'hello': 'NAME', 'how are you': ['VERB', 2, 'NAME and VERB again']}
print("✓ Passed")

print("\n" + "=" * 60)
print("All tests passed! ✅")
print("=" * 60)
