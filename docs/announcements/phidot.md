# phidot.org forum announcement (draft)

Post to the phidot.org forum (the Program MARK community) once the repo is
public and the PyPI release is live. Keep the "unofficial / no statistics /
honest scope" framing — it pre-empts the main objection the community raises
about third-party MARK tools. Include a concrete example.

---

**Subject:** markinp — a free tool to validate & build MARK `.inp` files (feedback welcome)

Hi all,

I've built a small, free, open-source tool called **markinp** to take some of the
pain out of preparing Program MARK input files, and I'd love this community's
feedback before I call it stable.

**The two moments it targets:**

1. *"MARK rejected my `.inp` and the message didn't tell me why."*
2. *"I have a capture spreadsheet and need to hand-build an `.inp`."*

**What it does** (three commands, nothing more):

- `markinp validate file.inp` — checks the file and reports **line-numbered,
  plain-English** problems with a suggested fix, e.g.:

  ```
  MK001  ERROR  line 12: record is not terminated by a semicolon
         hint: Add a ';' at the end of this line to close the record
  ```

- `markinp inspect file.inp` — summarises the inferred structure (occasions,
  groups, covariates, #individuals, data-type guess).
- `markinp build captures.csv -o out.inp` — builds a valid, deterministic
  `.inp` from a tidy CSV (long or wide), handling groups, covariates,
  frequencies, and comments.

It catches the usual suspects: missing semicolons, ragged history lengths, the
wrong number of frequency columns for the group count, non-integer/blank values,
unterminated `/* */` comments, all-zero histories, encoding/BOM issues, and so
on — each with a stable code and a hint.

**Important, up front:** markinp is an **independent, unofficial** utility. It is
*not* affiliated with or endorsed by the authors of Program MARK or RMark — it
only reads/writes the `.inp` file format. It does **file I/O and validation
only**: it never fits models or computes anything statistical. Where I checked
the format rules, I leaned on Chapter 2 of Cooch & White's *Gentle Introduction*.

**Scope (being honest):** the standard 0/1 encounter-history format (CJS /
Jolly-Seber / closed captures) is fully validated. Known-fate, dead-recovery
(Brownie), multistrata, and occupancy-style formats are currently only *detected
and structurally checked* — the tool says so rather than pretending. Full support
for those is on the roadmap, and I'd genuinely value pointers on the trickier
format rules.

**Install / links:**

```
pip install markinp
```

Source, docs, and issue tracker: https://github.com/leonbzt/markinp

If you have `.inp` files that trip it up — especially edge cases or specialised
data types — I'd love a bug report or a (non-sensitive) sample. Thanks for taking
a look.

— Leon
