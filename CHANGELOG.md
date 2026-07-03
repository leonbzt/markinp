# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.3.0] — 2026-07-04

### Added
- **First-class occupancy / detection-history support.** `.` (a not-surveyed
  occasion) is now a legal history character; markinp infers a new
  `occupancy` data type from a `0`/`1`/`.` alphabet and fully validates it — no
  more `MK900` "partial support" note for these files.
- `MK021` (warning): an occupancy history of only `.` (a site that was never
  surveyed and contributes nothing to the model).
- `markinp build --data-type occupancy`: build an occupancy `.inp` from a tidy
  site × survey CSV. A missing/blank detection cell becomes `.` (not surveyed),
  never a silent `0` — markinp will not conflate "not surveyed" with
  "not detected".

### Changed
- `MK011` (all-zero history) is **no longer flagged for occupancy data**, where a
  site that was surveyed but never detected is valid, informative data.
- `MK900`'s wording no longer lists occupancy as an unsupported format (it is now
  supported); the note still covers multistrata, false-positive, and
  robust-design files.

## [0.2.0] — 2026-07-03

### Changed
- Smarter data-type detection: histories using a non-standard alphabet (e.g. `.`
  for a not-surveyed occasion, or `2` for a certain detection — as in occupancy,
  false-positive, and robust-design files) are now recognised as a specialised
  format and reported with a single `MK900` note, instead of a flood of `MK005`
  illegal-character errors. Pass `--data-type live_recapture` to enforce strict
  `0`/`1` checking. Validated against a corpus of 93 real MARK files: false
  positives on standard-adjacent files dropped sharply with no regressions.

## [0.1.0] — 2026-07-02

Initial release.

### Added
- Core library: `parse`, `validate`, `inspect`, `build`, `write`.
- CLI (`markinp`) with `validate`, `inspect`, and `build` commands;
  `validate` accepts multiple files and exits non-zero if any fail.
- Human-readable and `--json` (schema version 1) output for every command.
- Diagnostic taxonomy MK001–MK020 and MK900 (partial-support detection),
  documented in `docs/error-codes.md`.
- Deterministic `.inp` writer and `parse -> write -> parse` round-trip stability.
- Distribution: PyPI Trusted Publishing workflow, a reusable GitHub Action,
  a pre-commit hook, and a Bioconda recipe.

[Unreleased]: https://github.com/leonbzt/markinp/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/leonbzt/markinp/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/leonbzt/markinp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/leonbzt/markinp/releases/tag/v0.1.0
