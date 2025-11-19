"""Pattern matching and type-preserving substitution logic for templates.

This module provides the core substitution functionality for embody, supporting
multiple syntaxes (${var}, {var}) with type preservation.
"""

import re
import string
from typing import Any, Dict, Tuple, Pattern, Optional
from collections.abc import Callable


class SubstitutionSyntax:
    """Defines the syntax patterns for template variable substitution."""

    # Pattern for ${var} syntax
    DOLLAR_BRACE = re.compile(r'\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}')
    # Pattern for {var} syntax (Python str.format style)
    BRACE = re.compile(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}')
    # Pattern for [[var]] syntax
    DOUBLE_BRACKET = re.compile(r'\[\[([a-zA-Z_][a-zA-Z0-9_]*)\]\]')

    @classmethod
    def get_pattern(cls, syntax: str = 'dollar_brace') -> Pattern:
        """Get the regex pattern for the specified syntax.

        Args:
            syntax: One of 'dollar_brace', 'brace', 'double_bracket'

        Returns:
            Compiled regex pattern

        Examples:
            >>> pattern = SubstitutionSyntax.get_pattern('dollar_brace')
            >>> pattern.findall('${name} is ${age}')
            ['name', 'age']
        """
        patterns = {
            'dollar_brace': cls.DOLLAR_BRACE,
            'brace': cls.BRACE,
            'double_bracket': cls.DOUBLE_BRACKET,
        }
        return patterns.get(syntax, cls.DOLLAR_BRACE)


def extract_template_vars(
    template: str,
    syntax: str = 'dollar_brace'
) -> list[str]:
    """Extract all template variable names from a string.

    Args:
        template: Template string containing variables
        syntax: Variable syntax to use

    Returns:
        List of variable names found in the template

    Examples:
        >>> extract_template_vars('Hello ${name}, you are ${age} years old')
        ['name', 'age']
        >>> extract_template_vars('Hello {name}', syntax='brace')
        ['name']
    """
    pattern = SubstitutionSyntax.get_pattern(syntax)
    return pattern.findall(template)


def is_exact_match(template: str, syntax: str = 'dollar_brace') -> Optional[str]:
    """Check if template is exactly one variable placeholder (no other text).

    This is crucial for type preservation. If the template is exactly ${var},
    we should return the raw value, not convert it to a string.

    Args:
        template: Template string to check
        syntax: Variable syntax to use

    Returns:
        Variable name if exact match, None otherwise

    Examples:
        >>> is_exact_match('${name}')
        'name'
        >>> is_exact_match('Hello ${name}')

        >>> is_exact_match('${count}')
        'count'
    """
    pattern = SubstitutionSyntax.get_pattern(syntax)
    match = pattern.fullmatch(template)
    if match:
        return match.group(1)
    return None


def substitute(
    template: Any,
    params: Dict[str, Any],
    syntax: str = 'dollar_brace',
    strict: bool = False
) -> Any:
    """Perform type-preserving substitution on a template value.

    This is the core substitution function. It handles:
    1. Exact match: ${var} -> returns params['var'] with type preserved
    2. Partial match: "Count is ${var}" -> string interpolation
    3. Non-string templates: returned unchanged

    Args:
        template: The template value (can be any type)
        params: Dictionary of parameters for substitution
        syntax: Variable syntax to use
        strict: If True, raise KeyError for missing variables

    Returns:
        The substituted value with type preservation

    Examples:
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
    """
    # If not a string, return as-is
    if not isinstance(template, str):
        return template

    # Check for exact match - return raw value (type preserved)
    var_name = is_exact_match(template, syntax)
    if var_name:
        if var_name in params:
            return params[var_name]
        elif strict:
            raise KeyError(f"Missing required parameter: {var_name}")
        else:
            return template  # Return template unchanged if var not found

    # Partial match - do string interpolation
    pattern = SubstitutionSyntax.get_pattern(syntax)
    vars_in_template = pattern.findall(template)

    if not vars_in_template:
        # No variables in template, return as-is
        return template

    # Check if all vars are available
    if strict:
        missing = [var for var in vars_in_template if var not in params]
        if missing:
            raise KeyError(f"Missing required parameters: {missing}")

    # Perform substitution based on syntax
    if syntax == 'brace':
        # Use Python's str.format directly
        try:
            return template.format(**params)
        except KeyError as e:
            if strict:
                raise
            return template
    else:
        # For ${var} and [[var]], we need to replace manually
        result = template
        for var in vars_in_template:
            if var in params:
                # Convert value to string for interpolation
                value_str = str(params[var])
                # Replace the pattern
                if syntax == 'dollar_brace':
                    result = result.replace(f'${{{var}}}', value_str)
                elif syntax == 'double_bracket':
                    result = result.replace(f'[[{var}]]', value_str)
        return result


def substitute_all_syntaxes(
    template: Any,
    params: Dict[str, Any],
    syntaxes: list[str] = None,
    strict: bool = False
) -> Any:
    """Apply substitution for multiple syntax styles.

    Useful when you want to support mixed syntax in templates.

    Args:
        template: The template value
        params: Dictionary of parameters
        syntaxes: List of syntaxes to try (default: ['dollar_brace', 'brace'])
        strict: If True, raise errors for missing variables

    Returns:
        The substituted value

    Examples:
        >>> substitute_all_syntaxes('${name} is {age}', {'name': 'Alice', 'age': 30})
        'Alice is 30'
    """
    syntaxes = syntaxes or ['dollar_brace', 'brace']
    result = template
    for syntax in syntaxes:
        result = substitute(result, params, syntax=syntax, strict=strict)
    return result


# For backwards compatibility with str.format style
class SafeFormatter(string.Formatter):
    """A string formatter that doesn't raise errors for missing keys."""

    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            return kwargs.get(key, '{' + key + '}')
        return super().get_value(key, args, kwargs)


def safe_format(template: str, **params) -> str:
    """Safely format a string, leaving undefined placeholders unchanged.

    Args:
        template: Template string
        **params: Parameters for substitution

    Returns:
        Formatted string

    Examples:
        >>> safe_format('Hello {name}, you are {age}', name='Alice')
        'Hello Alice, you are {age}'
    """
    return SafeFormatter().format(template, **params)
