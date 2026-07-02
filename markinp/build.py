"""Build a :class:`~markinp.model.Dataset` from a tidy capture table (CSV).

Two layouts are supported:

* **long** — one row per (individual x occasion) with a 0/1 detection flag.
* **wide** — one row per individual, either as occasion columns or a single
  prebuilt ``history`` column.

The builder produces a deterministic dataset: individuals are collapsed by
identical (history, covariates) when requested, groups and covariates are read
in a stable order, and the caller is expected to run :mod:`markinp.validate` on
the result before writing (the CLI does this and refuses to write a bad file).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path

from . import diagnostics as dx
from .model import Dataset, DataType, Diagnostic, EncounterHistory, Severity
from .tokens import is_float_token, is_missing_marker

_TRUE = {"1", "y", "yes", "true", "t", "detected", "seen"}
_FALSE = {"0", "n", "no", "false", "f", "", "."}


@dataclass
class BuildOptions:
    """Column mappings and toggles for :func:`build_dataset`."""

    fmt: str = "auto"  # "long" | "wide" | "auto"
    id_col: str | None = None
    occasion_col: str | None = None
    detect_col: str | None = None
    history_col: str | None = None
    group_col: str | None = None
    covariate_cols: list[str] = field(default_factory=list)
    comment_col: str | None = None
    collapse: bool = True


@dataclass
class _Individual:
    """One individual before frequency vectors and collapsing are applied."""

    history: str
    group: str | None
    covariates: list[str]
    comment: str | None


@dataclass
class BuildResult:
    """The built dataset (or ``None`` on hard failure) plus diagnostics."""

    dataset: Dataset | None
    diagnostics: list[Diagnostic]
    n_rows: int = 0


def _detect_format(header: list[str], opts: BuildOptions) -> str:
    """Choose long vs. wide when ``fmt == "auto"``."""
    if opts.fmt in {"long", "wide"}:
        return opts.fmt
    if opts.history_col:
        return "wide"
    if opts.occasion_col or opts.detect_col:
        return "long"
    return "wide"


def _normalize_detection(value: str, line: int) -> tuple[str, Diagnostic | None]:
    """Map a detection cell to '0'/'1', or report an illegal value."""
    token = value.strip().lower()
    if token in _TRUE:
        return "1", None
    if token in _FALSE:
        return "0", None
    return "0", dx.mk005_illegal_history_char(line, value.strip())


def _reserved_columns(opts: BuildOptions) -> set[str]:
    reserved = set(opts.covariate_cols)
    for col in (opts.id_col, opts.group_col, opts.comment_col, opts.history_col):
        if col:
            reserved.add(col)
    return reserved


def _covariates_for(
    row: dict[str, str], opts: BuildOptions, line: int
) -> tuple[list[str], list[Diagnostic]]:
    """Extract and validate the covariate cells for one row."""
    diagnostics: list[Diagnostic] = []
    values: list[str] = []
    for col in opts.covariate_cols:
        raw = (row.get(col) or "").strip()
        if is_missing_marker(raw) or not is_float_token(raw):
            diagnostics.append(dx.mk007_missing_covariate(line, raw))
            values.append(raw)
        else:
            values.append(_format_number(raw))
    return values, diagnostics


def _format_number(raw: str) -> str:
    """Canonicalize a numeric string so equal values collapse identically."""
    value = float(raw)
    if value == int(value):
        return str(int(value))
    return repr(value)


def _is_detection_token(value: str) -> bool:
    return value.strip().lower() in _TRUE or value.strip().lower() in _FALSE


def _occasion_columns(
    rows: list[dict[str, str]], header: list[str], reserved: set[str]
) -> list[str]:
    """Pick occasion columns: unreserved columns whose cells are all 0/1 flags.

    This lets ``id``/label columns coexist with occasion columns in wide format
    without the user having to enumerate which is which — an id column holds
    non-detection values and is skipped automatically.
    """
    occasion_cols: list[str] = []
    for col in header:
        if col in reserved:
            continue
        if all(_is_detection_token(row.get(col) or "") for row in rows):
            occasion_cols.append(col)
    return occasion_cols


def _read_wide(
    rows: list[dict[str, str]], header: list[str], opts: BuildOptions
) -> tuple[list[_Individual], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    individuals: list[_Individual] = []
    reserved = _reserved_columns(opts)
    occasion_cols = [] if opts.history_col else _occasion_columns(rows, header, reserved)

    for i, row in enumerate(rows):
        line = i + 2  # +1 header, +1 to 1-based
        if opts.history_col:
            history = (row.get(opts.history_col) or "").strip()
        else:
            chars: list[str] = []
            for col in occasion_cols:
                char, diag = _normalize_detection(row.get(col) or "", line)
                if diag:
                    diagnostics.append(diag)
                chars.append(char)
            history = "".join(chars)
        covs, cov_diags = _covariates_for(row, opts, line)
        diagnostics.extend(cov_diags)
        group = (row.get(opts.group_col) or "").strip() if opts.group_col else None
        comment = (row.get(opts.comment_col) or "").strip() if opts.comment_col else None
        individuals.append(_Individual(history, group or None, covs, comment or None))
    return individuals, diagnostics


def _read_long(
    rows: list[dict[str, str]], opts: BuildOptions
) -> tuple[list[_Individual], list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    if not opts.id_col or not opts.occasion_col or not opts.detect_col:
        return [], [_missing_long_columns()]
    id_col = opts.id_col
    occ_col = opts.occasion_col
    det_col = opts.detect_col

    # Preserve first-seen order of individuals.
    order: list[str] = []
    by_id: dict[str, list[tuple[str, dict[str, str], int]]] = {}
    for i, row in enumerate(rows):
        line = i + 2
        ident = (row.get(id_col) or "").strip()
        if ident not in by_id:
            by_id[ident] = []
            order.append(ident)
        by_id[ident].append(((row.get(occ_col) or "").strip(), row, line))

    individuals: list[_Individual] = []
    for ident in order:
        entries = by_id[ident]
        entries.sort(key=lambda e: _occasion_key(e[0]))
        chars: list[str] = []
        for _occ_value, row, line in entries:
            char, diag = _normalize_detection(row.get(det_col) or "", line)
            if diag:
                diagnostics.append(diag)
            chars.append(char)
        first_row = entries[0][1]
        first_line = entries[0][2]
        covs, cov_diags = _covariates_for(first_row, opts, first_line)
        diagnostics.extend(cov_diags)
        group = (first_row.get(opts.group_col) or "").strip() if opts.group_col else None
        comment = (first_row.get(opts.comment_col) or "").strip() if opts.comment_col else None
        individuals.append(_Individual("".join(chars), group or None, covs, comment or None))
    return individuals, diagnostics


def _missing_long_columns() -> Diagnostic:
    return Diagnostic(
        code="MK008",
        severity=Severity.ERROR,
        message="long format needs --id-col, --occasion-col, and --detect-col",
        hint="Name the individual, occasion, and detection columns, or use --format wide",
        line=None,
    )


def _occasion_key(value: str) -> tuple[int, float | str]:
    """Sort occasions numerically when possible, else lexically."""
    try:
        return (0, float(value))
    except ValueError:
        return (1, value)


@dataclass
class _Bucket:
    """Accumulator for one output record while collapsing individuals."""

    history: str
    covariates: list[str]
    frequencies: list[int]
    comment: str | None
    merged: int = 1


def _assemble(individuals: list[_Individual], opts: BuildOptions) -> Dataset:
    """Turn individuals into a Dataset with frequency vectors and optional collapse."""
    groups = sorted({ind.group for ind in individuals if ind.group is not None})
    group_labels = groups if groups else None
    n_groups = len(groups) if groups else 1
    cov_labels = list(opts.covariate_cols) if opts.covariate_cols else None
    n_covariates = len(opts.covariate_cols)

    def group_index(group: str | None) -> int:
        return groups.index(group) if (groups and group is not None) else 0

    buckets: list[_Bucket] = []
    by_key: dict[tuple[str, tuple[str, ...]], _Bucket] = {}
    for ind in individuals:
        vector = [0] * n_groups
        vector[group_index(ind.group)] += 1
        key = (ind.history, tuple(ind.covariates))
        existing = by_key.get(key) if opts.collapse else None
        if existing is None:
            bucket = _Bucket(ind.history, ind.covariates, vector, ind.comment)
            buckets.append(bucket)
            if opts.collapse:
                by_key[key] = bucket
        else:
            for i, freq in enumerate(vector):
                existing.frequencies[i] += freq
            existing.merged += 1
            # A collapsed group of individuals loses its per-individual label.
            if existing.comment != ind.comment:
                existing.comment = None

    records: list[EncounterHistory] = []
    for bucket in buckets:
        raw_values = [str(f) for f in bucket.frequencies] + bucket.covariates
        records.append(
            EncounterHistory(
                history=bucket.history,
                frequencies=list(bucket.frequencies),
                covariates=[float(c) for c in bucket.covariates if is_float_token(c)],
                comment=bucket.comment,
                line=0,
                raw_values=raw_values,
            )
        )

    return Dataset(
        n_occasions=len(records[0].history) if records else 0,
        n_groups=n_groups,
        n_covariates=n_covariates,
        group_labels=group_labels,
        cov_labels=cov_labels,
        data_type=DataType.LIVE_RECAPTURE,
        records=records,
    )


def build_dataset(text: str, opts: BuildOptions) -> BuildResult:
    """Build a dataset from CSV ``text`` according to ``opts``."""
    reader = csv.DictReader(StringIO(text))
    header = list(reader.fieldnames or [])
    rows = list(reader)
    if not rows:
        return BuildResult(None, [dx.mk008_no_records()], 0)

    fmt = _detect_format(header, opts)
    if fmt == "long":
        individuals, diagnostics = _read_long(rows, opts)
    else:
        individuals, diagnostics = _read_wide(rows, header, opts)

    dataset = _assemble(individuals, opts)
    return BuildResult(dataset, diagnostics, len(rows))


def build_file(path: str | Path, opts: BuildOptions) -> BuildResult:
    """Read a CSV file and build a dataset from it."""
    text = Path(path).read_text(encoding="utf-8-sig")
    return build_dataset(text, opts)
