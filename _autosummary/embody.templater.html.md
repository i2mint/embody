# embody.templater

Base objects for definding templates

Born from a
[stackoverflow Q&A](https://stackoverflow.com/questions/69383734/templated-object-generation-in-python/69384846).

```pycon
>>> from embody.templater import Templater
>>> # the following template has templated dicts, strings, and lists
>>> template = {
...     'hello': '{name}',
...     'how are you': ['{verb}', 2, '{name} and {verb} again']
... }
>>> g = Templater.template_func(template=template)
>>> g(name='NAME', verb="VERB")
{'hello': 'NAME', 'how are you': ['VERB', 2, 'NAME and VERB again']}
>>> str(g.__signature__)
'(*, name, verb)'
```

### Functions

| `get_generator_return`(gen)                                                             |                                               |
|-----------------------------------------------------------------------------------------|-----------------------------------------------|
| `templated_dict_func`(template)                                                         |                                               |
| `templated_list_func`(template)                                                         |                                               |
| [`templated_string_func`](#embody.templater.templated_string_func)(template)        | A function making templated strings.          |
| [`unique_list_conserving_order`](#embody.templater.unique_list_conserving_order)(iterable) | List of unique elements in the original order |

### Classes

| `Templater`()   |    |
|-----------------|----|

### embody.templater.templated_string_func(template)

A function making templated strings. Like template.format, but with a signature

* **Return type:**
  [`Generator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Generator)[[`str`](https://docs.python.org/3/builtins/stdtypes.html#str), [`None`](https://docs.python.org/3/builtins/constants.html#None), [`Callable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Callable)[[`...`](https://docs.python.org/3/builtins/constants.html#Ellipsis), [`str`](https://docs.python.org/3/builtins/stdtypes.html#str)]]

### embody.templater.unique_list_conserving_order(iterable)

List of unique elements in the original order

```pycon
>>> unique_list_conserving_order([3, 2, 3, 5, 1, 2, 6, 3, 5])
[3, 2, 5, 1, 6]
```

* **Return type:**
  [`list`](https://docs.python.org/3/builtins/stdtypes.html#list)
