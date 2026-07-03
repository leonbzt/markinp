# CLI reference

Every command prints human-readable output by default, accepts `--json` for
machine output, and exits `0` when there are no errors and `1` otherwise.

## `markinp validate`

Validate one or more `.inp` files.

```bash
markinp validate FILE.inp [FILE.inp ...] [options]
```

| Option | Meaning |
|--------|---------|
| `--groups N` | Assert the expected number of groups |
| `--occasions N` | Assert the expected history length |
| `--covariates N` | Assert the expected covariate count |
| `--data-type TYPE` | Hint the data type (`live_recapture`, `closed_captures`, `occupancy`, `known_fate`, `dead_recovery`, `multistrata`) |
| `--strict` | Treat warnings as errors |
| `--json` | Emit machine-readable JSON |

With several files, `--json` emits an array of per-file objects. The command
exits non-zero if **any** file has an error, so it works in CI and pre-commit.

```bash
markinp validate data/*.inp --strict
```

## `markinp inspect`

Summarise the inferred structure of a file (read-only).

```bash
markinp inspect FILE.inp [--json]
```

Reports occasions, groups, covariates, number of records, number of individuals
(sum of the absolute frequencies), and a data-type guess.

## `markinp build`

Build a valid, deterministic `.inp` from a tidy CSV.

```bash
markinp build INPUT.csv -o OUTPUT.inp [options]
```

| Option | Meaning |
|--------|---------|
| `--format long\|wide` | Layout (default: auto-detect) |
| `--id-col NAME` | Individual id column (long format) |
| `--occasion-col NAME` | Occasion column (long format) |
| `--detect-col NAME` | 0/1 detection column (long format) |
| `--history-col NAME` | Prebuilt history column (wide alternative) |
| `--group-col NAME` | Column defining groups |
| `--covariate-cols A,B,...` | Comma-separated covariate columns |
| `--comment-col NAME` | Column written as `/* value */` per record |
| `--data-type TYPE` | `live_recapture` (default) or `occupancy` |
| `--collapse / --no-collapse` | Aggregate identical histories (default: on) |
| `--json` | Emit a build report |

`build` validates its own output and refuses to write a file that would not
pass `validate`.

### Long format

One row per (individual × occasion):

```
id,occasion,detected,sex,weight
A1,1,1,M,10.2
A1,2,0,M,10.2
A1,3,1,M,10.2
```

```bash
markinp build captures.csv -o out.inp \
    --id-col id --occasion-col occasion --detect-col detected \
    --group-col sex --covariate-cols weight
```

### Wide format

One row per individual, with occasion columns (or a prebuilt `history` column):

```
id,o1,o2,o3,sex,weight
A1,1,0,1,M,10.2
```

```bash
markinp build captures.csv -o out.inp --format wide \
    --group-col sex --covariate-cols weight
```

### Occupancy format

For occupancy / detection-history data, pass `--data-type occupancy`. A blank or
`NA` detection cell is written as `.` (**not surveyed**) instead of `0`, so a
missing survey is never mistaken for a non-detection:

```
site,survey,detected,elev
A,1,1,120
A,2,0,120
A,3,,120      # not surveyed -> '.'
```

```bash
markinp build sites.csv -o out.inp --data-type occupancy \
    --id-col site --occasion-col survey --detect-col detected \
    --covariate-cols elev
# site A -> history "10."
```

## Use as a library

The CLI is a thin wrapper; everything is importable:

```python
from markinp import parse_text, validate

result = parse_text("1001 1;\n0101 2;\n")
for diag in validate(result.dataset):
    print(diag.code, diag.message)
```
