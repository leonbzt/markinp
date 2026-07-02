# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

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

[Unreleased]: https://github.com/leonbzt/markinp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/leonbzt/markinp/releases/tag/v0.1.0
