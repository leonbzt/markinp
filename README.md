# markinp

[![CI](https://github.com/leonbzt/markinp/actions/workflows/ci.yml/badge.svg)](https://github.com/leonbzt/markinp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/markinp.svg)](https://pypi.org/project/markinp/)
[![Python versions](https://img.shields.io/pypi/pyversions/markinp.svg)](https://pypi.org/project/markinp/)
[![Docs](https://img.shields.io/badge/docs-mkdocs--material-blue.svg)](https://leonbzt.github.io/markinp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21145090.svg)](https://doi.org/10.5281/zenodo.21145090)

**Read, validate, and build Program MARK encounter-history (`.inp`) files —
with error messages that actually tell you what to fix.**

`markinp` removes the most common friction in the capture–recapture workflow:
hand-building `.inp` files in a text editor or Excel, and only discovering
formatting mistakes when MARK rejects the file with an unhelpful message.

It does three things and nothing more:

1. **validate** an existing `.inp` file and report precise, actionable errors;
2. **inspect** an `.inp` file and summarize its structure;
3. **build** a valid `.inp` file from a tidy capture table (CSV).

> **Disclaimer.** `markinp` is an independent, unofficial utility. It is **not**
> affiliated with, endorsed by, or maintained by the authors of Program MARK or
> RMark. "MARK" is referenced only to describe the file format it interoperates
> with. `markinp` never fits models or computes statistics — it does file I/O
> and validation only.

> **Note on the name.** The command and PyPI package are `markinp` (the name
> `markio` was already taken on PyPI).

---

## Install

```bash
pip install markinp
```

## 60-second quickstart

Validate a file you already have:

```bash
markinp validate captures.inp
```

```
markinp validate captures.inp

Structure: 4 occasions, 2 groups, 1 covariate, live_recapture
Records:   3   Individuals: 7

Summary: 0 errors, 0 warnings, 0 infos  ->  PASS
```

When something is wrong, you get the line and the fix — not a traceback:

```
  MK001  ERROR   line 12: record is not terminated by a semicolon
           hint: Add a ';' at the end of this line to close the record ...
```

Inspect the inferred structure:

```bash
markinp inspect captures.inp
```

Build an `.inp` from a tidy CSV:

```bash
# long format: one row per (individual x occasion)
markinp build captures.csv -o out.inp \
    --id-col id --occasion-col occasion --detect-col detected \
    --group-col sex --covariate-cols weight
```

Validate many files at once (exits non-zero if *any* fail):

```bash
markinp validate data/*.inp --strict
```

Every command accepts `--json` for machine-readable output and exits non-zero
when errors are found, so `markinp validate` drops straight into CI.

## Guard a pipeline (CI & pre-commit)

**GitHub Action** — fail a build when any `.inp` file is malformed:

```yaml
# .github/workflows/validate-inp.yml
name: Validate .inp
on: [push, pull_request]
jobs:
  markinp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: leonbzt/markinp@v0
        with:
          files: "data/**/*.inp"
          args: "--strict"
```

**pre-commit hook** — validate `.inp` files before every commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/leonbzt/markinp
    rev: v0.1.0
    hooks:
      - id: markinp-validate
```

## Use it as a library

The CLI is a thin wrapper; everything is importable:

```python
from markinp import parse_text, validate

result = parse_text("1001 1;\n0101 2;\n")
for diag in validate(result.dataset):
    print(diag.code, diag.message)
```

## The `.inp` format in one minute

Each record is one line ending in `;`. Whitespace separates the fields:

```
[/* comment */]  HISTORY  FREQ_1 [FREQ_2 ...]  [COV_1 ...]  ;  [/* comment */]
```

- **HISTORY** — one character per sampling occasion (`1` = detected, `0` = not).
- **FREQ** — one integer count **per group**; may be negative for losses on
  capture.
- **COV** — optional numeric individual covariates (no missing values allowed).

```
/* ind 001 */ 1001 1 0 10.2;
/* ind 002 */ 1101 0 2 9.5;
0101 3 1 8.1;
```

The number of occasions, groups, and covariates is usually **not** stored in the
file, so `markinp` infers it. Tighten the checks by asserting what you expect:

```bash
markinp validate captures.inp --occasions 4 --groups 2 --covariates 1
```

## Error codes

Every problem is reported as a stable, documented diagnostic code (`MK001` …).
See [`docs/error-codes.md`](docs/error-codes.md) for the full reference.
Highlights:

| Code  | Meaning |
|-------|---------|
| MK001 | Record not terminated by `;` |
| MK002 | History length differs between records |
| MK004 | Wrong number of frequency columns for the group count |
| MK007 | Missing / non-numeric covariate |
| MK011 | All-zero history (warning) |
| MK012 | Negative frequency — loss on capture (warning) |
| MK900 | Specialized format detected; only partially validated (info) |

`--strict` promotes warnings to errors. Exit code is `0` when there are no
errors and `1` otherwise.

## Scope

v0 fully supports the **standard 0/1 encounter-history format** (live recapture /
CJS / Jolly-Seber / closed captures). Known-fate, dead-recovery (Brownie), and
multistrata formats are **detected and structurally checked only** (see `MK900`);
full support is a later milestone. `markinp` will always tell you honestly when
it can only partially validate a file.

## Development

```bash
pip install -e ".[dev]"
ruff check .
mypy markinp
pytest
```

## Testing

The suite includes a fixture that triggers **every** diagnostic code, round-trip
(`parse → write → parse`) stability checks, and `build → validate` round-trips.

To try it on real data, point `markinp` at a folder of `.inp` files:

```bash
markinp validate path/to/*.inp        # batch validate; exits 1 if any fail
markinp inspect path/to/one.inp       # summarize inferred structure
```

A local `sample_data/` folder of third-party MARK example files is **not** part
of this repository (licensing), but is handy as a regression corpus — running
`markinp validate sample_data/*.inp` over it is a quick way to smoke-test a
change against a wide variety of real files. Note that occupancy, false-positive,
robust-design, and multistrata files are outside v0's standard-format scope and
will be flagged accordingly (see [`docs/error-codes.md`](docs/error-codes.md)).

## Citation

If markinp helps your work, please cite it. The concept DOI below always
resolves to the latest version; see [`CITATION.cff`](CITATION.cff) for full
metadata (and the version-specific DOI).

> Botzenhardt, L. *markinp: read, validate, and build Program MARK
> encounter-history (.inp) files*. https://doi.org/10.5281/zenodo.21145090

## License

MIT — see [`LICENSE`](LICENSE).
