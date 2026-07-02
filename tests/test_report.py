"""Tests for report rendering, JSON schema, and exit-code logic."""

from __future__ import annotations

import json

from markinp.model import Diagnostic, Severity
from markinp.parse import parse_file
from markinp.report import (
    SCHEMA_VERSION,
    counts,
    has_errors,
    render_validate_json,
)
from markinp.validate import validate

from .conftest import FIXTURES


def _warn() -> Diagnostic:
    return Diagnostic("MK012", Severity.WARNING, "w", "h", 1)


def _err() -> Diagnostic:
    return Diagnostic("MK001", Severity.ERROR, "e", "h", 1)


def test_has_errors_true_for_error() -> None:
    assert has_errors([_err()]) is True


def test_has_errors_false_for_warning() -> None:
    assert has_errors([_warn()]) is False


def test_strict_promotes_warning_to_error() -> None:
    assert has_errors([_warn()], strict=True) is True


def test_counts_respects_strict() -> None:
    tally = counts([_warn(), _err()], strict=True)
    assert tally == {"errors": 2, "warnings": 0, "infos": 0}


def test_validate_json_is_versioned_and_well_formed() -> None:
    result = parse_file(FIXTURES / "missing_semicolon.inp")
    diagnostics = result.diagnostics + validate(result.dataset)
    payload = json.loads(
        render_validate_json(result.dataset, diagnostics, strict=False, path="x.inp")
    )
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["ok"] is False
    assert payload["command"] == "validate"
    assert "n_occasions" in payload["summary"]
    assert any(d["code"] == "MK001" for d in payload["diagnostics"])


def test_validate_json_ok_true_for_clean_file() -> None:
    result = parse_file(FIXTURES / "valid_single_group.inp")
    diagnostics = result.diagnostics + validate(result.dataset)
    payload = json.loads(
        render_validate_json(result.dataset, diagnostics, strict=False, path="x.inp")
    )
    assert payload["ok"] is True
