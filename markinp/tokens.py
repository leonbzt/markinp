"""Small, pure helpers for classifying numeric tokens.

Frequencies must be integers; covariates are floats. The single hardest
inference in the tool is telling a group-frequency column from a covariate
column when neither is declared, because the number of groups and covariates is
*not stored in the file*. The rule markinp uses is deliberately simple and
predictable: a value written with a decimal point (or exponent) is treated as a
covariate; an all-integer column is treated as a group frequency. Users tighten
this with ``--groups`` / ``--covariates``.
"""

from __future__ import annotations

#: Tokens ecologists commonly use for "no value", which are illegal as MARK
#: covariates (covariates cannot be missing).
MISSING_MARKERS = frozenset({"", ".", "na", "n/a", "nan", "null", "none", "*", "?", "-"})


def is_int_token(tok: str) -> bool:
    """True if ``tok`` parses as a Python integer (e.g. ``"3"``, ``"-2"``)."""
    try:
        int(tok)
    except ValueError:
        return False
    return True


def is_float_token(tok: str) -> bool:
    """True if ``tok`` parses as a float (e.g. ``"1.5"``, ``"10"``, ``"1e3"``)."""
    try:
        float(tok)
    except ValueError:
        return False
    return True


def looks_like_covariate(tok: str) -> bool:
    """True if ``tok`` is numeric but not a plain integer literal.

    Used only for structure inference: a decimal point or exponent marks a
    column as a covariate rather than a group frequency.
    """
    return is_float_token(tok) and not is_int_token(tok)


def is_missing_marker(tok: str) -> bool:
    """True if ``tok`` is a placeholder for a missing value (illegal covariate)."""
    return tok.strip().lower() in MISSING_MARKERS
