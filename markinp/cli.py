"""Command-line interface for markinp.

This module contains no domain logic. It parses arguments, calls library
functions, hands results to :mod:`markinp.report`, and sets the exit code.
Everything it does is doable in a few lines of Python via the library.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from . import __version__, report
from .build import BuildOptions, build_file
from .model import DataType, Diagnostic
from .parse import parse_file
from .validate import validate
from .write import write_file

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Read, validate, and build Program MARK encounter-history (.inp) files.",
)


def _parse_data_type(value: str | None) -> DataType | None:
    if value is None:
        return None
    try:
        return DataType(value.lower())
    except ValueError as exc:
        allowed = ", ".join(dt.value for dt in DataType)
        raise typer.BadParameter(f"unknown data type; choose one of: {allowed}") from exc


def _version_callback(show: bool) -> None:
    if show:
        typer.echo(f"markinp {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version", callback=_version_callback, is_eager=True, help="Show version and exit."
        ),
    ] = False,
) -> None:
    """markinp — a friendly linter and builder for MARK .inp files."""


@app.command(name="validate")
def validate_cmd(
    files: Annotated[
        list[Path],
        typer.Argument(help="One or more .inp files to validate.", exists=True, dir_okay=False),
    ],
    groups: Annotated[
        int | None, typer.Option("--groups", help="Assert the expected number of groups.")
    ] = None,
    occasions: Annotated[
        int | None, typer.Option("--occasions", help="Assert the expected history length.")
    ] = None,
    covariates: Annotated[
        int | None, typer.Option("--covariates", help="Assert the expected covariate count.")
    ] = None,
    data_type: Annotated[
        str | None, typer.Option("--data-type", help="Hint the data type for stricter checks.")
    ] = None,
    strict: Annotated[bool, typer.Option("--strict", help="Treat warnings as errors.")] = False,
    as_json: Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")] = False,
) -> None:
    """Validate one or more .inp files and report precise, actionable diagnostics.

    Exits non-zero if any file has an error, so it drops straight into CI and
    pre-commit. With several files, ``--json`` emits an array of per-file objects.
    """
    dtype = _parse_data_type(data_type)
    any_errors = False
    payloads: list[dict[str, object]] = []
    blocks: list[str] = []

    for file in files:
        result = parse_file(file)
        diagnostics = result.diagnostics + validate(
            result.dataset,
            groups=groups,
            occasions=occasions,
            covariates=covariates,
            data_type=dtype,
        )
        diagnostics.sort(key=lambda d: (d.line if d.line is not None else -1, d.code))
        if report.has_errors(diagnostics, strict):
            any_errors = True

        path = str(file)
        if as_json:
            payloads.append(
                report.validate_payload(result.dataset, diagnostics, strict=strict, path=path)
            )
        else:
            blocks.append(
                report.render_validate_human(result.dataset, diagnostics, strict=strict, path=path)
            )

    if as_json:
        output: object = payloads[0] if len(payloads) == 1 else payloads
        typer.echo(json.dumps(output, indent=2))
    else:
        typer.echo("\n\n".join(blocks))

    if any_errors:
        raise typer.Exit(1)


@app.command()
def inspect(
    file: Annotated[
        Path, typer.Argument(help="The .inp file to inspect.", exists=True, dir_okay=False)
    ],
    as_json: Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")] = False,
) -> None:
    """Summarize the inferred structure of an .inp file (read-only)."""
    result = parse_file(file)
    diagnostics = result.diagnostics + validate(result.dataset)
    path = str(file)
    if as_json:
        typer.echo(report.render_inspect_json(result.dataset, diagnostics, path=path))
    else:
        typer.echo(report.render_inspect_human(result.dataset, diagnostics, path=path))


@app.command()
def build(
    input_csv: Annotated[
        Path, typer.Argument(help="Tidy capture table (CSV).", exists=True, dir_okay=False)
    ],
    output: Annotated[Path, typer.Option("-o", "--output", help="Path to write the .inp file.")],
    fmt: Annotated[str, typer.Option("--format", help="Layout: long, wide, or auto.")] = "auto",
    id_col: Annotated[
        str | None, typer.Option("--id-col", help="Individual id column (long).")
    ] = None,
    occasion_col: Annotated[
        str | None, typer.Option("--occasion-col", help="Occasion column (long).")
    ] = None,
    detect_col: Annotated[
        str | None, typer.Option("--detect-col", help="0/1 detection column (long).")
    ] = None,
    history_col: Annotated[
        str | None, typer.Option("--history-col", help="Prebuilt history column (wide).")
    ] = None,
    group_col: Annotated[
        str | None, typer.Option("--group-col", help="Column defining groups.")
    ] = None,
    covariate_cols: Annotated[
        str | None, typer.Option("--covariate-cols", help="Comma-separated covariate columns.")
    ] = None,
    comment_col: Annotated[
        str | None, typer.Option("--comment-col", help="Column to write as /* comment */.")
    ] = None,
    collapse: Annotated[
        bool, typer.Option("--collapse/--no-collapse", help="Aggregate identical histories.")
    ] = True,
    as_json: Annotated[
        bool, typer.Option("--json", help="Emit a machine-readable build report.")
    ] = False,
) -> None:
    """Build a valid, deterministic .inp file from a tidy capture table."""
    opts = BuildOptions(
        fmt=fmt,
        id_col=id_col,
        occasion_col=occasion_col,
        detect_col=detect_col,
        history_col=history_col,
        group_col=group_col,
        covariate_cols=[c.strip() for c in covariate_cols.split(",")] if covariate_cols else [],
        comment_col=comment_col,
        collapse=collapse,
    )
    result = build_file(input_csv, opts)
    diagnostics: list[Diagnostic] = list(result.diagnostics)
    if result.dataset is not None:
        diagnostics += validate(result.dataset)
    diagnostics.sort(key=lambda d: (d.line if d.line is not None else -1, d.code))

    wrote = False
    if result.dataset is not None and not report.has_errors(diagnostics):
        write_file(result.dataset, output)
        wrote = True

    if as_json:
        typer.echo(_build_json(result, diagnostics, str(output), wrote))
    else:
        typer.echo(_build_human(result, diagnostics, str(output), wrote))

    if not wrote:
        raise typer.Exit(1)


def _build_human(result, diagnostics, output: str, wrote: bool) -> str:  # type: ignore[no-untyped-def]
    lines = [f"markinp build -> {output}", ""]
    n_records = len(result.dataset.records) if result.dataset else 0
    lines.append(f"Read {result.n_rows} row(s); produced {n_records} record(s).")
    if diagnostics:
        lines.append("")
        for diag in diagnostics:
            lines.append(report._format_diagnostic(diag, strict=False))
    lines.append("")
    lines.append(f"Wrote {output}" if wrote else "Refused to write: fix the errors above.")
    return "\n".join(lines)


def _build_json(result, diagnostics, output: str, wrote: bool) -> str:  # type: ignore[no-untyped-def]
    payload = {
        "schema_version": report.SCHEMA_VERSION,
        "command": "build",
        "output": output,
        "written": wrote,
        "rows_read": result.n_rows,
        "records": len(result.dataset.records) if result.dataset else 0,
        "diagnostics": [report._diag_to_dict(d, strict=False) for d in diagnostics],
    }
    return json.dumps(payload, indent=2)


if __name__ == "__main__":
    app()
