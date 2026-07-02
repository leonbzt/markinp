"""Encode a :class:`~markinp.model.Dataset` back to deterministic ``.inp`` text.

Output bytes are identical for identical input: records are emitted in a stable
sort order and separated by ``\\n`` regardless of platform. Writing works from
each record's ``raw_values`` so a parsed file round-trips its exact tokens; the
builder populates ``raw_values`` with freshly formatted numbers.
"""

from __future__ import annotations

from pathlib import Path

from .model import Dataset, EncounterHistory
from .tokens import is_float_token


def _sort_key(record: EncounterHistory) -> tuple[str, tuple[float, ...], str]:
    """Order records by history, then covariate/frequency values, then comment."""
    numeric = tuple(
        float(tok) if is_float_token(tok) else float("inf") for tok in record.raw_values
    )
    return (record.history, numeric, record.comment or "")


def format_record(record: EncounterHistory) -> str:
    """Render one record as a single ``.inp`` line (no trailing newline)."""
    prefix = f"/* {record.comment} */ " if record.comment else ""
    body = " ".join([record.history, *record.raw_values])
    return f"{prefix}{body};"


def write_text(dataset: Dataset) -> str:
    """Render a whole dataset as deterministic ``.inp`` text (trailing newline)."""
    lines = [format_record(r) for r in sorted(dataset.records, key=_sort_key)]
    return "\n".join(lines) + "\n" if lines else ""


def write_file(dataset: Dataset, path: str | Path) -> None:
    """Write ``dataset`` to ``path`` with UNIX newlines and UTF-8 encoding."""
    Path(path).write_text(write_text(dataset), encoding="utf-8", newline="\n")
