---
title: "markinp: reading, validating, and building Program MARK encounter-history files"
tags:
  - Python
  - ecology
  - capture-recapture
  - mark-recapture
  - Program MARK
  - data validation
authors:
  - name: Leon Botzenhardt
    orcid: 0000-0000-0000-0000   # TODO: add your ORCID (free at https://orcid.org)
    affiliation: 1
affiliations:
  - name: Independent researcher   # TODO: replace with your institution
    index: 1
date: 2 July 2026
bibliography: paper.bib
---

# Summary

Capture–recapture (or capture–mark–recapture) studies are a cornerstone of
wildlife ecology, conservation biology, and fisheries science. Program MARK
[@white1999mark], the field's dominant analysis platform, reads encounter
histories from a plain-text input file with the `.inp` extension. Despite its
central role, the `.inp` format is easy to get wrong by hand and MARK's error
messages when a file is malformed are terse and rarely point to the offending
line. `markinp` is a small, dependency-light command-line tool and Python
library that **validates**, **inspects**, and **builds** `.inp` files, turning
opaque formatting failures into precise, line-numbered, actionable diagnostics.
It performs file input/output and validation only; it never fits models or
computes statistics, and it is not affiliated with the authors of Program MARK
or RMark [@laake2013rmark].

# Statement of need

Preparing an `.inp` file is a recurring source of friction in the
capture–recapture workflow. Encounter histories must all share the same length,
each record must carry one integer frequency per group, individual covariates
must be numeric and complete, records must be terminated with a semicolon, and
comments must be balanced. A single missing semicolon or a ragged history can
cause MARK to reject the file with a message that does not identify the cause,
and users — many of whom are not programmers — are left comparing their file
against examples line by line. The same friction appears when converting a tidy
capture spreadsheet into an `.inp` file, which is commonly done by hand in a
text editor or spreadsheet program.

`markinp` addresses both pain points. `markinp validate` reports every problem
it finds as a structured *diagnostic* with a stable code, a severity, the source
line, a plain-English message, and a concrete hint (for example, "record has 3
frequency values but the file uses 2 groups — check for a missing or extra
value"). `markinp inspect` summarises a file's inferred structure (occasions,
groups, covariates, number of individuals, and a data-type guess). `markinp
build` generates a valid, deterministic `.inp` file from a tidy CSV in long or
wide layout, handling groups, covariates, frequencies, comments, and the
collapsing of identical histories. Every command offers human-readable output by
default and machine-readable JSON on request, and exits non-zero when errors are
found so that it can guard a data pipeline in continuous integration, as a
reusable GitHub Action, or as a pre-commit hook.

The tool is intentionally narrow in scope. Version 0 fully validates the
standard 0/1 encounter-history format used by live-recapture (Cormack–Jolly–
Seber), Jolly–Seber, and closed-captures models — the same subset that RMark's
`convert.inp` handles [@laake2013rmark]. Specialised formats (known-fate,
dead-recovery, and multistrata) are detected and structurally checked, and the
tool reports honestly when it can only partially validate a file rather than
implying that an unsupported file is correct. Format rules were encoded from the
canonical field reference, the *Gentle Introduction to MARK*
[@cooch2023gentle].

`markinp` complements, rather than competes with, RMark: it needs neither R nor
MARK to run, it works in both directions (validate an existing file or build a
new one), and it can serve as a pre-flight check before data are imported for
analysis. By making the most common `.inp` errors immediately legible, `markinp`
lowers a small but pervasive barrier for the large community of ecologists who
rely on Program MARK.

# Acknowledgements

`markinp` is an independent, unofficial utility. "MARK" is referenced only to
describe the file format with which it interoperates.

# References
