# Contributing to markinp

Thanks for your interest in improving markinp! Bug reports, real-world `.inp`
files that trip it up, and pull requests are all welcome.

## Reporting bugs / requesting features

Open an issue at <https://github.com/leonbzt/markinp/issues>. For a validation
bug, a **small** (non-sensitive) example `.inp` file and the command you ran are
the most helpful thing you can include.

## Development setup

```bash
git clone https://github.com/leonbzt/markinp
cd markinp
python -m pip install -e ".[dev]"
```

Before opening a pull request, please make sure the full gate is green:

```bash
ruff format .        # format
ruff check .         # lint
mypy markinp         # type check (strict)
pytest               # tests
```

## Ground rules (from the project's design)

markinp is deliberately narrow. A few non-negotiables keep it trustworthy:

- **No statistics, ever.** markinp does file I/O and validation only — no model
  fitting, likelihoods, or estimation.
- **Errors are the product.** Every problem is a structured diagnostic with a
  stable code, a severity, a line number, a plain message, and an actionable
  hint. Codes are never renumbered once released.
- **Never silently change a user's data.** Report a diagnostic; only modify data
  when the user explicitly asks.
- **Deterministic output.** Given the same input, output bytes are identical.
- **A change to parsing or a format rule needs a test.** Add a fixture under
  `tests/fixtures/` and a test asserting the exact diagnostic code.

If you add a new diagnostic code, document it in `docs/error-codes.md` and
`plan.md` first, then implement it with a triggering fixture.

## Code style

- Type-hint every function; keep functions small and pure where possible.
- Convert caught exceptions into diagnostics rather than raising to the user.
- Match the surrounding code's conventions.

By contributing, you agree that your contributions are licensed under the
project's MIT license.
