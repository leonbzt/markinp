# markinp launch & growth plan

A prioritized, phased plan. The theme: this tool has a small, well-defined
audience that gathers in known places — reach *those* places well rather than
broadcasting widely.

## Phase 1 — foundations (done / in progress)

- [x] Publish to **PyPI** (`pip install markinp`).
- [~] **Bioconda** recipe PR (in review) → `conda install -c bioconda markinp`.
- [ ] **Zenodo DOI**: connect the repo at <https://zenodo.org/account/settings/github/>,
      flip `leonbzt/markinp` on, then re-publish the GitHub release. Zenodo mints
      a DOI from `.zenodo.json`. Add the DOI badge to the README and the DOI to
      `CITATION.cff`.
- [ ] **Docs site** live (MkDocs → GitHub Pages via `docs.yml`); enable Pages
      (Settings → Pages → branch `gh-pages`).
- [ ] Repo polish: add GitHub **topics** (`mark`, `capture-recapture`, `rmark`,
      `ecology`, `inp`), a **demo GIF/asciinema** in the README, and a pinned
      "good first issue".

## Phase 2 — credibility & citability (weeks 1–6)

- [ ] **JOSS submission** — `paper/paper.md` is drafted; fill in ORCID +
      affiliation, preview the PDF (the `draft-pdf` workflow builds it), then
      submit at <https://joss.theoj.org/>. A JOSS DOI is the single biggest
      adoption unlock for an academic tool.
- [ ] **pyOpenSci peer review** — see the checklist below. Open a pre-submission
      inquiry, then submit for review; accepted packages are promoted and can be
      fast-tracked to JOSS.
- [ ] **conda-forge** in addition to Bioconda (broader, not bio-only reach).

## Phase 3 — the audience's watering holes (weeks 1–8)

- [ ] **phidot.org forum** — post `announcements/phidot.md` (works now; `pip`
      install is live).
- [ ] **R-sig-ecology** — subscribe, then post `announcements/r-sig-ecology.md`
      as plain text (ideally after Bioconda merges so `conda install` also works).
- [ ] **ECOLOG-L** (large ecology listserv) and the **MARK listserv**; fisheries
      lists (AFS) too — MARK is heavily used in fisheries.
- [ ] **Instructor & author outreach** — use `announcements/instructor-outreach.md`.
      Email 5–10 recent MARK/RMark authors and any workshop instructors; a note to
      Evan Cooch (phidot / *Gentle Introduction*).

## Phase 4 — durable presence (months)

- [ ] **Conference** abstract (EURING / ISEC / TWS) — `announcements/conference-abstract.md`.
- [ ] **SEO that compounds** — the docs `index.md` already targets the literal
      error strings people paste into Google. Add short pages / blog posts titled
      after real MARK errors; cross-post to r-bloggers (with an R example), dev.to.
- [ ] **Screencast** (2 min) showing markinp catching a missing semicolon.
- [ ] **v0.2 feature** — smarter format detection so occupancy / false-positive /
      robust-design files get an honest `MK900` "partial support" message instead
      of a wall of `MK005` errors. This is the top credibility win with the exact
      users who will try it first.

## Channel cheat-sheet

| Channel | Audience | Effort | Payoff |
|---|---|---|---|
| phidot forum | MARK core users | low | high |
| JOSS paper | academics (citations) | med | very high |
| pyOpenSci | Python + science community | med | high |
| Bioconda / conda-forge | conda installers | low | high |
| R-sig-ecology / ECOLOG-L | ecologists | low | med–high |
| Workshop instructors | students (recurring) | low | very high |
| EURING / ISEC | CR specialists | med | high |
| Docs SEO | anyone Googling the error | med | compounding |
| Direct author emails | close-fit researchers | low | med–high |

## pyOpenSci readiness checklist

pyOpenSci reviews scientific Python packages. Start a **pre-submission inquiry**
(GitHub issue on `pyOpenSci/software-submission`) with the text below, then
submit.

Already satisfied:

- [x] Open license (MIT), public repo, semantic versioning.
- [x] Installable from PyPI; minimal dependencies; `py.typed`.
- [x] Automated tests + CI on Linux/macOS/Windows; lint + type checking.
- [x] Documentation site with usage, API/CLI reference, and a format primer.
- [x] Clear statement of scope and target audience.

Quick follow-ups to add before review:

- [x] `CONTRIBUTING.md` and a code of conduct.
- [ ] Issue/PR templates (`.github/ISSUE_TEMPLATE/`).
- [ ] A short "get help / report a bug" section and a changelog (have one).
- [ ] A tutorial-style docs page (the quickstart covers much of this).

**Pre-submission inquiry text:**

> **Package:** markinp — read, validate, and build Program MARK
> encounter-history (`.inp`) files.
>
> **What it does & audience:** A CLI/library that gives wildlife ecologists and
> fisheries scientists precise, line-numbered diagnostics for malformed MARK
> `.inp` files and builds valid `.inp` files from tidy CSVs. File I/O and
> validation only; no statistics.
>
> **Scope fit:** data validation / data munging for a specific scientific file
> format, with a clear, non-overlapping niche (no existing Python package targets
> the MARK `.inp` format). Would this be in scope for pyOpenSci review?
