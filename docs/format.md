# The `.inp` format in one minute

A Program MARK `.inp` file is plain text. Each **record** is one line, terminated
by a semicolon. Fields are separated by whitespace (spaces or tabs).

```
[/* comment */]  HISTORY  FREQ_1 [FREQ_2 ... FREQ_g]  [COV_1 ... COV_c]  ;  [/* comment */]
```

- **HISTORY** — the encounter history, one character per sampling occasion. In
  the standard format, `1` = detected/captured and `0` = not detected.
- **FREQ_1 … FREQ_g** — one integer frequency **per group** `g`: the count of
  individuals sharing this history in that group. Frequencies may be **negative**
  to denote losses on capture (removals).
- **COV_1 … COV_c** — optional numeric individual covariates. Covariates
  **cannot** have missing values.
- **`;`** — terminates the record. A missing semicolon is the single most common
  reason MARK rejects a file.
- **Comments** are delimited by `/* ... */` and may appear anywhere; they are
  often used at the start of a line to label an individual.

## Worked example

Two groups (e.g. Male / Female) and one covariate (weight):

```
/* ind 001 */ 1001 1 0 10.2;
/* ind 002 */ 1101 0 2 9.5;
0101 3 1 8.1;
```

- Record 1: history `1001`, group-1 frequency `1`, group-2 frequency `0`,
  covariate `10.2`.
- Record 2: history `1101`, group-1 frequency `0`, group-2 frequency `2`,
  covariate `9.5`.
- Record 3: history `0101`, group-1 frequency `3`, group-2 frequency `1`,
  covariate `8.1`.

## Rules markinp checks

- Every history has the **same length** (= number of occasions).
- Every record has the **same number of frequency columns** (= number of groups)
  and the **same number of covariate columns**.
- Frequencies are integers; covariates are numeric and never blank.
- Records end in `;`; comments are balanced.

The number of occasions, groups, and covariates is usually **not** stored in the
file, so `markinp` infers it — and you can assert the values you expect to make
the checks stricter:

```bash
markinp validate captures.inp --occasions 4 --groups 2 --covariates 1
```

!!! info "Inference rule of thumb"
    A value column written with a decimal point (e.g. `10.5`) is treated as a
    **covariate**; an all-integer column is treated as a **group frequency**.
    Because a whole-number covariate looks exactly like a frequency, assert your
    structure with `--groups`/`--covariates` when it matters.

## Encoding and line endings

MARK is a Windows-origin tool and input often comes from Excel, so files are
commonly UTF-8 or Latin-1 with CRLF line endings and may carry a byte-order mark
(BOM). `markinp` reads all of these robustly and flags odd encodings.
