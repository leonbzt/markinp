"""Validate a :class:`~markinp.model.Dataset` and return diagnostics.

``validate`` is the policy layer. It never prints and never exits — it returns a
``list[Diagnostic]`` that :mod:`markinp.report` renders. Structure is taken from
the dataset's *inferred* values unless the caller asserts stricter ones via the
``groups`` / ``occasions`` / ``covariates`` / ``data_type`` arguments, in which
case a mismatch is reported (and, for occasions/counts, escalated).
"""

from __future__ import annotations

from . import diagnostics as dx
from .model import (
    SPECIALIZED_TYPES,
    Dataset,
    DataType,
    Diagnostic,
    EncounterHistory,
)
from .tokens import is_float_token, is_int_token

_STANDARD_TYPES = frozenset({DataType.LIVE_RECAPTURE, DataType.CLOSED_CAPTURES})
_LDLD_TYPES = frozenset({DataType.KNOWN_FATE, DataType.DEAD_RECOVERY})
_STRATUM_LEGAL = frozenset("0ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")


def validate(
    dataset: Dataset,
    *,
    groups: int | None = None,
    occasions: int | None = None,
    covariates: int | None = None,
    data_type: DataType | None = None,
) -> list[Diagnostic]:
    """Run every v0 diagnostic against ``dataset``.

    Args:
        dataset: The parsed dataset.
        groups: Assert an expected group count (mismatches become errors).
        occasions: Assert an expected history length.
        covariates: Assert an expected covariate count.
        data_type: Override the inferred data type for stricter character checks.

    Returns:
        Diagnostics sorted by (line, code) for deterministic output.
    """
    diagnostics: list[Diagnostic] = []

    if not dataset.records:
        return [dx.mk008_no_records()]

    n_occ = occasions if occasions is not None else dataset.n_occasions
    n_grp = groups if groups is not None else dataset.n_groups
    n_cov = covariates if covariates is not None else dataset.n_covariates
    dtype = data_type if data_type is not None else dataset.data_type

    if dtype in SPECIALIZED_TYPES:
        diagnostics.append(dx.mk900_partial_support(dtype.value))
    elif dtype == DataType.UNKNOWN:
        unexpected = sorted({c for r in dataset.records for c in r.history if c not in {"0", "1"}})
        diagnostics.append(dx.mk900_nonstandard_alphabet(unexpected))

    for record in dataset.records:
        diagnostics.extend(_check_history_chars(record, dtype))
        diagnostics.extend(_check_history_length(record, n_occ, occasions is not None))
        diagnostics.extend(_check_ldld(record, dtype))
        diagnostics.extend(_check_columns_and_values(record, n_grp, n_cov))
        diagnostics.extend(_check_all_zero(record))

    diagnostics.extend(_check_empty_groups(dataset.records, n_grp, dataset.group_labels))
    diagnostics.extend(_check_duplicates(dataset.records))

    diagnostics.sort(key=lambda d: (d.line if d.line is not None else -1, d.code))
    return diagnostics


def _check_history_chars(record: EncounterHistory, dtype: DataType) -> list[Diagnostic]:
    """Flag characters illegal for the data type (MK005 / MK017).

    For an inferred non-standard alphabet (``UNKNOWN``) we do not know the legal
    character set, so we skip per-character checks entirely; the single MK900 on
    the file already reports the situation honestly.
    """
    if dtype == DataType.UNKNOWN:
        return []
    diagnostics: list[Diagnostic] = []
    seen: set[str] = set()
    for char in record.history:
        if char in seen:
            continue
        seen.add(char)
        if dtype == DataType.MULTISTRATA:
            if char not in _STRATUM_LEGAL:
                diagnostics.append(dx.mk017_illegal_stratum(record.line, char))
        elif char not in {"0", "1"}:
            diagnostics.append(dx.mk005_illegal_history_char(record.line, char))
    return diagnostics


def _check_history_length(
    record: EncounterHistory, target: int, asserted: bool
) -> list[Diagnostic]:
    """Flag histories whose length disagrees with the file/assertion."""
    if len(record.history) == target:
        return []
    if asserted:
        return [dx.mk010_wrong_occasions(record.line, len(record.history), target)]
    return [dx.mk002_ragged_history(record.line, len(record.history), target)]


def _check_ldld(record: EncounterHistory, dtype: DataType) -> list[Diagnostic]:
    """For LDLD data types, histories must have an even number of columns (MK018)."""
    if dtype in _LDLD_TYPES and len(record.history) % 2 != 0:
        return [dx.mk018_odd_ldld_columns(record.line, len(record.history))]
    return []


def _check_columns_and_values(record: EncounterHistory, n_grp: int, n_cov: int) -> list[Diagnostic]:
    """Check column counts, frequency values, and covariate values."""
    diagnostics: list[Diagnostic] = []
    values = record.raw_values
    expected = n_grp + n_cov

    if n_cov == 0:
        if len(values) != n_grp:
            diagnostics.append(dx.mk004_frequency_count(record.line, len(values), n_grp))
        freq_tokens = values[:n_grp]
        cov_tokens: list[str] = []
    elif len(values) < n_grp:
        diagnostics.append(dx.mk004_frequency_count(record.line, len(values), n_grp))
        freq_tokens = values
        cov_tokens = []
    else:
        freq_tokens = values[:n_grp]
        cov_tokens = values[n_grp:]
        if len(values) != expected:
            diagnostics.append(dx.mk006_covariate_count(record.line, len(cov_tokens), n_cov))

    for tok in freq_tokens:
        diagnostics.extend(_check_frequency(record.line, tok))
    for tok in cov_tokens:
        diagnostics.extend(_check_covariate(record.line, tok))

    return diagnostics


def _check_frequency(line: int, tok: str) -> list[Diagnostic]:
    """A frequency must be an integer; may be negative (loss on capture)."""
    if is_int_token(tok):
        if int(tok) < 0:
            return [dx.mk012_negative_frequency(line, tok)]
        return []
    if is_float_token(tok):
        return [dx.mk014_noninteger_frequency(line, tok)]
    return [dx.mk003_nonnumeric_frequency(line, tok)]


def _check_covariate(line: int, tok: str) -> list[Diagnostic]:
    """A covariate must be a number and cannot be missing or non-numeric (MK007)."""
    if is_float_token(tok):
        return []
    return [dx.mk007_missing_covariate(line, tok)]


def _check_all_zero(record: EncounterHistory) -> list[Diagnostic]:
    """Flag an all-zero history (never encountered) as a warning (MK011)."""
    if record.history and set(record.history) == {"0"}:
        return [dx.mk011_all_zero_history(record.line)]
    return []


def _check_empty_groups(
    records: list[EncounterHistory], n_grp: int, labels: list[str] | None
) -> list[Diagnostic]:
    """Flag any declared group whose frequency column is zero everywhere (MK019)."""
    if n_grp <= 1:
        return []
    totals = [0] * n_grp
    for record in records:
        for i in range(n_grp):
            if i < len(record.raw_values) and is_int_token(record.raw_values[i]):
                totals[i] += abs(int(record.raw_values[i]))
    diagnostics: list[Diagnostic] = []
    for i, total in enumerate(totals):
        if total == 0:
            label = labels[i] if labels and i < len(labels) else None
            diagnostics.append(dx.mk019_empty_group(i, label))
    return diagnostics


def _check_duplicates(records: list[EncounterHistory]) -> list[Diagnostic]:
    """Suggest collapsing rows with identical history and covariates (MK013)."""
    groups: dict[tuple[str, tuple[str, ...]], list[int]] = {}
    for record in records:
        key = (record.history, tuple(record.raw_values))
        groups.setdefault(key, []).append(record.line)
    diagnostics: list[Diagnostic] = []
    for lines in groups.values():
        if len(lines) > 1:
            diagnostics.append(dx.mk013_uncollapsed_duplicates(min(lines), len(lines)))
    return diagnostics
