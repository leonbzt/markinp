# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

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

[Unreleased]: https://github.com/leonbzt/markinp/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/leonbzt/markinp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/leonbzt/markinp/releases/tag/v0.1.0
