"""Base objects for definding templates

Born from a
`stackoverflow Q&A <https://stackoverflow.com/questions/69383734/templated
-object-generation-in-python/69384846>`_.


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
"""

import string
from functools import partial
from inspect import Signature, Parameter
from operator import itemgetter
from typing import Any, TypeVar, Tuple, Dict, List
from collections.abc import Callable, Generator, Iterable
from collections import namedtuple

T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")
V = TypeVar("V")

# TODO: Make these things picklable


def get_generator_return(gen: Generator[T, Any, U]) -> tuple[Generator[T, Any, U], U]:
    return_value = None

    def inner():
        nonlocal return_value
        return_value = yield from gen

    gen_items = list(inner())

    def new_gen():
        yield from gen_items
        return return_value

    return new_gen(), return_value


def unique_list_conserving_order(iterable: Iterable) -> list:
    """List of unique elements in the original order
    >>> unique_list_conserving_order([3, 2, 3, 5, 1, 2, 6, 3, 5])
    [3, 2, 5, 1, 6]
    """
    seen = set()
    return [x for x in iterable if len(seen) < len(seen.add(x) or seen)]


# TemplateFunc: TypeAlias = Generator[str, None, Callable[..., T]]
TemplateFunc = Generator[str, None, Callable[..., T]]


class Templater:
    templater_registry: dict[type, Callable[[Any], TemplateFunc]] = {}

    @classmethod
    def register(cls, handles_type: type):
        def decorator(f):
            cls.templater_registry[handles_type] = f
            return f

        return decorator

    @classmethod
    def template_func_generator(cls, template: T) -> TemplateFunc[T]:
        if type(template) in cls.templater_registry:
            template_factory = cls.templater_registry[type(template)]
            return template_factory(template)
        else:
            # an empty generator that returns a function that returns the template unchanged,
            # since we don't know how to handle it
            def just_return():
                return lambda: template
                yield  # this yield is needed to tell python that this is a generator

            return just_return()

    @classmethod
    def template_func(cls, template: T) -> Callable[..., T]:
        gen = cls.template_func_generator(template)
        params, f = get_generator_return(gen)

        parameters = unique_list_conserving_order(
            Parameter(name=param, kind=Parameter.KEYWORD_ONLY) for param in params
        )
        f.__signature__ = Signature(parameters)
        return f


@Templater.register(str)
def templated_string_func(template: str) -> TemplateFunc[str]:
    """A function making templated strings. Like template.format, but with a signature"""
    f = partial(str.format, template)
    yield from filter(None, map(itemgetter(1), string.Formatter().parse(template)))

    return f


@Templater.register(dict)
def templated_dict_func(template: dict[K, V]) -> TemplateFunc[dict[K, V]]:
    DictEntryInfo = namedtuple(
        "DictEntryInfo", ["key_func", "value_func", "key_args", "value_args"]
    )
    entries: list[DictEntryInfo] = []
    for key, value in template.items():
        key_params, key_template_func = get_generator_return(
            Templater.template_func_generator(key)
        )
        value_params, value_template_func = get_generator_return(
            Templater.template_func_generator(value)
        )
        key_params = tuple(key_params)
        value_params = tuple(value_params)
        yield from key_params
        yield from value_params

        entries.append(
            DictEntryInfo(
                key_template_func, value_template_func, key_params, value_params
            )
        )

    def template_func(**kwargs):
        return {
            entry_info.key_func(
                **{arg: kwargs[arg] for arg in entry_info.key_args}
            ): entry_info.value_func(
                **{arg: kwargs[arg] for arg in entry_info.value_args}
            )
            for entry_info in entries
        }

    return template_func


@Templater.register(list)
def templated_list_func(template: list[T]) -> TemplateFunc[list[T]]:
    entries = []
    for item in template:
        params, item_template_func = get_generator_return(
            Templater.template_func_generator(item)
        )
        params = tuple(params)
        yield from params

        entries.append((item_template_func, params))

    # How is this used?
    def template_func(**kwargs):
        # print(kwargs)
        return [
            item_template_func(**{arg: kwargs[arg] for arg in args})
            for item_template_func, args in entries
        ]

    return template_func
