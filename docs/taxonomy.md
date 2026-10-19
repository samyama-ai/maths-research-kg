# Taxonomies and code lists

The hierarchies (taxonomies) and the fixed value lists (controlled code lists) of the Maths
Research KG. Every taxonomy term is a `TaxonomyTerm` node with `scheme` and `notation`
(SKOS). Every code list is a property with allowed values; the build rejects anything else.
Formats, counts and checks of every coding system (including DOI, arXiv, MSC2020 and the
numbered famous lists) are in [`coding-systems.md`](coding-systems.md).

Source: `samyama-ai/maths_research` @ `6a4b298`. Counts were measured on that commit and are
targets to re-check after the build.

## Summary

| Kind | Count | Items |
|---|---:|---|
| Taxonomies | 5 | Topic, Subtopic, MSC2020 mapping, arXiv / ACM CCS mapping, Famous problem lists |
| Controlled code lists | 10 | 4 existing in the catalog + 6 project-defined |

## Taxonomies

### 1. Topic (existing, 10 terms)

Flat, from `TAXONOMY.md`. Scheme `topic`, notation = folder number.

| Notation | Topic | Problems | open | partially | solved-recently | empirical |
|---|---|---:|---:|---:|---:|---:|
| 01 | Number Theory | 134 | 96 | 17 | 16 | 5 |
| 02 | Algebra & Group Theory | 108 | 54 | 19 | 35 | 0 |
| 03 | Algebraic & Differential Geometry | 113 | 59 | 26 | 28 | 0 |
| 04 | Topology & Knot Theory | 112 | 46 | 25 | 38 | 3 |
| 05 | Real & Complex Analysis | 114 | 61 | 33 | 17 | 3 |
| 06 | Partial Differential Equations | 119 | 32 | 69 | 15 | 3 |
| 07 | Combinatorics & Graph Theory | 114 | 67 | 19 | 28 | 0 |
| 08 | Mathematical Logic & Set Theory | 115 | 46 | 53 | 15 | 1 |
| 09 | Probability & Stochastic Processes | 115 | 32 | 54 | 25 | 4 |
| 10 | Theoretical Computer Science | 117 | 84 | 18 | 12 | 3 |

### 2. Subtopic (project-defined, from the catalog)

Second level under each Topic, taken word for word from the **Scope** column of `TAXONOMY.md`
(e.g. 01 → distribution of primes, Diophantine equations, elliptic curves, modular forms, class
field theory, arithmetic geometry). About 5–6 per topic, ~55 terms. `BROADER` → its Topic.

A Problem is `CLASSIFIED_AS` a Subtopic when the subtopic phrase (or a listed synonym) appears in
its title or section 1–2. `CLASSIFIED_AS.method = keyword-classified`. A problem may match zero
or several subtopics; zero is allowed and counted.

### 3. MSC2020 mapping (external, map only)

The Mathematics Subject Classification 2020 (zbMATH Open + AMS). Mapped **at topic level** in v1:
each Topic is `CLASSIFIED_AS` one or more MSC top-level codes. The codes used become
TaxonomyTerms with scheme `msc2020`. No per-problem MSC codes in v1 (the catalog has none).

| Topic | MSC2020 top-level codes |
|---|---|
| 01 Number Theory | 11 Number theory |
| 02 Algebra & Group Theory | 20 Group theory; 16 Associative rings; 17 Nonassociative rings; 18 Category theory, homological algebra; 13 Commutative algebra |
| 03 Geometry | 14 Algebraic geometry; 53 Differential geometry; 52 Convex and discrete geometry; 51 Geometry |
| 04 Topology & Knot Theory | 57 Manifolds and cell complexes; 55 Algebraic topology; 54 General topology; 19 K-theory |
| 05 Analysis | 26 Real functions; 30 Functions of a complex variable; 42 Harmonic analysis; 46 Functional analysis; 47 Operator theory; 37 Dynamical systems |
| 06 PDEs | 35 Partial differential equations; 76 Fluid mechanics |
| 07 Combinatorics | 05 Combinatorics |
| 08 Logic & Set Theory | 03 Mathematical logic and foundations |
| 09 Probability | 60 Probability theory and stochastic processes; 82 Statistical mechanics |
| 10 Theoretical CS | 68 Computer science; 94 Information and communication theory; 81P Quantum information |

### 4. arXiv category and ACM CCS mapping (external, map only)

| Topic | arXiv categories | ACM CCS 2012 |
|---|---|---|
| 01 | math.NT | — |
| 02 | math.GR, math.RA, math.RT, math.CT | — |
| 03 | math.AG, math.DG, math.MG, math.SG | — |
| 04 | math.GT, math.AT, math.KT | — |
| 05 | math.CA, math.CV, math.FA, math.OA, math.DS | — |
| 06 | math.AP | — |
| 07 | math.CO | — |
| 08 | math.LO | — |
| 09 | math.PR | — |
| 10 | cs.CC, cs.DS, cs.CR, quant-ph | Theory of computation (computational complexity, algorithm design, cryptography, quantum computation theory) |

Schemes `arxiv` and `acm-ccs`; Topic → term via `CLASSIFIED_AS {method: mapped}`.

### 5. Famous problem lists (project-defined, from the catalog)

| List | Size of the list | Pages mentioning |
|---|---:|---:|
| Millennium Prize Problems (Clay, 2000) | 7 | 39 (Clay 56) |
| Hilbert's problems (1900) | 23 | 171 |
| Smale's problems (1998) | 18 | 23 |
| Erdős problems | open-ended | 149 |

A mention is not membership. `PART_OF_LIST` is set only when the page states the problem *is* on
the list (e.g. "one of the seven Millennium Prize Problems", "Hilbert's tenth problem").
`PART_OF_LIST.method = list-matched`. Expected members: far fewer than the mention counts.

## Controlled code lists

### Existing in the catalog (4)

| Property | Values | Count |
|---|---|---|
| `Problem.status` | `open`, `partially-solved`, `solved-recently`, `empirically-supported` | 577 / 333 / 229 / 22 |
| `Problem.catalog_provenance` | `synthesized`, `verified` | 1,161 / 0 |
| `Problem.topic` | the 10 topic slugs | 1,161 |
| `section` (on every section-derived node) | `1`–`10` with the TEMPLATE.md names | — |

### Project-defined (6)

#### `CITES.role` — cleaned reference tag

Section 9 has 14,550 reference lines with **485 different tag spellings** (85 lines untagged).
Each tag is mapped by keyword, first match wins, original kept in `CITES.raw_tag`:

| Role | Keywords in the tag | Lines | CiTO |
|---|---|---:|---|
| `sota` | sota, recent, state, frontier, current, breakthrough, latest | 5,196 | cites-for-information |
| `foundational` | foundational, original, classic, seminal, historical, key, milestone, background | 4,842 | cites-as-authority |
| `survey` | survey, review, expository, lecture, notes | 2,226 | cites-as-recommended-reading |
| `related` | related, connection, context, see also, application | 569 | cites-for-information |
| `technique` | technique, method, structure, barrier, complexity, theory, tool | 390 | uses-method-in |
| `partial` | partial, special case, verified | 262 | cites-as-evidence |
| `computational` | computational, numerics, computer, algorithm, counterexample | 197 | cites-as-data-source |
| `book` | book, monograph, textbook | 169 | cites-as-recommended-reading |
| `other` | anything else (top: Reference 34, Extension 13, Bounds 12) | 614 | cites |
| `untagged` | no tag on the line | 85 | cites |

Target: `other` + `untagged` below 5% (now 4.8%). Rule order and keyword lists will live in code
and be tested.

#### `Problem.kind` — from the title

| Value | Rule (title contains) | Count |
|---|---|---:|
| `conjecture` | conjecture | 508 |
| `hypothesis` | hypothesis | 15 |
| `problem` | problem | 127 |
| `programme` | program | 6 |
| `theorem` | theorem, lemma | 36 |
| `question` | none of the above (e.g. "Infinitude of Wagstaff Primes") | 469 |

`kind_method = title-keyword`. `question` is large; a v2 rule may read section 1.

#### `Result.result_type` — from section 4 bullets (3,931 bullets on 654 pages)

| Value | Meaning | Count (first keyword rule) |
|---|---|---:|
| `bound` | an upper/lower bound or rate | 1,460 |
| `computational` | computer search, numerical verification | 378 |
| `special_case` | proved in some dimensions, classes or small cases | 291 |
| `conditional` | proved assuming another conjecture (e.g. GRH) | 249 |
| `counterexample` | disproved, refuted or a counterexample found | 91 |
| `other` | none of the rules matched | 1,462 |
| `summary` | page has no section 4 bullets; whole section kept as one Result | 507 pages |

`other` is 37%: the rules need a second pass before the build.

#### `RELATED_TO.kind`

`implies`, `implied_by`, `equivalent`, `generalizes`, `special_case`, `related`
(default when no relation word is in the sentence). `RELATED_TO.method = title-matched`.

#### `confidence` — on ResearchDirection and Result

`frontier-verify` (sentence carries `*(frontier — verify)*`, 2,283 flags) or `stated`.

#### `Problem.formalization`

`mentioned` (page names Lean, Coq/Rocq, Isabelle or mathlib: 29 pages) or `none-mentioned`.
Small, but it answers "which problems have machine-checked progress".

## How a value was decided

Every coded value that is our rule rather than the page's own field carries a `*_method`:
`title-keyword`, `tag-keyword`, `bullet-keyword`, `title-matched`, `list-matched`, `mapped`.
