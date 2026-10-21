# Coding systems

Every coding system the Maths Research KG uses or considered: what the code looks like, where it
lives in the graph, how many the catalog has, and how it is checked.

A **coding system** here is any scheme that gives a thing a code with a fixed format: external
identifiers (DOI, arXiv id), external classification codes (MSC2020), numbered lists (Hilbert's
problems), and our own controlled code lists. The meaning of each project code list is in
[`taxonomy.md`](taxonomy.md#controlled-code-lists); the standards behind the external ones are in
[`standards.md`](standards.md).

Measured on `samyama-ai/maths_research` @ `6a4b298`.

## Summary

| Group | Count | Systems |
|---|---:|---|
| A. External identifiers, read from the pages | 4 | DOI, arXiv id, ISO 8601 date, Git SHA-1 + URL |
| B. External classification codes, mapped by us | 3 | MSC2020, arXiv category, ACM CCS 2012 |
| C. Numbered famous-problem lists | 3 | Hilbert's problems (1–23), Millennium Prize Problems (7), Smale's problems (1–18) |
| D. Project code lists | 10 | see table D |
| E. Evaluated, not used in v1 | 8 | zbMATH, MR number, ISBN, ORCID, OEIS, LMFDB label, Wikidata QID, MathML/OpenMath |

## A. External identifiers (read from the pages)

| System | Format (regex) | On | In the catalog | Check |
|---|---|---|---:|---|
| DOI (ISO 26324) | `10\.\d{4,9}/\S+` | `Paper.doi` | 3,997 on 519 pages (all as `https://doi.org/…`) | syntax only; never invented, never looked up |
| arXiv id, new style | `\d{4}\.\d{4,5}(v\d+)?` | `Paper.arxiv_id` | 285 on 169 pages | syntax; `YYMM` month 01–12 |
| arXiv id, old style | `[a-z-]+(\.[A-Z]{2})?/\d{7}` | `Paper.arxiv_id` | 36 on 24 pages | syntax |
| ISO 8601 date | `YYYY-MM-DD`; page dates `YYYY-MM` | `retrieved_at`, `source_date`, Problem dates | 1,161 × 3 page dates | valid calendar date / year-month |
| Git SHA-1 + URL | `[0-9a-f]{40}`; `https://github.com/samyama-ai/maths_research/blob/<sha>/<path>` | `DataSource.version`, every `source_url` | 1 commit | equals the lock file commit |

## B. External classification codes (mapped by us)

The catalog contains none of these codes (MSC: 0 mentions; arXiv categories: 4 mentions on 2
pages). We assign them **at topic level**, as a mapping, in [`taxonomy.md`](taxonomy.md#3-msc2020-mapping-external-map-only).

| System | Format | Levels | On | Used in v1 |
|---|---|---|---|---|
| MSC2020 | `\d{2}` (area), `\d{2}[A-Z]` (section), `\d{2}[A-Z]\d{2}` (subject), e.g. `11`, `11M`, `11M26` | 3 | `TaxonomyTerm {scheme: msc2020}` via `CLASSIFIED_AS` | 2-digit areas + `81P` (~30 codes) |
| arXiv category | `(math|cs|quant-ph)(\.[A-Z]{2})?`, e.g. `math.NT`, `cs.CC` | 2 | `TaxonomyTerm {scheme: arxiv}` | ~25 categories |
| ACM CCS 2012 | concept path, e.g. `Theory of computation → Computational complexity and cryptography` | up to 6 | `TaxonomyTerm {scheme: acm-ccs}` | topic 10 only |

Check: every code used must be in the list in `taxonomy.md`; `BROADER` links follow the code's
own levels (`11M26` → `11M` → `11`).

## C. Numbered famous-problem lists

| System | Codes | On | In the catalog | Rule |
|---|---|---|---:|---|
| Hilbert's problems (1900) | `hilbert:1` … `hilbert:23` | `PART_OF_LIST {number}` | 16 distinct "Hilbert's N-th problem" phrases on 29 pages (tenth on 17 pages) | number written as digits or words ("tenth", "14th") is normalised to 1–23 |
| Millennium Prize Problems (2000) | `millennium:` + one of 7 fixed slugs (`p-vs-np`, `riemann-hypothesis`, `navier-stokes`, `yang-mills`, `hodge`, `birch-swinnerton-dyer`, `poincare`) | `PART_OF_LIST` | "Millennium Prize" on 9 pages | member only if the page is that problem, not a related one |
| Smale's problems (1998) | `smale:1` … `smale:18` | `PART_OF_LIST {number}` | 0 numbered (1 hit is "Smale's 1957") | kept for completeness; expect 0–few |

Erdős problems are kept as a list without numbers (`list:erdos`): no page uses an Erdős problem
number, and most "Erdős" hits are names of theorems (Erdős–Ko–Rado, Erdős–Rényi).

## D. Project code lists

| Code list | On | Values | Source |
|---|---|---|---|
| `status` | Problem | `open`, `partially-solved`, `solved-recently`, `empirically-supported` | catalog |
| `catalog_provenance` | Problem | `synthesized`, `verified` | catalog |
| topic slug | Topic, Problem | `01-number-theory` … `10-theoretical-cs` | catalog |
| `section` | section nodes | `1`–`10` | catalog (TEMPLATE.md) |
| `kind` | Problem | `conjecture`, `hypothesis`, `problem`, `programme`, `theorem`, `question` | title keyword |
| `result_type` | Result | `bound`, `computational`, `special_case`, `conditional`, `counterexample`, `other`, `summary` | bullet keyword |
| `role` | CITES | `foundational`, `sota`, `survey`, `book`, `technique`, `partial`, `computational`, `related`, `other`, `untagged` | tag keyword |
| `kind` | RELATED_TO | `implies`, `implied_by`, `equivalent`, `generalizes`, `special_case`, `related` | sentence keyword |
| `confidence` | Result, ResearchDirection | `frontier-verify`, `stated` | catalog flag |
| `formalization` | Problem | `mentioned`, `none-mentioned` | keyword |

Supporting codes on every node: `provenance` (2 values), `source` (2), `method` (6),
`*_method` (6) and `Paper.parse_status` (3). Node id patterns are in
[`standards.md`](standards.md#identifiers).

## E. Evaluated, not used in v1

| System | What it is | In the catalog | Why not |
|---|---|---:|---|
| zbMATH Open id (`Zbl …`) | id of every maths paper in zbMATH | 0 | would need an external lookup (import) |
| MathSciNet MR number | AMS review id | 0 | same |
| ISBN | book id | 0 | books are cited by title only |
| ORCID | researcher id | 0 | people out of scope |
| OEIS A-number (`A\d{6}`) | integer sequence id | 7 on 4 pages | too few; could be a `Paper`-like `Sequence` node in v2 |
| LMFDB label (e.g. `389a1`) | elliptic curve / L-function label | 1 label; LMFDB named on 7 pages | too few |
| Wikidata QID | general knowledge-base id | 0 | external records |
| MathML / OpenMath | formula encodings | 0 (catalog uses LaTeX) | formulas kept as LaTeX text |

## Validation

The build will check, per coding system: format (regex above), allowed values (lists C and D),
and counts against this page. A value that fails is reported, not dropped silently.
