"""Read ``.inp`` text into a :class:`~markinp.model.Dataset`.

The parser is a decoder only: it turns bytes into records and records into an
inferred structure. It emits *parse-level* diagnostics (encoding, missing
terminators, unterminated comments, whitespace) but does not judge the data
semantically — that is :mod:`markinp.validate`'s job. Line numbers are tracked
throughout so every downstream diagnostic can point at a source line.
"""

from __future__ import annotations

import codecs
from collections import Counter
from pathlib import Path

from . import diagnostics as dx
from .model import Dataset, DataType, Diagnostic, EncounterHistory
from .tokens import is_float_token, is_int_token, looks_like_covariate

_ASCII_LETTERS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")


class ParseResult:
    """The Dataset plus any diagnostics raised while decoding it."""

    def __init__(self, dataset: Dataset, diagnostics: list[Diagnostic]) -> None:
        self.dataset = dataset
        self.diagnostics = diagnostics


def read_text(path: str | Path) -> tuple[str, list[Diagnostic]]:
    """Read a file as text, tolerating BOMs and non-UTF-8 encodings.

    MARK files usually originate on Windows and from Excel, so they may be
    Latin-1, may carry a UTF-8 BOM, and may use CRLF line endings. This returns
    the decoded text (line endings normalized to ``\\n``) plus any ``MK020``
    encoding diagnostics.
    """
    data = Path(path).read_bytes()
    diagnostics: list[Diagnostic] = []

    if data.startswith(codecs.BOM_UTF8):
        data = data[len(codecs.BOM_UTF8) :]
        diagnostics.append(
            dx.mk020_encoding(
                "file starts with a UTF-8 byte-order mark (BOM)",
                "Some tools mishandle a BOM; save the file as plain UTF-8 without one",
            )
        )

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("latin-1")
        diagnostics.append(
            dx.mk020_encoding(
                "file is not valid UTF-8; decoded it as Latin-1",
                "Re-save the file as UTF-8 to avoid mangled characters",
            )
        )

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text, diagnostics


def _strip_line_comments(line: str, in_comment: bool) -> tuple[str, list[str], bool, str]:
    """Remove ``/* ... */`` comments from one line.

    Returns the code (comment-free) text, the comment strings found on the line,
    whether a comment is still open at end of line, and the partial text of any
    still-open comment (so a multi-line comment can be reassembled).
    """
    out: list[str] = []
    comments: list[str] = []
    partial: list[str] = []
    i, n = 0, len(line)

    while i < n:
        if in_comment:
            close = line.find("*/", i)
            if close == -1:
                partial.append(line[i:])
                i = n
            else:
                partial.append(line[i:close])
                comments.append("".join(partial).strip())
                partial = []
                in_comment = False
                i = close + 2
        else:
            opener = line.find("/*", i)
            if opener == -1:
                out.append(line[i:])
                i = n
            else:
                out.append(line[i:opener])
                i = opener + 2
                in_comment = True
    return "".join(out), comments, in_comment, "".join(partial)


def parse_text(text: str) -> ParseResult:
    """Parse decoded ``.inp`` text into a :class:`ParseResult`."""
    diagnostics: list[Diagnostic] = []
    records: list[EncounterHistory] = []

    in_comment = False
    comment_start_line: int | None = None
    pending_comment: str | None = None

    for lineno, raw_line in enumerate(text.split("\n"), start=1):
        was_open = in_comment
        code, comments, in_comment, _partial = _strip_line_comments(raw_line, in_comment)
        if not was_open and in_comment:
            comment_start_line = lineno
        elif not in_comment:
            comment_start_line = None if not was_open else comment_start_line

        if not code.strip():
            # Comment-only or blank line: remember a comment to label the next record.
            if comments:
                pending_comment = comments[0]
            continue

        comment = comments[0] if comments else pending_comment
        pending_comment = None

        record, record_diags = _parse_record(code, comment, lineno)
        diagnostics.extend(record_diags)
        if record is not None:
            records.append(record)

    if in_comment and comment_start_line is not None:
        diagnostics.append(dx.mk009_unterminated_comment(comment_start_line))

    dataset = _build_dataset(records)
    return ParseResult(dataset, diagnostics)


def _parse_record(
    code: str, comment: str | None, lineno: int
) -> tuple[EncounterHistory | None, list[Diagnostic]]:
    """Turn one line's code text into a record (or ``None`` if it holds no data)."""
    diagnostics: list[Diagnostic] = []

    if ";" in code:
        body, _, after = code.partition(";")
        if after.strip():
            diagnostics.append(dx.mk015_content_after_semicolon(lineno))
    else:
        body = code
        diagnostics.append(dx.mk001_missing_semicolon(lineno))

    if "\t" in body.strip() and " " in body.strip():
        diagnostics.append(dx.mk016_mixed_whitespace(lineno))

    tokens = body.split()
    if not tokens:
        return None, diagnostics

    history = tokens[0]
    values = tokens[1:]
    record = EncounterHistory(
        history=history,
        frequencies=[],
        covariates=[],
        comment=comment,
        line=lineno,
        raw_values=values,
    )
    return record, diagnostics


def infer_data_type(records: list[EncounterHistory]) -> DataType:
    """Guess the data type from history characters alone.

    Only the standard 0/1 case and the presence of stratum letters are
    distinguishable from content; known-fate vs. dead-recovery vs. closed
    captures require the user to assert ``--data-type``.
    """
    chars: set[str] = set()
    for record in records:
        chars.update(record.history)
    if chars - {"0", "1"} & _ASCII_LETTERS:
        return DataType.MULTISTRATA
    return DataType.LIVE_RECAPTURE


def infer_occasions(records: list[EncounterHistory]) -> int:
    """Infer occasion count as the most common history length."""
    if not records:
        return 0
    lengths = Counter(len(r.history) for r in records)
    return lengths.most_common(1)[0][0]


def infer_groups_covariates(records: list[EncounterHistory]) -> tuple[int, int]:
    """Infer (n_groups, n_covariates) from the value columns.

    The structural width is the most common count of value columns. Columns are
    split into a leading block of group frequencies and a trailing block of
    covariates at the first column that contains a decimal-formatted value. There
    is always at least one group.
    """
    if not records:
        return 1, 0
    widths = Counter(len(r.raw_values) for r in records)
    width = widths.most_common(1)[0][0]

    first_cov = width
    for col in range(width):
        if any(
            col < len(r.raw_values) and looks_like_covariate(r.raw_values[col]) for r in records
        ):
            first_cov = col
            break

    n_groups = max(1, first_cov)
    n_covariates = max(0, width - n_groups)
    return n_groups, n_covariates


def _build_dataset(records: list[EncounterHistory]) -> Dataset:
    """Assemble a Dataset and fill best-effort typed frequency/covariate views."""
    data_type = infer_data_type(records)
    n_occasions = infer_occasions(records)
    n_groups, n_covariates = infer_groups_covariates(records)

    for record in records:
        freqs: list[int] = []
        covs: list[float] = []
        for i, tok in enumerate(record.raw_values):
            if i < n_groups:
                if is_int_token(tok):
                    freqs.append(int(tok))
            elif is_float_token(tok):
                covs.append(float(tok))
        record.frequencies = freqs
        record.covariates = covs

    return Dataset(
        n_occasions=n_occasions,
        n_groups=n_groups,
        n_covariates=n_covariates,
        group_labels=None,
        cov_labels=None,
        data_type=data_type,
        records=records,
    )


def parse_file(path: str | Path) -> ParseResult:
    """Read and parse an ``.inp`` file from disk."""
    text, encoding_diags = read_text(path)
    result = parse_text(text)
    result.diagnostics = encoding_diags + result.diagnostics
    return result
