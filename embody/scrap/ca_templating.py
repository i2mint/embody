"""CA templating"""

from functools import partial
import operator as o
from verb import Command


def example():
    # ------------------------The new syntax, essentially all you need to change on
    # your side------------------------------------------
    class PlaceHolder:
        pass

    ph = PlaceHolder()

    # This is how Andie defined the conditions:
    # phase_definitions = [{'phase_name': 'phase_1', 'tag_filters': [{'tag':
    # 'temperature', 'operator': '<', 'value': 80},
    #                                                                {'tag':
    #                                                                'temperature',
    #                                                                'operator': '>',
    #                                                                'value': 60}]},
    #                      {'phase_name': 'phase_2', 'tag_filters': [{'tag':
    #                      'temperature', 'operator': '>', 'value': 0}]}]

    # The same translated in Thor's language
    thored_phase_definitions = [
        {
            'phase_name': 'phase_1',
            'tag_filters': {
                '&': (
                    {'<': ({'[]': (ph, 'temperature')}, 80)},
                    {'>': ({'[]': (ph, 'temperature')}, 60)},
                )
            },
        },
        {
            'phase_name': 'phase_2',
            'tag_filters': {'<': ({'[]': (ph, 'temperature')}, 80)},
        },
    ]

    # ------------------------How to write and execute a command to test a phase
    # condition, basically copy that code------------------------------------------

    from verb import Literal

    # then say you want to test if a certain event satisfies the condition:
    event_to_test = {'temperature': 2}
    # for a somewhat technical reason, you need at the moment to add that Literal to
    # your event_to_test, Thor is/worked at removing that so it most likely will not
    # be needed by the time you get that, if you pull verb
    event_to_test = Literal(event_to_test)
    # I pick for the demo the conditions defining the first phase in the
    # thored_phase_definitions
    condition_to_test = thored_phase_definitions[0]['tag_filters']
    # we then can translate the conditions into a dictionary which Command can understand
    command_dict = recursive_format_iterable(
        condition_to_test,
        {
            dict: {
                'replace_dict': {PlaceHolder: event_to_test},
                'init_func': dict_init_func,
                'search_func': dict_search_func,
                'set_func': set_in_dict,
                'post_process_output': lambda x: x,
            },
            tuple: {
                'replace_dict': {PlaceHolder: event_to_test},
                'init_func': tuple_init_func,
                'search_func': tuple_search_func,
                'set_func': set_in_tuple,
                'post_process_output': lambda x: tuple(x),
            },
        },
    )
    # and finally, we can execute the command, returning whether or not event_to_test satisfies the conditions to belong to phase 1
    Command.from_dict(command_dict, func_of_key)()


func_of_key = {
    '&': o.and_,
    '>': o.gt,
    '<': o.lt,
    '>=': o.ge,
    '<=': o.le,
    '==': o.eq,
    '[]': lambda d, tag: d[tag],
}


def dict_search_func(item, iterable):
    return iterable[item]


def set_in_dict(iterable, item, val):
    iterable[item] = val


def dict_init_func(iterable):
    return dict()


class PlaceHolder_1:
    pass


class PlaceHolder_2:
    pass


ph_1 = PlaceHolder_1()
ph_2 = PlaceHolder_2()


def format_iterable(
    iterable,
    replace_dict={PlaceHolder_1: 'NEW', PlaceHolder_2: 'EVEN_NEWER'},
    init_func=dict_init_func,
    search_func=dict_search_func,
    set_func=set_in_dict,
    post_process_output=lambda x: x,
):
    """

    :param iterable:
    :param replace_dict:
    :param init_func:
    :param search_func:
    :param set_func:
    :param post_process_output:
    :return:

    Works by default for dicts
    >>> d = {'a': 1, 'b': (1,2), 'c': ph_1, 'd': ph_2}
    >>> format_iterable(d)
    {'a': 1, 'b': (1, 2), 'c': 'NEW', 'd': 'EVEN_NEWER'}

    >>> # And we can adapt to other iterables
    >>> def tuple_search_func(item, iterable):
    ...    return item

    >>> def set_in_tuple(iterable, item, val):
    ...    iterable.append(val)

    >>> def tuple_init_func(iterable):
    ...    return list()

    >>> t = (1, 'a', ph_1, 2, ph_2)
    >>> format_iterable(t,
    ...                 init_func=tuple_init_func,
    ...                 search_func=tuple_search_func,
    ...                 set_func=set_in_tuple,
    ...                 post_process_output=lambda x: tuple(x))
    (1, 'a', 'NEW', 2, 'EVEN_NEWER')

    """

    iterable_search_for_type = partial(search_func, iterable=iterable)
    new_iterable = init_func(iterable)

    for item in iterable:
        value = iterable_search_for_type(item)
        if type(value) in replace_dict:
            set_func(new_iterable, item, replace_dict[type(value)])
        else:
            set_func(new_iterable, item, value)

    return post_process_output(new_iterable)


def tuple_search_func(item, iterable):
    return item


def set_in_tuple(iterable, item, val):
    iterable.append(val)


def tuple_init_func(iterable):
    return list()


class TypeNotKnown(ValueError):
    pass


def format_multi_iterable(
    iterable,
    recipe={
        dict: {
            'replace_dict': {PlaceHolder_1: 'NEW', PlaceHolder_2: 'EVEN_NEWER'},
            'init_func': dict_init_func,
            'search_func': dict_search_func,
            'set_func': set_in_dict,
            'post_process_output': lambda x: x,
        },
        tuple: {
            'replace_dict': {
                PlaceHolder_1: 'NEW_TUPLE',
                PlaceHolder_2: 'EVEN_NEWER_TUPLE',
            },
            'init_func': tuple_init_func,
            'search_func': tuple_search_func,
            'set_func': set_in_tuple,
            'post_process_output': lambda x: tuple(x),
        },
    },
):
    """
    Same as format_iterable but can handle several types of iterables
    :param iterable:
    :param recipe:
    :return:

    >>> d = {'a': 1, 'b': (1,2), 'c': ph_1, 'd': ph_2}
    >>> format_multi_iterable(d)
    {'a': 1, 'b': (1, 2), 'c': 'NEW', 'd': 'EVEN_NEWER'}

    >>> t = (1, 'a', ph_1, 2, ph_2)
    >>> format_multi_iterable(t)
    (1, 'a', 'NEW', 2, 'EVEN_NEWER')

    """

    iterable_type = type(iterable)
    if iterable_type in recipe:
        return format_iterable(iterable, **recipe[iterable_type])
    else:
        raise TypeNotKnown('The type of your iterable is not in your recipe')


def recursive_format_iterable(
    iterable,
    recipe={
        dict: {
            'replace_dict': {PlaceHolder_1: 'NEW', PlaceHolder_2: 'EVEN_NEWER'},
            'init_func': dict_init_func,
            'search_func': dict_search_func,
            'set_func': set_in_dict,
            'post_process_output': lambda x: x,
        },
        tuple: {
            'replace_dict': {
                PlaceHolder_1: 'NEWTUPLE',
                PlaceHolder_2: 'EVEN_NEWER_TUPLE',
            },
            'init_func': tuple_init_func,
            'search_func': tuple_search_func,
            'set_func': set_in_tuple,
            'post_process_output': lambda x: tuple(x),
        },
    },
):
    iterable_type = type(iterable)
    if iterable_type in recipe:
        recipe_for_type = recipe[iterable_type]
        new_iterable = recipe_for_type['init_func'](iterable=iterable)
        default_set_func = recipe_for_type['set_func']
        default_search_func = partial(recipe_for_type['search_func'], iterable=iterable)
        default_post_process = recipe_for_type['post_process_output']
        default_replace_dict = recipe_for_type['replace_dict']
    else:
        raise TypeNotKnown('The type of your iterable is not in your recipe')

    for item in iterable:
        value = default_search_func(item)
        value_type = type(value)
        if value_type in recipe:
            new_value = recursive_format_iterable(value, recipe=recipe)
        elif value_type in default_replace_dict:
            new_value = default_replace_dict[value_type]
        else:
            new_value = value
        default_set_func(new_iterable, item, new_value)

    return default_post_process(new_iterable)
