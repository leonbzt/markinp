# markinp error codes

Every problem markinp reports is a **diagnostic** with a stable code, a
severity, a plain-English message, an actionable hint, and (when known) a line
number. Codes are stable once released and never renumbered.

- **Severity:** `E` = error, `W` = warning, `I` = info.
- `--strict` promotes every warning to an error.
- Exit code is `0` when there are no errors and `1` otherwise.
- `MK900` is informational: it means markinp detected a specialized format it
  only checks partially — treat a clean result on those files with caution.

## Quick reference

| Code  | Sev | Triggered when… | What to do |
|-------|:---:|-----------------|------------|
| MK001 | E | A record line does not end in `;` | Add a `;` at the end of the line |
| MK002 | E | A history's length differs from the file's occasion count | Give every history one character per occasion |
| MK003 | E | A frequency value is not a number | Remove stray text; check for an accidental space |
| MK004 | E | The number of frequency columns ≠ the number of groups | Provide exactly one frequency per group |
| MK005 | E | A history contains a non-`0`/`1` character when the file is (asserted) standard | Standard histories use only `0`/`1`; pass `--data-type` for other formats |
| MK006 | E | The covariate count differs between records | Give every record the same number of covariates |
| MK007 | E | A covariate is blank or non-numeric | Fill in a number; MARK covariates cannot be missing |
| MK008 | E | The file has no encounter records | Add at least one history record ending in `;` |
| MK009 | E | A `/* … */` comment is never closed | Close the comment with `*/` |
| MK010 | E | A history length ≠ the asserted `--occasions` | Fix the history or the `--occasions` value |
| MK011 | W | A history is all zeros (never encountered) | Usually invalid for live recapture; verify the row |
| MK012 | W | A frequency is negative | Valid only as a loss on capture (removal); confirm |
| MK013 | I | Identical history+covariate rows are not collapsed | Aggregate them into one row with a summed frequency |
| MK014 | E | A frequency is not a whole number (e.g. `1.5`, `2.0`) | Write frequencies as integers |
| MK015 | W | There is content after the `;` that is not a comment | Move it before the `;` or wrap it in `/* */` |
| MK016 | I | Fields are separated by a mix of tabs and spaces | Harmless; use consistent whitespace |
| MK017 | E | A multistrata history uses a non-stratum character | Use only `0` and stratum letters (A, B, …) |
| MK018 | E | A known-fate / dead-recovery history has odd length | These histories are Live/Dead pairs (even length) |
| MK019 | W | A declared group has all-zero frequencies | A group with no individuals is often a setup mistake |
| MK020 | W | Unexpected encoding / BOM / non-UTF-8 bytes | Save the file as plain UTF-8 |
| MK900 | I | A specialized format was detected (multistrata, or a non-`0`/`1` alphabet such as occupancy/false-positive/robust-design) | Only partially validated; full support is a later milestone |

## How markinp infers structure

The number of occasions, groups, and covariates is usually **not** stored in an
`.inp` file, so markinp infers it and lets you assert stricter values:

- **Occasions** = the most common history length. A history of a different
  length raises `MK002` (or `MK010` if you passed `--occasions`).
- **Groups vs. covariates.** A value column written with a decimal point or
  exponent (e.g. `10.5`, `1e3`) is treated as a **covariate**; an all-integer
  column is treated as a **group frequency**. There is always at least one
  group. Because a covariate written as a whole number (e.g. `10`) is
  indistinguishable from a frequency, assert your true structure with
  `--groups` and `--covariates` when it matters.
- **Data type.** Histories using only `0`/`1` are read as the standard
  live-recapture format. Histories containing letters are read as multistrata,
  and histories using other non-standard characters (e.g. `.` for a not-surveyed
  occasion, or `2` for a certain detection) are recognised as a specialised
  format markinp does not yet fully support (occupancy, false-positive occupancy,
  robust design, ...). In both cases markinp reports a single `MK900` and does
  **not** flag the individual encounter characters, rather than drowning you in
  per-character errors. If you know a file is standard and want strict `0`/`1`
  checking, pass `--data-type live_recapture`. Known-fate and dead-recovery
  cannot be told apart from the bytes alone — assert them with
  `--data-type known_fate` / `--data-type dead_recovery` to enable the Live/Dead
  pairing check (`MK018`).

## Tightening the checks

```bash
markinp validate captures.inp --occasions 4 --groups 2 --covariates 1
markinp validate captures.inp --strict          # warnings become errors
markinp validate captures.inp --data-type known_fate
```

## Scope reminder

v0 fully validates the standard `0`/`1` format. Known-fate, dead-recovery
(Brownie), and multistrata files are **detected and structurally checked only**
(`MK900`); markinp will always say so rather than pretend a specialized file is
fully validated.
