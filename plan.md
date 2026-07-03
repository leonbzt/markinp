# plan.md — markio development plan

A small utility for reading, validating, and building Program MARK
encounter-history (`.inp`) files. See `CLAUDE.md` for rules and the format
primer. This file is the scope and the roadmap.

---

## 1. Vision

Make the two worst moments in the MARK workflow painless:

- **"MARK rejected my file and I don't know why."** → `markio validate` gives a
  precise, line-numbered, actionable diagnosis in one second.
- **"I have a capture spreadsheet and need an `.inp`."** → `markio build`
  produces a valid `.inp` from a tidy CSV, correctly handling groups,
  covariates, frequencies, and comments.

Success looks like this being **the first thing a MARK user runs** on a new
data file, and something they can drop into CI to guard a pipeline.

---

## 2. Scope

### v0 IS
- Validate the standard 0/1 encounter-history format (live recapture / CJS /
  Jolly-Seber / closed captures) with a rich set of diagnostics.
- Inspect an `.inp`: summarize inferred structure.
- Build an `.inp` from a tidy CSV (long or wide layout).
- Human-readable output by default; `--json` and CI-friendly exit codes.
- Cross-platform (incl. Windows/CRLF) and installable via pip.

### v0 IS NOT
- **No** model fitting or statistics of any kind.
- **No** full support for known-fate, dead-recovery (Brownie), or multistrata
  formats (detected and structurally checked only; flagged as partial).
- **No** GUI or web app.
- **No** direct MARK/RMark execution.
- **No** output/results parsing yet (that is v1).

---

## 3. v0 success criteria

> **Note:** the shipped command/package is `markinp` (`markio` was taken on
> PyPI). The examples below read `markinp` in the built tool.

- [x] `markinp validate good.inp` exits 0 with a clean summary.
- [x] `markinp validate broken.inp` names the exact line and fix for each of the
      v0 error codes below, and exits 1.
- [x] `markinp inspect file.inp` reports occasions, groups, covariates, number of
      histories, number of individuals, and a data-type guess.
- [x] `markinp build captures.csv -o out.inp` produces a file that
      `markinp validate` passes with zero errors.
- [x] `--json` works on all commands and is documented with a schema version.
- [ ] Installs via `pip install markinp`; CI green on Linux/macOS/Windows.
      (CI workflow written; not yet run on the matrix / published.)
- [x] README with a 60-second quickstart; `CITATION.cff` present.

---

## 4. Data model (`model.py`)

```
Severity        = enum(ERROR, WARNING, INFO)

DataType        = enum(LIVE_RECAPTURE, CLOSED_CAPTURES, KNOWN_FATE,
                       DEAD_RECOVERY, MULTISTRATA, UNKNOWN)

EncounterHistory:
    history:      str            # e.g. "1001"
    frequencies:  list[int]      # one per group; may be negative (losses)
    covariates:   list[float]    # length = n_covariates; no missing values
    comment:      str | None
    line:         int            # source line for diagnostics

Dataset:
    n_occasions:  int
    n_groups:     int
    n_covariates: int
    group_labels: list[str] | None
    cov_labels:   list[str] | None
    data_type:    DataType
    records:      list[EncounterHistory]

Diagnostic:                       # see CLAUDE.md §7 for the frozen contract
    code, severity, message, hint, line, col
```

---

## 5. CLI specification

Three commands in v0. All accept `--json` and return exit code 0 (no errors)
or 1 (errors present). `--strict` promotes warnings to errors.

### `markio validate`
```
markio validate FILE.inp
    [--groups N]        assert expected number of groups
    [--occasions N]     assert expected history length
    [--covariates N]    assert expected covariate count
    [--data-type TYPE]  hint the data type for better checks
    [--strict]          treat warnings as errors
    [--json]
```
Reads the file, infers structure, runs all diagnostics, prints a report.
If any `--groups/--occasions/--covariates` are given, mismatches become errors.

### `markio inspect`
```
markio inspect FILE.inp [--json]
```
Prints: inferred occasions, groups, covariates, #records, #individuals
(sum of |frequencies|), detected data type, and any structural warnings.
Read-only; always exits 0 unless the file cannot be read.

### `markio build`
```
markio build INPUT.csv -o OUTPUT.inp
    [--format long|wide]        default: auto-detect
    [--id-col NAME]             individual id (long format)
    [--occasion-col NAME]       occasion index/label (long format)
    [--detect-col NAME]         0/1 detection (long format)
    [--history-col NAME]        prebuilt history string (wide alt)
    [--group-col NAME]          column defining groups
    [--covariate-cols A,B,...]  numeric covariate columns
    [--collapse / --no-collapse]  aggregate identical histories (default: on)
    [--comment-col NAME]        write /* value */ per record
    [--json]                    emit a build report
```
Reads a tidy capture table and writes a valid, deterministic `.inp`.
- **long** format: one row per (individual × occasion) with a detection flag.
- **wide** format: one row per individual, either occasion columns or a
  prebuilt `history` column.
After writing, `build` internally validates its own output and refuses to write
a file that would not pass `validate` (reporting why instead).

### Example CSVs

Long:
```
id,occasion,detected,sex,weight
A1,1,1,M,10.2
A1,2,0,M,10.2
A1,3,1,M,10.2
```

Wide:
```
id,o1,o2,o3,sex,weight
A1,1,0,1,M,10.2
```

---

## 6. Error taxonomy (v0)

Codes are **stable once released** — never renumber. Severities: E=error,
W=warning, I=info. `--strict` promotes W→E.

| Code  | Sev | Trigger | Hint given to user |
|-------|-----|---------|--------------------|
| MK001 | E | Record not terminated by `;` | Add a semicolon at the end of the line |
| MK002 | E | History length differs between records | All histories must have one character per occasion; check line N |
| MK003 | E | Non-numeric value in a frequency column | Frequencies must be whole numbers; check for stray text/space |
| MK004 | E | Frequency-column count ≠ inferred/declared groups | Give one frequency per group; check for a missing or extra value |
| MK005 | E | Non-`0`/`1` char in history when the file is (asserted) standard | Standard histories use only `0`/`1`; pass `--data-type` for other formats |
| MK006 | E | Covariate count differs between records | Every record needs the same number of covariates |
| MK007 | E | Missing covariate value | Covariates cannot be blank in MARK; fill or remove the covariate |
| MK008 | E | File has no encounter records | The file is empty or all comments; add data |
| MK009 | E | Unterminated `/* ... */` comment | Close the comment with `*/` |
| MK010 | E | History length ≠ asserted `--occasions` | Expected X occasions but found Y on line N |
| MK011 | W | All-zero history present | An all-zero history is usually invalid for this model; verify |
| MK012 | W | Negative frequency (losses on capture) | Valid only as a loss-on-capture; confirm this is intended |
| MK013 | I | Identical histories not collapsed | These rows could be aggregated with a frequency count |
| MK014 | E | Non-integer frequency (e.g. `1.5`) | Frequencies must be integers |
| MK015 | W | Content after the `;` that is not a comment | Move it before the semicolon or wrap it in `/* */` |
| MK016 | I | Mixed tabs and spaces between fields | Harmless, but consistent whitespace is cleaner |
| MK017 | E | Multistrata state char not in strata set | (multistrata) Use only declared strata letters |
| MK018 | E | Odd column count for LDLD pairing | (known-fate/recovery) histories must be in Live/Dead pairs |
| MK019 | W | A declared group has all-zero frequencies | Group G has no individuals; check group setup |
| MK020 | W | Unexpected encoding / BOM / non-ASCII | Save as UTF-8 or ASCII; a BOM/odd byte was found |
| MK900 | I | Partial support: specialized format detected (multistrata, or a non-`0`/`1` alphabet — occupancy/false-positive/robust-design) | Full validation of this format is not yet implemented |

Add new codes here **before** implementing them.

---

## 7. Milestones

### M0 — Scaffold
- [x] `pyproject.toml` (hatchling), package skeleton, `[project.scripts] markinp = "markinp.cli:app"`.
- [x] Ruff + mypy + pytest config.
- [x] GitHub Actions CI matrix (Linux/macOS/Windows × 3.10–3.13).
- [x] `LICENSE` (MIT), `README.md`, `CITATION.cff`, `.gitignore`, `CHANGELOG.md`.
- [ ] Commit `CLAUDE.md` and `plan.md`. (Repo init pending user go-ahead.)

### M1 — Parser + data model
- [x] `model.py` dataclasses.
- [x] `parse.py`: tokenize records, handle comments, whitespace, CRLF, BOM;
      capture line numbers; produce a `Dataset` plus low-level parse diagnostics.
- [x] Fixtures: a handful of valid `.inp` files (single group, multi-group,
      with covariates, with comments).
- [x] Round-trip stub: `parse` then re-`parse` is stable.

### M2 — Validator
- [x] `validate.py` implementing MK001–MK020 (+ MK900 detection).
- [x] `report.py`: human renderer + `--json` (schema_version 1).
- [x] Exit-code logic and `--strict`.
- [x] One failing fixture per code; assert exact codes; assert clean files are clean.
- [x] `markinp validate` wired in `cli.py`.

### M3 — Inspect
- [x] `inspect` summary (occasions, groups, covariates, #records, #individuals,
      data-type guess).
- [x] Human + JSON output; tests.

### M4 — Builder
- [x] `build.py`: long and wide readers (stdlib `csv`), auto-detect layout.
- [x] Group handling, covariate handling, comment column, collapse logic.
- [x] `write.py`: deterministic `.inp` writer.
- [x] `build` self-validates its output before writing.
- [x] Round-trip test: `build -> validate` yields zero errors; sample datasets.

### M5 — Release
- [x] README quickstart + examples; document every error code (`docs/error-codes.md`).
- [x] PyPI publish via Trusted Publishing GitHub Action (`.github/workflows/release.yml`).
      (Workflow ready; fires on the `v*` tag once the PyPI pending publisher is set up.)
- [x] Bioconda recipe (`conda-recipe/meta.yaml`); submit after the sdist is on PyPI (fill sha256).
- [x] Ship a reusable GitHub Action (`action.yml`) + a pre-commit hook (`.pre-commit-hooks.yaml`).
- [x] Tag `v0.1.0`.

---

## 8. Test plan

- Unit tests per module (`parse`, `validate`, `build`, `write`, `report`).
- Fixture corpus: tiny valid files + one invalid file per diagnostic code.
- Round-trip: `parse->write->parse` stable; `build->validate` clean.
- CLI snapshot tests for human and JSON output.
- Optional: `hypothesis` to fuzz histories/frequencies for round-trip stability.
- Coverage target: 90%+ on the library modules.

---

## 9. Distribution plan

- **PyPI** first (Trusted Publishing; no API tokens in the repo).
- **Bioconda** recipe once the API is stable at v0.1.0.
- **GitHub Action** wrapper so `markio validate` can gate other repos' CI.
- **pre-commit** hook example in the README.
- `CITATION.cff` + semantic versioning; keep a `CHANGELOG.md` from v0.1.0.

---

## 10. Roadmap beyond v0

- **Shipped (v0.2+) — In-browser validator.** A client-side page
  (`docs/validator.html`) that runs the library in the browser via Pyodide/WASM.
  Zero install, no server, data stays on the user's device. Reuses
  `parse`/`validate`/`report` unchanged (see CLAUDE.md rule 9).
- **v0.3 (short–mid term, prioritized) — Occupancy.** First-class support for the
  occupancy / detection-history format used by the `unmarked` (R) and PRESENCE
  community — a larger and faster-growing audience than pure capture-recapture
  (driven by camera traps, eDNA, bioacoustics). Detect `.` (not-surveyed) and
  multi-state detections, validate structurally, and build from a tidy CSV. This
  is a committed direction, not a "maybe".
- **v1 — Output tidier.** Parse MARK results into tidy tables (real/beta
  estimates, model list, AICc). Higher-uncertainty parsing; scope after v0.
- **v1 — `convert`.** Round-trip `.inp` ⇄ tidy CSV, including an RMark-style
  dataframe export (mirrors RMark's `convert.inp`, no R needed, both directions).
- **v2 — Specialized formats.** Full known-fate (LDLD), dead-recovery (Brownie),
  and multistrata support, promoting MK900 detections to full checks.

---

## 11. Open decisions (resolve early, record the answer here)

- [ ] **Package name.** Confirm `markio` is free on PyPI and conda-forge/Bioconda;
      pick a fallback (e.g. `markinp`, `inpkit`) if not.
leon: markio is already taken, use "markinp"
- [ ] **pandas or stdlib** for CSV reading in `build`. Default: stdlib `csv` to
      keep installs light; revisit only if reshaping gets painful.
leon: okay
- [ ] **Data-type inference vs assertion.** How much to infer automatically vs.
      require the user to declare via `--data-type`. Default: infer, let flags
      tighten.
leon: infer, flags tighten
- [x] **JSON schema versioning.** Confirm the shape of the `--json` object and
      freeze `schema_version: 1`.

 leon: not sure
 resolved: frozen at `schema_version: 1`. Shape:
   `{schema_version, command, file, ok, summary{...structure..., errors, warnings,
   infos}, diagnostics:[{code, severity, message, hint, line, col}]}`.
   `inspect` omits `ok` and error-severity diagnostics; `build` uses
   `{schema_version, command, output, written, rows_read, records, diagnostics}`.
- [ ] **License.** Confirm MIT (permissive helps adoption and packaging).
leon: ok
