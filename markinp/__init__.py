"""markinp — read, validate, and build Program MARK encounter-history files.

markinp is an independent, unofficial utility. It is not affiliated with,
endorsed by, or maintained by the authors of Program MARK or RMark. "MARK" is
referenced only to describe the file format it interoperates with.

Public API (library-first; the CLI is a thin wrapper over these):

    >>> from markinp import parse_text, validate
    >>> result = parse_text("1001 1;\\n0101 2;\\n")
    >>> diagnostics = validate(result.dataset)
"""

from __future__ import annotations

from .build import BuildOptions, BuildResult, build_dataset, build_file
from .model import (
    Dataset,
    DataType,
    Diagnostic,
    EncounterHistory,
    Severity,
)
from .parse import ParseResult, parse_file, parse_text
from .validate import validate
from .write import write_file, write_text

__version__ = "0.2.0"

__all__ = [
    "BuildOptions",
    "BuildResult",
    "Dataset",
    "DataType",
    "Diagnostic",
    "EncounterHistory",
    "ParseResult",
    "Severity",
    "__version__",
    "build_dataset",
    "build_file",
    "parse_file",
    "parse_text",
    "validate",
    "write_file",
    "write_text",
]
