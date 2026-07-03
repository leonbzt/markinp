# CLAUDE.md

Guidance for Claude Code (and any AI assistant) working in this repository.
Read this file **and** `plan.md` before making changes. `plan.md` holds the
scope, milestones, and the full error taxonomy; this file holds the rules,
the domain primer, and the commands.

---

## 1. What this project is

`markio` is a small, well-tested command-line utility and Python library for
**reading, validating, and building Program MARK encounter-history (`.inp`)
files**. It removes the most common friction in the capture-recapture
workflow: hand-building `.inp` files in a text editor or Excel, and discovering
formatting mistakes only when MARK rejects the file with an unhelpful message.

It does **three** things and nothing more:

1. **validate** an existing `.inp` file and report precise, actionable errors.
2. **inspect** an `.inp` file and summarize its structure.
3. **build** a valid `.inp` file from a tidy capture table (CSV).

Target users: wildlife ecologists, conservation biologists, and fisheries
scientists who use Program MARK (directly or via RMark). Most are not
programmers. **UX and error-message quality are the product**, not an add-on.

> **Disclaimer to preserve in the README:** `markio` is an independent,
> unofficial utility. It is not affiliated with, endorsed by, or maintained by
> the authors of Program MARK or RMark. "MARK" is referenced only to describe
> the file format it interoperates with.

---

## 2. Golden rules (non-negotiable)

1. **Never reimplement MARK's statistics.** This tool does file I/O and
   validation only. No model fitting, no likelihoods, no estimation. Ever.
2. **Library-first.** Every capability lives in an importable function with a
   clean signature and type hints. The CLI is a thin wrapper over the library
   so that RMark users and pipelines can call the same code from Python.
3. **Errors are the product.** Every problem is reported as a structured
   *diagnostic* with a stable code, a severity, the line number, a plain-English
   message, and an actionable hint. Never raise a raw traceback at the user.
4. **Never silently change a user's data.** Report a diagnostic; only modify
   data when the user explicitly asks (e.g. `--fix`, `--collapse`). Silent
   "helpful" reinterpretation is forbidden — it is the exact failure mode we
   are replacing.
5. **Deterministic output.** Given the same input, output bytes are identical.
   Sort predictably. This keeps diffs clean and makes CI usable.
6. **Two output modes, always.** Human-readable by default; `--json` for
   machines. Exit non-zero when errors are found so the tool works in CI.
7. **Keep dependencies minimal.** It must install cleanly on Linux, macOS, and
   Windows and be packageable for Bioconda. Prefer the standard library. Do not
   add a heavy dependency without recording the reason in `plan.md`.
8. **Respect the spec exactly.** When unsure about the `.inp` format, consult
   Chapter 2 of the MARK "Gentle Introduction" book (the field's canonical
   reference) and encode the rule as a test rather than guessing.
9. **No native GUI app; no server backend.** The command line and library are
   the primary interfaces. A browser-based validator is permitted **only** as a
   thin, client-side presentation layer over the same library (compiled to WASM
   via Pyodide): it must add no validation logic of its own, run entirely in the
   user's browser, and send no data to any server. It reuses `parse`/`validate`/
   `report` unchanged — if the web tool needs logic the library lacks, that logic
   belongs in the library, not the page.

---

## 3. MARK `.inp` format primer (authoritative for this repo)

An `.inp` file is a plain-text file. Each record is one line, terminated by a
semicolon. Fields are separated by whitespace (spaces or tabs).

**Grammar of one record:**

```
[/* comment */]  HISTORY  FREQ_1 [FREQ_2 ... FREQ_g]  [COV_1 ... COV_c]  ;  [/* comment */]
```

- **HISTORY** — the encounter history, one character per sampling occasion.
  For the standard format: `1` = detected/captured, `0` = not.
- **FREQ_1 … FREQ_g** — one integer frequency **per group** `g`. The frequency
  is the count of individuals sharing this history in that group. A record for
  a single individual uses `1` in its group's column and `0` in the others.
  Frequencies may be **negative** to denote losses on capture (removals).
- **COV_1 … COV_c** — optional numeric individual covariates, `c` of them.
  **Covariates cannot have missing values.**
- **`;`** — terminates the record. **The single most common user error is a
  missing semicolon.**
- **Comments** are delimited by `/* ... */` and may appear anywhere; they are
  frequently used at the start of a line to label the individual.

**Worked example** — 2 groups (e.g. Male/Female) and 1 covariate (weight):

```
/* ind 001 */ 1001 1 0 10;
/* ind 002 */ 1101 0 2 5;
0101 3 1 6;
```

Record 1: history `1001`, group-1 freq `1`, group-2 freq `0`, covariate `10`.
Record 2: history `1101`, group-1 freq `0`, group-2 freq `2`, covariate `5`.
Record 3: history `0101`, group-1 freq `3`, group-2 freq `1`, covariate `6`.

**Cross-record invariants:**

- Every HISTORY must have the **same length** (= number of occasions).
- Every record must have the **same number of frequency columns** (= number of
  groups) and the **same number of covariate columns**.
- The data type, number of occasions, groups, covariates, and strata are set by
  the user when the MARK project is created; they are usually **not** stored in
  the file itself. `markio` therefore *infers* them and lets the user assert
  expected values with flags for stricter checking.

**Data types (scope note):**

- v0 fully supports the **standard 0/1 encounter-history format** used by live
  recapture (CJS / Jolly-Seber) and closed-captures models. This is the same
  subset RMark's `convert.inp` handles.
- **Known-fate** and **dead-recovery (Brownie)** use paired `LDLD…` columns;
  **multistrata** uses letters for states. v0 should *detect* these and validate
  what it safely can (structural checks), but full support is a later milestone.
  Do not pretend to fully validate a format we have not implemented — say so in
  a diagnostic.

**Encoding & line endings:** MARK is a Windows-origin tool and input often comes
from Excel, so files are commonly UTF-8 or Latin-1 with CRLF line endings, and
may carry a BOM. Read robustly; normalize internally; flag odd encodings.

---

## 4. Architecture

Keep the library and the CLI strictly separated.

```
markio/
  __init__.py       # version, public API re-exports
  model.py          # dataclasses: Dataset, EncounterHistory, DataType, Diagnostic, Severity
  parse.py          # .inp text -> Dataset (the reader/decoder); tracks line numbers
  validate.py       # Dataset (+ optional asserted params) -> list[Diagnostic]
  build.py          # tidy CSV (long/wide) -> Dataset (the builder)
  write.py          # Dataset -> .inp text (the encoder), deterministic
  report.py         # render list[Diagnostic] as human text or JSON
  cli.py            # Typer app; thin wrappers that call the functions above
tests/
  fixtures/         # small valid and invalid .inp files, one concern each
  ...
```

**Rule:** `cli.py` contains no domain logic. It parses arguments, calls library
functions, and hands results to `report.py`. Anything the CLI can do must be
doable in three lines of Python via the library.

---

## 5. Tech stack & commands

- **Language:** Python 3.10+ (use modern typing: `list[str]`, `X | None`).
- **CLI:** [Typer](https://typer.tiangolo.com/) (auto-generates `--help`).
- **Core parsing/building:** standard library only (`csv`, `io`, `re`).
  Do not require pandas in the core. (A pandas convenience layer at the CLI
  edge is allowed only if justified in `plan.md`.)
- **Tests:** pytest. Optional `hypothesis` for round-trip property tests.
- **Lint + format:** [Ruff](https://docs.astral.sh/ruff/) (does both).
- **Type check:** mypy (strict) or pyright.
- **Build backend:** hatchling, via `pyproject.toml`.

Standard commands (assume a virtualenv; keep these working):

```bash
pip install -e ".[dev]"     # install package + dev extras
ruff format .               # format
ruff check . --fix          # lint
mypy markio                 # type check
pytest -q                   # run tests
markio --help               # smoke-test the CLI
```

CI must run `ruff check`, `mypy`, and `pytest` on a matrix of
{Linux, macOS, Windows} × {3.10, 3.11, 3.12, 3.13}. Windows is not optional —
our users are on Windows and our files carry CRLF.

---

## 6. Coding conventions

- Type-hint every function. No untyped public functions.
- Prefer small pure functions. Parsing returns data; it does not print.
- No bare `except:`. Catch specific exceptions and convert to diagnostics.
- User-facing strings are plain, specific, and kind. A good message names the
  line, says what is wrong, and says what to do. Example:
  `line 12: record has 3 frequency columns but the file uses 2 groups — remove one value or check for a stray space before the semicolon`.
- Docstrings on every public function: one-line summary, args, returns, and a
  tiny example where it helps.
- Keep functions under ~40 lines where reasonable; if a function grows a
  branch per diagnostic, that is a signal to move the rule into `validate.py`.

---

## 7. The diagnostic contract

All problems flow through one type (see `model.py`):

```python
@dataclass(frozen=True)
class Diagnostic:
    code: str          # stable, e.g. "MK001"
    severity: Severity # ERROR | WARNING | INFO
    message: str       # what is wrong, in plain English
    hint: str          # what to do about it
    line: int | None   # 1-based source line, when known
    col: int | None = None
```

- Codes are stable and documented in `plan.md`. Never renumber a released code.
- `validate()` returns `list[Diagnostic]`; it never exits or prints.
- `report.py` decides presentation. Exit codes: `0` if no ERROR-severity
  diagnostics, `1` if any ERROR. `--strict` promotes WARNING to ERROR.
- `--json` emits a versioned object: `{"schema_version": 1, "diagnostics": [...], "summary": {...}}`.

---

## 8. Testing rules

- **Every diagnostic code has at least one fixture** that triggers it and a
  test asserting the exact code appears (and clean files do not trigger it).
- **Round-trip tests:** `parse -> write -> parse` must be stable; and
  `build -> validate` on generated files must produce zero errors.
- Fixtures live in `tests/fixtures/`, are tiny, and target one concern each.
  Name them by intent, e.g. `missing_semicolon.inp`, `ragged_history.inp`.
- Prefer golden-file / snapshot tests for CLI output so UX regressions are
  caught.
- A change to parsing or a format rule is not complete without a test.

---

## 9. What NOT to do

- Do not add model fitting, estimation, or anything statistical.
- Do not "auto-correct" a file unless the user passed an explicit fix flag.
- Do not invent format rules — verify against Chapter 2 of the MARK book.
- Do not break determinism (no unsorted sets in output, no timestamps in files).
- Do not add a dependency for convenience; justify every one in `plan.md`.
- Do not claim full validation of known-fate / dead-recovery / multistrata
  until those milestones land; emit an honest "partial support" diagnostic.
- Do not build a native GUI app or a server backend. (A client-side, in-browser
  validator that merely calls the library — no server, no new logic — is allowed;
  see rule 9.)

---

## 10. Distribution (keep these paths open from day one)

- Publish to **PyPI** via GitHub Actions Trusted Publishing.
- Then submit a **Bioconda** recipe (our users install via conda).
- Ship a **GitHub Action** and a **pre-commit hook** so `markio validate` can
  guard other people's pipelines.
- Maintain `CITATION.cff` and semantic versioning.

---

## 11. How to work in this repo

1. Read `plan.md`. Pick the current milestone; do not skip ahead.
2. Make the smallest change that advances one task. Keep tests green.
3. For any new format behavior: add a fixture, add a test, then implement.
4. Update `plan.md` checkboxes and the error-taxonomy table when codes change.
5. Never leave the CLI able to do something the library cannot.
