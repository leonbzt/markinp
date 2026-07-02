"""Core data model for markinp.

These are plain dataclasses shared by every layer. ``Diagnostic`` is the frozen
contract described in ``CLAUDE.md`` section 7 — every problem the tool reports is
one of these. ``Dataset`` is the decoded, in-memory form of an ``.inp`` file.

``EncounterHistory`` keeps the original whitespace-separated tokens after the
history in ``raw_values``. Those tokens are the *authoritative* record of what
the file said; ``frequencies``/``covariates`` are best-effort typed views that
are populated only for tokens that parse cleanly. Validation always works from
``raw_values`` so a malformed token is reported, never silently coerced.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    """How serious a diagnostic is. ``--strict`` promotes WARNING to ERROR."""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class DataType(Enum):
    """The MARK data type a file appears to use.

    Only ``LIVE_RECAPTURE`` / ``CLOSED_CAPTURES`` (the standard 0/1 format) are
    fully validated in v0. The specialized types are detected and structurally
    checked only (see diagnostic ``MK900``).
    """

    LIVE_RECAPTURE = "live_recapture"
    CLOSED_CAPTURES = "closed_captures"
    KNOWN_FATE = "known_fate"
    DEAD_RECOVERY = "dead_recovery"
    MULTISTRATA = "multistrata"
    UNKNOWN = "unknown"


#: Data types that markinp does not yet fully validate.
SPECIALIZED_TYPES = frozenset({DataType.KNOWN_FATE, DataType.DEAD_RECOVERY, DataType.MULTISTRATA})


@dataclass(frozen=True)
class Diagnostic:
    """A single, structured problem report.

    Attributes:
        code: Stable identifier, e.g. ``"MK001"`` (never renumbered once shipped).
        severity: ERROR, WARNING, or INFO.
        message: Plain-English statement of what is wrong.
        hint: Concrete, actionable suggestion for fixing it.
        line: 1-based source line, when known.
        col: 1-based column, when known.
    """

    code: str
    severity: Severity
    message: str
    hint: str
    line: int | None
    col: int | None = None


@dataclass
class EncounterHistory:
    """One record from an ``.inp`` file.

    Attributes:
        history: The encounter-history string, e.g. ``"1001"``.
        frequencies: One integer per group (best-effort typed view of the leading
            ``raw_values``); may be negative to denote losses on capture.
        covariates: Numeric individual covariates (best-effort typed view of the
            trailing ``raw_values``).
        comment: The ``/* ... */`` label attached to the record, if any.
        line: 1-based source line the record was read from.
        raw_values: The original whitespace-separated tokens after the history.
            Authoritative for validation.
    """

    history: str
    frequencies: list[int]
    covariates: list[float]
    comment: str | None
    line: int
    raw_values: list[str] = field(default_factory=list)


@dataclass
class Dataset:
    """A decoded ``.inp`` file plus its inferred structure.

    ``n_occasions``/``n_groups``/``n_covariates``/``data_type`` are *inferred*
    from the data alone (see ``parse.py``). The user can assert stricter values
    on the command line, which ``validate`` compares against.
    """

    n_occasions: int
    n_groups: int
    n_covariates: int
    group_labels: list[str] | None
    cov_labels: list[str] | None
    data_type: DataType
    records: list[EncounterHistory]

    def n_individuals(self) -> int:
        """Total individuals = sum of the absolute values of all frequencies."""
        total = 0
        for record in self.records:
            total += sum(abs(freq) for freq in record.frequencies)
        return total
