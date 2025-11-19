"""Generate templated objects with advanced structural embodiment features.

This package provides powerful tools for template-based object generation,
supporting:
- Multiple syntax styles (${var}, {var}, [[var]])
- Type-preserving substitution
- Multiple traversal strategies (recursive, compiled, iterative)
- Cycle detection
- Mapping interfaces with various access patterns
- Path-based addressing (JSON Pointer, dot notation, tuple paths)

Basic usage:
    >>> from embody import embody
    >>> template = {'name': '${name}', 'age': '${age}'}
    >>> result = embody(template, {'name': 'Alice', 'age': 30})
    >>> result
    {'name': 'Alice', 'age': 30}

Advanced usage:
    >>> from embody import Embodier, Context
    >>> template = {'greeting': 'Hello ${name}', 'count': '${num}'}
    >>> embodier = Embodier(template, syntax='dollar_brace', strict=True)
    >>> embodier({'name': 'Alice', 'num': 42})
    {'greeting': 'Hello Alice', 'count': 42}
"""

# Original API (preserved for backwards compatibility)
from embody.templater import Templater

# New enhanced API
from embody.base import (
    embody,
    Embodier,
    Context,
    TemplateWrapper,
    MissingParameterError,
)

from embody.strategies import (
    RecursiveVisitorEngine,
    CompiledPathEngine,
    IterativeStackEngine,
    get_engine,
    KeyCollisionError,
)

from embody.substitution import (
    SubstitutionSyntax,
    substitute,
    extract_template_vars,
    is_exact_match,
)

from embody.util import (
    flatten_dict,
    unflatten_dict,
    flatten_to_tuples,
    unflatten_from_tuples,
    detect_cycle,
    get_by_path,
    set_by_path,
    max_depth,
    count_template_markers,
    CycleError,
    PathNotFoundError,
)

from embody.mappings import (
    EmbodiedMapping,
    LazyEmbodiedMapping,
    FlatMapping,
    AttributeMapping,
    FrozenMapping,
    MutableEmbodiedMapping,
    PathMapping,
    as_mapping,
)

from embody.paths import (
    JSONPointer,
    DotPath,
    TuplePath,
    parse_path,
    resolve_path,
    set_path,
    InvalidPathError,
)

__version__ = "0.1.7"  # Keep in sync with package version

__all__ = [
    # Core functions
    "embody",
    "Embodier",
    "Context",
    "TemplateWrapper",
    # Original API
    "Templater",
    # Strategies
    "RecursiveVisitorEngine",
    "CompiledPathEngine",
    "IterativeStackEngine",
    "get_engine",
    # Substitution
    "SubstitutionSyntax",
    "substitute",
    "extract_template_vars",
    "is_exact_match",
    # Utilities
    "flatten_dict",
    "unflatten_dict",
    "flatten_to_tuples",
    "unflatten_from_tuples",
    "detect_cycle",
    "get_by_path",
    "set_by_path",
    "max_depth",
    "count_template_markers",
    # Mappings
    "EmbodiedMapping",
    "LazyEmbodiedMapping",
    "FlatMapping",
    "AttributeMapping",
    "FrozenMapping",
    "MutableEmbodiedMapping",
    "PathMapping",
    "as_mapping",
    # Paths
    "JSONPointer",
    "DotPath",
    "TuplePath",
    "parse_path",
    "resolve_path",
    "set_path",
    # Exceptions
    "MissingParameterError",
    "KeyCollisionError",
    "CycleError",
    "PathNotFoundError",
    "InvalidPathError",
]
