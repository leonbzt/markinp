# R-sig-ecology mailing list announcement (draft)

Post to the R-sig-ecology mailing list. **Subscribe first** (posts from
non-members bounce) and send as **plain text** (no HTML). Keep it concise. The
same text, lightly trimmed, also works for RMark's GitHub Discussions and the
MARK listserv / MARK Facebook group.

---

**Subject:** markinp: a small CLI to validate & build Program MARK .inp files (complements RMark)

Dear list,

I'd like to share a small open-source tool that may be useful to anyone who works
with Program MARK input (`.inp`) files, including RMark users: **markinp**.

Up front: it is a command-line tool / Python library, **not** an R package, and
it is an independent, unofficial utility (not affiliated with MARK or RMark). It
deliberately does *no* statistics — file I/O and validation only.

**Why it might help an RMark workflow:**

- It gives **precise, line-numbered** diagnostics when an `.inp` is malformed,
  instead of a cryptic rejection — useful as a pre-flight check before
  `convert.inp()` / importing data.
- It **builds** a valid `.inp` from a tidy CSV (long or wide), handling groups,
  individual covariates, frequencies, and comments deterministically — so you
  don't hand-edit in a text editor or Excel.
- Being a CLI with proper exit codes, it drops into a **Makefile, CI job, or
  pre-commit hook** to guard a data pipeline (a reusable GitHub Action and
  pre-commit hook are included). No R or Python knowledge needed to run
  `markinp validate data/*.inp`.

**Example:**

```
$ markinp validate captures.inp
MK004  ERROR  line 7: record has 3 frequency values but the file uses 2 groups
       hint: Give exactly one frequency per group; check for a missing/extra value
```

**Scope:** the standard 0/1 encounter-history format is fully validated;
known-fate, dead-recovery, multistrata and occupancy formats are currently
detected and structurally checked only (the tool tells you when it can only
partially validate a file). A round-trip `.inp` <-> tidy-dataframe converter
(mirroring `convert.inp`, both directions) is on the roadmap.

Install: `pip install markinp`
Source / docs / issues (MIT): https://github.com/leonbzt/markinp

Feedback, feature requests, and awkward real-world `.inp` files are all very
welcome.

Best regards,
Leon Botzenhardt
