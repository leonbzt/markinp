"""Render diagnostics and summaries as human text or versioned JSON.

This module owns *presentation*. It decides nothing about validity — it receives
a dataset and a list of diagnostics and turns them into strings. Exit-code logic
lives in :func:`has_errors`; the CLI calls it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .model import Dataset, Diagnostic, Severity

SCHEMA_VERSION = 1


@dataclass
class RenderOptions:
    """Presentation flags carried from the CLI."""

    strict: bool = False
    color: bool = False


def effective_severity(diag: Diagnostic, strict: bool) -> Severity:
    """A WARNING becomes an ERROR under ``--strict``; others are unchanged."""
    if strict and diag.severity == Severity.WARNING:
        return Severity.ERROR
    return diag.severity


def has_errors(diagnostics: list[Diagnostic], strict: bool = False) -> bool:
    """True if any diagnostic is (or is promoted to) ERROR severity."""
    return any(effective_severity(d, strict) == Severity.ERROR for d in diagnostics)


def counts(diagnostics: list[Diagnostic], strict: bool = False) -> dict[str, int]:
    """Count diagnostics by effective severity."""
    result = {"errors": 0, "warnings": 0, "infos": 0}
    for diag in diagnostics:
        sev = effective_severity(diag, strict)
        if sev == Severity.ERROR:
            result["errors"] += 1
        elif sev == Severity.WARNING:
            result["warnings"] += 1
        else:
            result["infos"] += 1
    return result


def structure_summary(dataset: Dataset) -> dict[str, object]:
    """The inferred-structure block shared by validate/inspect output."""
    return {
        "n_occasions": dataset.n_occasions,
        "n_groups": dataset.n_groups,
        "n_covariates": dataset.n_covariates,
        "n_records": len(dataset.records),
        "n_individuals": dataset.n_individuals(),
        "data_type": dataset.data_type.value,
    }


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" + ("" if n == 1 else "s")


def _structure_line(dataset: Dataset) -> str:
    return (
        f"{_plural(dataset.n_occasions, 'occasion')}, "
        f"{_plural(dataset.n_groups, 'group')}, "
        f"{_plural(dataset.n_covariates, 'covariate')}, "
        f"{dataset.data_type.value}"
    )


def _format_diagnostic(diag: Diagnostic, strict: bool) -> str:
    sev = effective_severity(diag, strict).value
    where = f"line {diag.line}: " if diag.line is not None else ""
    return f"  {diag.code}  {sev:<7} {where}{diag.message}\n           hint: {diag.hint}"


def render_validate_human(
    dataset: Dataset, diagnostics: list[Diagnostic], *, strict: bool, path: str
) -> str:
    """Human-readable report for ``markinp validate``."""
    tally = counts(diagnostics, strict)
    lines = [
        f"markinp validate {path}",
        "",
        f"Structure: {_structure_line(dataset)}",
        f"Records:   {len(dataset.records)}   Individuals: {dataset.n_individuals()}",
    ]
    if diagnostics:
        lines.append("")
        for diag in diagnostics:
            lines.append(_format_diagnostic(diag, strict))
    lines.append("")
    verdict = "FAIL" if has_errors(diagnostics, strict) else "PASS"
    lines.append(
        f"Summary: {_plural(tally['errors'], 'error')}, "
        f"{_plural(tally['warnings'], 'warning')}, "
        f"{_plural(tally['infos'], 'info')}  ->  {verdict}"
    )
    return "\n".join(lines)


def validate_payload(
    dataset: Dataset, diagnostics: list[Diagnostic], *, strict: bool, path: str
) -> dict[str, object]:
    """The JSON object describing one validated file (reused for batches)."""
    tally = counts(diagnostics, strict)
    return {
        "schema_version": SCHEMA_VERSION,
        "command": "validate",
        "file": path,
        "ok": not has_errors(diagnostics, strict),
        "summary": {**structure_summary(dataset), **tally},
        "diagnostics": [_diag_to_dict(d, strict) for d in diagnostics],
    }


def render_validate_json(
    dataset: Dataset, diagnostics: list[Diagnostic], *, strict: bool, path: str
) -> str:
    """Versioned JSON report for a single ``markinp validate`` file."""
    return json.dumps(validate_payload(dataset, diagnostics, strict=strict, path=path), indent=2)


def render_inspect_human(dataset: Dataset, diagnostics: list[Diagnostic], *, path: str) -> str:
    """Human-readable structure summary for ``markinp inspect``."""
    lines = [
        f"markinp inspect {path}",
        "",
        f"  data type:   {dataset.data_type.value}",
        f"  occasions:   {dataset.n_occasions}",
        f"  groups:      {dataset.n_groups}",
        f"  covariates:  {dataset.n_covariates}",
        f"  records:     {len(dataset.records)}",
        f"  individuals: {dataset.n_individuals()}",
    ]
    warnings = [d for d in diagnostics if d.severity != Severity.ERROR]
    if warnings:
        lines.append("")
        lines.append("Notes:")
        for diag in warnings:
            lines.append(_format_diagnostic(diag, strict=False))
    return "\n".join(lines)


def render_inspect_json(dataset: Dataset, diagnostics: list[Diagnostic], *, path: str) -> str:
    """JSON structure summary for ``markinp inspect``."""
    payload = {
        "schema_version": SCHEMA_VERSION,
        "command": "inspect",
        "file": path,
        "summary": structure_summary(dataset),
        "diagnostics": [
            _diag_to_dict(d, strict=False) for d in diagnostics if d.severity != Severity.ERROR
        ],
    }
    return json.dumps(payload, indent=2)


def _diag_to_dict(diag: Diagnostic, strict: bool) -> dict[str, object]:
    return {
        "code": diag.code,
        "severity": effective_severity(diag, strict).value,
        "message": diag.message,
        "hint": diag.hint,
        "line": diag.line,
        "col": diag.col,
    }
