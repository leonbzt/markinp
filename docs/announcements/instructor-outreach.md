# Instructor & author outreach (draft templates)

The highest-leverage word-of-mouth channel: people who **teach** MARK/RMark
workshops watch students fight `.inp` formatting every year. One instructor
recommending `markinp` seeds a whole cohort of users annually. Keep emails short,
specific, and generous (you're saving them time, not selling).

**Who to contact**

- Instructors of MARK / RMark workshops (universities, agencies such as USGS,
  short courses at conferences).
- Evan Cooch (maintainer of the *Gentle Introduction to MARK* and phidot.org) —
  even a one-line mention or a link is field-defining reach.
- Authors of recent papers that used Program MARK or RMark (find them via Google
  Scholar; email 5–10 whose work is close to your own).

**Concrete contacts & links**

- **Evan Cooch** — maintainer of the *Gentle Introduction to MARK* and phidot.org;
  Cornell Dept. of Natural Resources & the Environment.
  `evan.cooch@cornell.edu` · <https://dnr.cals.cornell.edu/people/evan-cooch>
- **Gary White** — author of Program MARK, Colorado State University.
  <https://sites.warnercnr.colostate.edu/gwhite/>
- **Jeff Laake** — author of RMark. <https://github.com/jlaake/RMark>
- **unmarked mailing list (Google Group)** — the R `unmarked` / occupancy
  community; the single best-fit list now that markinp validates occupancy files.
  <https://groups.google.com/g/unmarked>
- **ECOLOG-L (ESA listserv)** — broad ecology reach. Subscribe:
  <https://esa.org/membership/ecolog/> · post to `ecolog-l@community.esa.org`.
- **R-sig-ecology** — <https://stat.ethz.ch/mailman/listinfo/r-sig-ecology>.

---

## Template A — workshop instructor

> **Subject:** A free tool that might save your MARK students some grief
>
> Hi [Name],
>
> I saw you teach [the MARK / RMark workshop at X]. I built a small, free,
> open-source tool called **markinp** that catches the `.inp` formatting mistakes
> students hit constantly — missing semicolons, ragged histories, wrong number of
> frequency columns — and reports them with the exact line and a fix, e.g.:
>
> ```
> MK001  ERROR  line 12: record is not terminated by a semicolon
>        hint: Add a ';' at the end of this line to close the record
> ```
>
> It can also build a valid `.inp` from a tidy CSV. It does file I/O and
> validation only (no statistics) and is an independent, unofficial utility — not
> affiliated with MARK or RMark.
>
> If it looks useful, I'd be grateful if you'd try it and let me know what breaks;
> and if it earns a place, a mention to students would mean a lot.
>
> Install: `pip install markinp` · Source: https://github.com/leonbzt/markinp
>
> Thanks for considering it,
> Leon

---

## Template B — recent MARK/RMark author

> **Subject:** markinp — validating/building MARK .inp files, might save you time
>
> Hi [Name],
>
> I enjoyed your paper [short, specific reference]. I built a small open-source
> tool, **markinp**, that validates and builds Program MARK `.inp` files with
> precise, line-numbered error messages, and works as a pre-flight check before
> RMark's `convert.inp()`. It needs neither R nor MARK to run.
>
> If you work with `.inp` files regularly it might be handy — and if you have
> files that trip it up, a bug report would genuinely help me improve it.
>
> `pip install markinp` · https://github.com/leonbzt/markinp
>
> Best,
> Leon
