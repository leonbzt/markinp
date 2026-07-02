# markinp

**Read, validate, and build Program MARK encounter-history (`.inp`) files — with
error messages that actually tell you what to fix.**

`markinp` removes the most common friction in the capture–recapture workflow:
hand-building `.inp` files in a text editor or Excel, and only discovering
formatting mistakes when MARK rejects the file with an unhelpful message such as
*"error reading input file"* or a silent failure partway through. Instead, you
get a precise, line-numbered diagnosis in about a second.

!!! note "Scope and disclaimer"
    `markinp` is an independent, unofficial utility. It is **not** affiliated
    with or endorsed by the authors of Program MARK or RMark. It does **file I/O
    and validation only** — it never fits models or computes statistics.

## Install

```bash
pip install markinp
# or, once the Bioconda recipe is merged:
conda install -c bioconda markinp
```

## What it does

- **`markinp validate file.inp`** — check a file and report every problem as a
  stable, line-numbered diagnostic with a fix (see [Error codes](error-codes.md)).
- **`markinp inspect file.inp`** — summarise the inferred structure: occasions,
  groups, covariates, records, individuals, and a data-type guess.
- **`markinp build captures.csv -o out.inp`** — build a valid, deterministic
  `.inp` from a tidy CSV (long or wide).

## A first look

```
$ markinp validate captures.inp
MK001  ERROR  line 12: record is not terminated by a semicolon
       hint: Add a ';' at the end of this line to close the record
```

Every command supports `--json` for machine-readable output and exits non-zero
when errors are found, so `markinp validate` drops straight into CI, a
[GitHub Action](https://github.com/leonbzt/markinp#guard-a-pipeline-ci--pre-commit),
or a pre-commit hook.

## Common problems markinp explains

If you searched for one of these, you're in the right place:

- *MARK won't read my `.inp` file / "error reading input file".*
- *Missing semicolon at the end of an encounter history.*
- *Encounter histories have different lengths (ragged histories).*
- *Wrong number of frequency columns for the number of groups.*
- *Covariate is blank / non-numeric.*
- *`convert.inp` fails in RMark.*

See [The .inp format](format.md) for a one-minute primer and
[Error codes](error-codes.md) for the full reference.
