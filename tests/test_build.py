"""Tests for the builder: long/wide readers, groups, covariates, collapse."""

from __future__ import annotations

from markinp.build import BuildOptions, build_dataset, build_file
from markinp.model import Severity
from markinp.validate import validate

from .conftest import FIXTURES


def _errors(diagnostics: list) -> list:  # type: ignore[type-arg]
    return [d for d in diagnostics if d.severity == Severity.ERROR]


def test_build_long_produces_valid_dataset() -> None:
    opts = BuildOptions(
        id_col="id",
        occasion_col="occasion",
        detect_col="detected",
        group_col="sex",
        covariate_cols=["weight"],
    )
    result = build_file(FIXTURES / "captures_long.csv", opts)
    assert result.dataset is not None
    # build -> validate must be clean.
    assert _errors(result.diagnostics + validate(result.dataset)) == []
    assert result.dataset.n_groups == 2
    assert result.dataset.n_covariates == 1
    assert result.dataset.n_occasions == 3


def test_build_long_histories_are_correct() -> None:
    opts = BuildOptions(
        id_col="id",
        occasion_col="occasion",
        detect_col="detected",
        group_col="sex",
        covariate_cols=["weight"],
    )
    dataset = build_file(FIXTURES / "captures_long.csv", opts).dataset
    assert dataset is not None
    histories = {r.history for r in dataset.records}
    assert histories == {"101", "011"}


def test_build_wide_matches_long() -> None:
    wide = build_file(
        FIXTURES / "captures_wide.csv",
        BuildOptions(fmt="wide", group_col="sex", covariate_cols=["weight"]),
    ).dataset
    long = build_file(
        FIXTURES / "captures_long.csv",
        BuildOptions(
            id_col="id",
            occasion_col="occasion",
            detect_col="detected",
            group_col="sex",
            covariate_cols=["weight"],
        ),
    ).dataset
    assert wide is not None and long is not None
    assert {r.history for r in wide.records} == {r.history for r in long.records}


def test_collapse_sums_identical_histories() -> None:
    csv = "id,o1,o2\nA,1,0\nB,1,0\nC,0,1\n"
    dataset = build_dataset(csv, BuildOptions(fmt="wide", collapse=True)).dataset
    assert dataset is not None
    by_history = {r.history: r.frequencies for r in dataset.records}
    assert by_history["10"] == [2]
    assert by_history["01"] == [1]


def test_no_collapse_keeps_rows_separate() -> None:
    csv = "id,o1,o2\nA,1,0\nB,1,0\n"
    dataset = build_dataset(csv, BuildOptions(fmt="wide", collapse=False)).dataset
    assert dataset is not None
    assert len(dataset.records) == 2


def test_missing_covariate_cell_is_reported() -> None:
    csv = "id,o1,o2,mass\nA,1,0,\nB,0,1,3.2\n"
    result = build_dataset(csv, BuildOptions(fmt="wide", covariate_cols=["mass"]))
    assert "MK007" in {d.code for d in result.diagnostics}


def test_empty_csv_reports_no_records() -> None:
    result = build_dataset("id,o1,o2\n", BuildOptions(fmt="wide"))
    assert "MK008" in {d.code for d in result.diagnostics}


def test_long_without_required_columns_is_reported() -> None:
    csv = "id,occasion,detected\nA,1,1\n"
    result = build_dataset(csv, BuildOptions(fmt="long"))
    assert _errors(result.diagnostics)
