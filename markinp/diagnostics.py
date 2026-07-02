"""Factory functions for every diagnostic code.

One function per code keeps the code, severity, and hint text in a single place
so wording stays consistent and codes never drift. The taxonomy is documented in
``plan.md`` section 6; keep the two in sync. Never renumber a released code.
"""

from __future__ import annotations

from .model import Diagnostic, Severity


def _err(
    code: str, message: str, hint: str, line: int | None, col: int | None = None
) -> Diagnostic:
    return Diagnostic(code, Severity.ERROR, message, hint, line, col)


def _warn(
    code: str, message: str, hint: str, line: int | None, col: int | None = None
) -> Diagnostic:
    return Diagnostic(code, Severity.WARNING, message, hint, line, col)


def _info(
    code: str, message: str, hint: str, line: int | None, col: int | None = None
) -> Diagnostic:
    return Diagnostic(code, Severity.INFO, message, hint, line, col)


def mk001_missing_semicolon(line: int) -> Diagnostic:
    return _err(
        "MK001",
        "record is not terminated by a semicolon",
        "Add a ';' at the end of this line to close the record — a missing "
        "semicolon is the most common reason MARK rejects a file",
        line,
    )


def mk002_ragged_history(line: int, length: int, expected: int) -> Diagnostic:
    return _err(
        "MK002",
        f"history is {length} characters but the file uses {expected} occasions",
        "Every history must have exactly one character per occasion; check for "
        "a missing or extra digit on this line",
        line,
    )


def mk003_nonnumeric_frequency(line: int, token: str) -> Diagnostic:
    return _err(
        "MK003",
        f"frequency value {token!r} is not a number",
        "Frequencies must be whole numbers; check for stray text or an accidental "
        "space that split a value",
        line,
    )


def mk004_frequency_count(line: int, found: int, expected: int) -> Diagnostic:
    return _err(
        "MK004",
        f"record has {found} frequency value(s) but the file uses {expected} group(s)",
        "Give exactly one frequency per group; check for a missing or extra value, "
        "or a stray space before the semicolon",
        line,
    )


def mk005_illegal_history_char(line: int, char: str) -> Diagnostic:
    return _err(
        "MK005",
        f"history contains {char!r}, which is not valid for this data type",
        "Standard encounter histories use only '0' and '1'; check for a typo or "
        "set --data-type if this is a specialized format",
        line,
    )


def mk006_covariate_count(line: int, found: int, expected: int) -> Diagnostic:
    return _err(
        "MK006",
        f"record has {found} covariate value(s) but the file uses {expected}",
        "Every record needs the same number of covariates; add the missing value "
        "or remove the extra one",
        line,
    )


def mk007_missing_covariate(line: int, token: str) -> Diagnostic:
    return _err(
        "MK007",
        f"covariate value {token!r} is missing or not numeric",
        "Covariates cannot be blank in MARK; fill in a number or remove the "
        "covariate column entirely",
        line,
    )


def mk008_no_records() -> Diagnostic:
    return _err(
        "MK008",
        "file contains no encounter records",
        "The file is empty or contains only comments; add at least one history "
        "record ending in ';'",
        None,
    )


def mk009_unterminated_comment(line: int) -> Diagnostic:
    return _err(
        "MK009",
        "comment starting here is never closed",
        "Close the comment with '*/'",
        line,
    )


def mk010_wrong_occasions(line: int, length: int, expected: int) -> Diagnostic:
    return _err(
        "MK010",
        f"history is {length} characters but you asserted {expected} occasions",
        f"Expected {expected} occasions but found {length} on this line; check the "
        "history or the --occasions value",
        line,
    )


def mk011_all_zero_history(line: int) -> Diagnostic:
    return _warn(
        "MK011",
        "history is all zeros (never encountered)",
        "An all-zero history is usually invalid for a live-recapture model; verify "
        "this individual belongs in the file",
        line,
    )


def mk012_negative_frequency(line: int, token: str) -> Diagnostic:
    return _warn(
        "MK012",
        f"frequency {token} is negative",
        "A negative frequency is only valid as a loss on capture (removal); confirm "
        "this is intended",
        line,
    )


def mk013_uncollapsed_duplicates(line: int, count: int) -> Diagnostic:
    return _info(
        "MK013",
        f"{count} records share this identical history and covariates",
        "These rows could be aggregated into one record with a summed frequency",
        line,
    )


def mk014_noninteger_frequency(line: int, token: str) -> Diagnostic:
    return _err(
        "MK014",
        f"frequency {token!r} is not a whole number",
        "Frequencies must be integers (write '2', not '2.0' or '1.5')",
        line,
    )


def mk015_content_after_semicolon(line: int) -> Diagnostic:
    return _warn(
        "MK015",
        "there is content after the semicolon that is not a comment",
        "Move it before the ';' or wrap it in '/* ... */'",
        line,
    )


def mk016_mixed_whitespace(line: int) -> Diagnostic:
    return _info(
        "MK016",
        "fields are separated by a mix of tabs and spaces",
        "Harmless, but consistent whitespace keeps the file tidy",
        line,
    )


def mk017_illegal_stratum(line: int, char: str) -> Diagnostic:
    return _err(
        "MK017",
        f"multistrata history contains {char!r}, which is not a stratum letter",
        "Use only '0' and the declared stratum letters (A, B, ...) in a multistrata history",
        line,
    )


def mk018_odd_ldld_columns(line: int, length: int) -> Diagnostic:
    return _err(
        "MK018",
        f"history has {length} columns, which is odd",
        "Known-fate and dead-recovery histories are Live/Dead pairs and must have "
        "an even number of columns",
        line,
    )


def mk019_empty_group(group_index: int, label: str | None) -> Diagnostic:
    who = f"group {group_index + 1}" + (f" ({label})" if label else "")
    return _warn(
        "MK019",
        f"{who} has all-zero frequencies (no individuals)",
        "Check the group setup — a declared group with no individuals is often a mistake",
        None,
    )


def mk020_encoding(message: str, hint: str, line: int | None = None) -> Diagnostic:
    return _warn("MK020", message, hint, line)


def mk900_partial_support(data_type: str) -> Diagnostic:
    return _info(
        "MK900",
        f"this looks like a {data_type} file, which markinp only checks partially",
        "Structure is checked, but full validation of this format is not yet "
        "implemented; treat a clean result with caution",
        None,
    )


def mk900_nonstandard_alphabet(chars: list[str]) -> Diagnostic:
    shown = ", ".join(repr(c) for c in chars)
    return _info(
        "MK900",
        f"histories use characters beyond the standard 0/1 (found: {shown})",
        "This looks like a specialised format (e.g. occupancy, false-positive, or "
        "robust design) that markinp only checks structurally; the encounter "
        "characters are not validated. Pass --data-type live_recapture to enforce "
        "strict 0/1 checking instead",
        None,
    )
