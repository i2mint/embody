"""Making templates for various objects"""
import string
from itertools import chain
from functools import reduce


class Literal:
    def __init__(self, obj):
        self.obj = obj


class Field:
    def __init__(self, name: str):
        assert str.isidentifier(name), f'Needs to be a valid python identifier: {name}'
        self.name = name


string_formatter = string.Formatter()

dflt_gen_specs = (
    (
        lambda x: isinstance(x, str),
        dict(
            split=string_formatter.parse,
            mapper=lambda x: (x[0], Field(x[1]) if x[1] is not None else ''),
            redu=lambda iterable: ''.join(chain.from_iterable(iterable)),
        ),
    ),
    (lambda x: isinstance(x, list), dict(split=iter, redu=''.join)),
    (lambda x: isinstance(x, dict), dict(split=lambda x: x.items(), redu=''.join)),
)

NoSpecsFound = object()


def get_specs(template, gen_specs=None):
    gen_specs = gen_specs or dflt_gen_specs
    for cond, spec in gen_specs:
        if cond(template):
            yield spec
    return NoSpecsFound  # will be contained in .args of StopIteration error instance


def templated_gen(template, gen_specs=None):
    gen_specs = gen_specs or dflt_gen_specs
    specs = next(get_specs(template, gen_specs), NoSpecsFound)
    print(specs)
    if specs is not NoSpecsFound:
        split, mapper, redu = specs['split'], specs['mapper'], specs['redu']
        # return template, split, mapper, redu
        return redu(map(mapper, split(template)))
