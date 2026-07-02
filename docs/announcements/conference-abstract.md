# Conference abstract (draft) — EURING / ISEC

A ~250-word tool abstract that fits either a short talk or a poster. Tailor the
title/emphasis to the venue.

**Where to submit (both are bullseye audiences):**

- **EURING Analytical Meeting** — biennial, the field's capture–recapture
  methods meeting; a MARK-heavy audience. Talks, posters, and workshops.
- **ISEC (International Statistical Ecology Conference)** — biennial; speed talks
  and posters; strong capture–recapture track.
- Also consider **The Wildlife Society (TWS)** annual conference and **ESA**
  (Ecological Society of America) for broader reach.

Watch each society's website/mailing list for the call for abstracts (usually
3–6 months before the meeting) and note the word limit (often 250–300 words).

---

**Title:** markinp: turning cryptic Program MARK input errors into precise,
actionable diagnostics

**Abstract:**

Program MARK remains the workhorse of capture–recapture analysis, but its
plain-text encounter-history (`.inp`) input format is easy to get wrong by hand,
and MARK's error messages rarely point to the offending line. Researchers — many
of whom are not programmers — routinely lose time hunting for a missing
semicolon, a ragged history, or a miscounted frequency column, and building an
`.inp` from a capture spreadsheet is commonly done by error-prone manual editing.

We present **markinp**, a small, open-source command-line tool and Python library
that validates, inspects, and builds `.inp` files. `markinp validate` reports
each problem as a structured diagnostic with a stable code, the source line, a
plain-English message, and a concrete fix; `markinp build` generates a valid,
deterministic `.inp` from a tidy CSV, handling groups, covariates, frequencies,
and comments. The tool does file I/O and validation only — it never fits models —
and it complements RMark by requiring neither R nor MARK to run. Human-readable
and JSON output, CI-friendly exit codes, a reusable GitHub Action, and a
pre-commit hook let it guard shared data pipelines. Version 0 fully validates the
standard 0/1 format and honestly reports partial support for specialised formats.
By making the most common `.inp` errors immediately legible, markinp lowers a
small but pervasive barrier for the large community that relies on Program MARK.

*markinp is an independent, unofficial utility, not affiliated with the authors
of Program MARK or RMark.*
