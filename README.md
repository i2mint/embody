
# embody
Generate templated objects


To install:	```pip install embody```


# Examples

```python
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
