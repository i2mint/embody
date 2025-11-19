"""Basic tests for embody functionality."""

import pytest
from embody import embody, Embodier, Context


def test_simple_dict_embodiment():
    """Test basic dictionary embodiment."""
    template = {'name': '${name}', 'age': '${age}'}
    result = embody(template, {'name': 'Alice', 'age': 30})
    assert result == {'name': 'Alice', 'age': 30}


def test_type_preservation():
    """Test that types are preserved in exact matches."""
    template = {'count': '${num}', 'active': '${flag}', 'items': '${list}'}
    params = {'num': 42, 'flag': True, 'list': [1, 2, 3]}
    result = embody(template, params)

    assert result['count'] == 42
    assert isinstance(result['count'], int)
    assert result['active'] is True
    assert isinstance(result['active'], bool)
    assert result['items'] == [1, 2, 3]
    assert isinstance(result['items'], list)


def test_string_interpolation():
    """Test string interpolation when not exact match."""
    template = {'message': 'Hello ${name}, you are ${age} years old'}
    result = embody(template, {'name': 'Bob', 'age': 25})
    assert result['message'] == 'Hello Bob, you are 25 years old'


def test_nested_dict():
    """Test nested dictionary embodiment."""
    template = {
        'user': {
            'name': '${name}',
            'profile': {
                'age': '${age}',
                'city': '${city}'
            }
        }
    }
    params = {'name': 'Charlie', 'age': 35, 'city': 'NYC'}
    result = embody(template, params)

    assert result['user']['name'] == 'Charlie'
    assert result['user']['profile']['age'] == 35
    assert result['user']['profile']['city'] == 'NYC'


def test_list_embodiment():
    """Test list embodiment."""
    template = ['${a}', '${b}', '${c}']
    result = embody(template, {'a': 1, 'b': 2, 'c': 3})
    assert result == [1, 2, 3]


def test_mixed_nested_structure():
    """Test complex nested structure with dicts and lists."""
    template = {
        'items': [
            {'name': '${item1}', 'price': '${price1}'},
            {'name': '${item2}', 'price': '${price2}'}
        ]
    }
    params = {'item1': 'Apple', 'price1': 1.50, 'item2': 'Banana', 'price2': 0.75}
    result = embody(template, params)

    assert result['items'][0]['name'] == 'Apple'
    assert result['items'][0]['price'] == 1.50
    assert result['items'][1]['name'] == 'Banana'
    assert result['items'][1]['price'] == 0.75


def test_embodier_class():
    """Test using the Embodier class directly."""
    template = {'greeting': 'Hi ${name}'}
    embodier = Embodier(template)
    result = embodier({'name': 'Dave'})
    assert result == {'greeting': 'Hi Dave'}


def test_context():
    """Test Context class."""
    ctx = Context({'name': 'Eve', 'age': 40})
    assert ctx['name'] == 'Eve'
    assert ctx['age'] == 40


def test_context_with_callable():
    """Test Context with callable values."""
    counter = [0]

    def increment():
        counter[0] += 1
        return counter[0]

    ctx = Context({'count': increment})
    assert ctx['count'] == 1
    assert ctx['count'] == 2  # Should increment each time


def test_context_hierarchy():
    """Test Context parent/child hierarchy."""
    parent = Context({'a': 1, 'b': 2})
    child = parent.child({'b': 20, 'c': 30})

    assert child['a'] == 1  # From parent
    assert child['b'] == 20  # Overridden
    assert child['c'] == 30  # New in child


def test_kwargs_params():
    """Test passing params as kwargs."""
    template = {'x': '${x}', 'y': '${y}'}
    result = embody(template, x=10, y=20)
    assert result == {'x': 10, 'y': 20}


def test_dynamic_keys():
    """Test dynamic keys in dictionaries."""
    template = {'${key}': '${value}'}
    result = embody(template, {'key': 'mykey', 'value': 'myvalue'})
    assert result == {'mykey': 'myvalue'}


def test_missing_params_lenient():
    """Test that missing params don't break in lenient mode."""
    template = {'a': '${x}', 'b': '${y}'}
    result = embody(template, {'x': 1}, strict=False)
    # ${y} should remain as-is since it's an exact match and param is missing
    assert result['a'] == 1
    assert result['b'] == '${y}'


def test_missing_params_strict():
    """Test that missing params raise error in strict mode."""
    from embody import MissingParameterError

    template = {'a': '${x}', 'b': '${y}'}
    with pytest.raises(MissingParameterError):
        embody(template, {'x': 1}, strict=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
