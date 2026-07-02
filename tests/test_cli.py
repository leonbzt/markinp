"""End-to-end tests for the CLI via Typer's test runner."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from markinp.cli import app

from .conftest import FIXTURES

runner = CliRunner()


def test_validate_clean_file_exits_zero() -> None:
    result = runner.invoke(app, ["validate", str(FIXTURES / "valid_single_group.inp")])
    assert result.exit_code == 0
    assert "PASS" in result.stdout


def test_validate_broken_file_exits_one_and_names_code() -> None:
    result = runner.invoke(app, ["validate", str(FIXTURES / "missing_semicolon.inp")])
    assert result.exit_code == 1
    assert "MK001" in result.stdout


def test_validate_json_output() -> None:
    result = runner.invoke(app, ["validate", str(FIXTURES / "valid_single_group.inp"), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == 1


def test_validate_multiple_files_fails_if_any_fails() -> None:
    result = runner.invoke(
        app,
        [
            "validate",
            str(FIXTURES / "valid_single_group.inp"),
            str(FIXTURES / "missing_semicolon.inp"),
        ],
    )
    assert result.exit_code == 1
    assert "MK001" in result.stdout


def test_validate_multiple_files_json_is_an_array() -> None:
    result = runner.invoke(
        app,
        [
            "validate",
            str(FIXTURES / "valid_single_group.inp"),
            str(FIXTURES / "valid_multi_group.inp"),
            "--json",
        ],
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert isinstance(payload, list)
    assert len(payload) == 2


def test_strict_promotes_warning_to_failure() -> None:
    warn_file = str(FIXTURES / "negative_frequency.inp")
    assert runner.invoke(app, ["validate", warn_file]).exit_code == 0
    assert runner.invoke(app, ["validate", warn_file, "--strict"]).exit_code == 1


def test_inspect_exits_zero_and_reports_structure() -> None:
    result = runner.invoke(app, ["inspect", str(FIXTURES / "valid_multi_group.inp")])
    assert result.exit_code == 0
    assert "groups:" in result.stdout


def test_build_writes_a_file_that_validates(tmp_path: Path) -> None:
    out = tmp_path / "out.inp"
    result = runner.invoke(
        app,
        [
            "build",
            str(FIXTURES / "captures_long.csv"),
            "-o",
            str(out),
            "--id-col",
            "id",
            "--occasion-col",
            "occasion",
            "--detect-col",
            "detected",
            "--group-col",
            "sex",
            "--covariate-cols",
            "weight",
        ],
    )
    assert result.exit_code == 0
    assert out.exists()
    # The written file passes validate with no errors.
    check = runner.invoke(app, ["validate", str(out)])
    assert check.exit_code == 0


def test_build_refuses_to_write_invalid_output(tmp_path: Path) -> None:
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("id,o1,o2,mass\nA,1,0,\n", encoding="utf-8")
    out = tmp_path / "out.inp"
    result = runner.invoke(
        app,
        ["build", str(bad_csv), "-o", str(out), "--covariate-cols", "mass"],
    )
    assert result.exit_code == 1
    assert not out.exists()


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "markinp" in result.stdout
