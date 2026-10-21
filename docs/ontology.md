# Ontology

What kinds of thing the Maths Research KG holds, how they relate, what must always be true of
them, and how they line up with nine published vocabularies.

This is the conceptual model. Property lists and counts will be in [`schema.md`](schema.md); the
allowed values of each coded property are in [`taxonomy.md`](taxonomy.md); identifiers and
external standards are in [`standards.md`](standards.md); every coding system is in
[`coding-systems.md`](coding-systems.md).

It is written as prose and tables. No OWL or RDF file is published: mappings to other vocabularies
are declared as triples and checked by the build (as in `dbms-research-kg`).

Source: `samyama-ai/maths_research` at commit `6a4b298fc057fe449dee31667c066c269c9209d4`
(1,161 problem pages, 10 topics). All counts below were measured on that commit.

## Scope

The graph answers one family of question: **where are the frontiers of mathematics, what has been
proved toward each one, what blocks it, and how are the problems connected across fields?**

| Domain | Classes |
|---|---|
| The catalog | Topic, Problem, DataSource |
| What is known | Result, Concept |
| What blocks it | Obstacle, Gap |
| What would close it | ResearchDirection, FutureDirection |
| Evidence | Paper, WorkedExample |

One class, **TaxonomyTerm**, holds the codes of the taxonomies in [`taxonomy.md`](taxonomy.md)
(subtopics, MSC2020, arXiv, ACM CCS, famous problem lists).

**Out of scope for v1:** people (names in the pages are too noisy to extract reliably; 2,847
"Name (Year)" patterns, many of them "Theorem (1990)"), institutions, records from zbMATH,
MathSciNet, Wikidata or OEIS, citation counts, anything after the pinned commit, and the truth of
any mathematical claim. The graph records what the catalog *says*; every page is
`provenance: synthesized`.

## Properties every thing has

| Property | On | Values |
|---|---|---|
| `id` | every node | see [Identifiers](standards.md#identifiers) |
| `provenance` | every node | `catalog-synthesized` (read from a page), `schema-vocabulary` (a taxonomy code) |
| `source` | every node | `maths_research`, or `project_schema` for a taxonomy code |
| `method` | every node and derived edge | `parsed`, `title-matched`, `keyword-classified`, `list-matched`, `mapped`, `catalog` |
| `source_url` | every page-derived node | the catalog file at the pinned commit (Concepts and mapped codes come from no single page and have none) |
| `retrieved_at`, `source_date` | every node | from the source lock record, `YYYY-MM-DD` |

Edges carry no provenance fields of their own: an edge comes from the page of its start node.
Derived edges (`RELATED_TO`, `INVOLVES`, `CLASSIFIED_AS`, `PART_OF_LIST`) carry `method`; `CITES`
carries `role_method`.

Where a value is our rule over the page's words rather than the words themselves, `method` (and,
for coded values, a `*_method` property) says which rule.

## Classes

### The catalog

| Class | Definition | Identified by | Expected count |
|---|---|---|---:|
| **Topic** | One of the 10 numbered fields of `TAXONOMY.md`. | folder name, e.g. `01-number-theory` | 10 |
| **Problem** | One page: a conjecture, problem, hypothesis or question, with status, statement and sections. | frontmatter `id`, e.g. `01-number-theory/abc-conjecture` | 1,161 |
| **DataSource** | The catalog itself at the pinned commit. | `datasource:maths_research` | 1 |

### What is known

| Class | Definition | Comes from | Expected count |
|---|---|---|---:|
| **Result** | One proved, verified or conditional partial result toward a problem. Has `result_type`. | section 4 bullets | ~4,440 (3,931 bullets on 654 pages, plus one `summary` Result for each of the other 507 pages) |
| **Concept** | A named mathematical object or theory (zeta function, elliptic curve, forcing). Shared across problems. | sections 1, 2 and 5, matched against the curated list in `etl/concepts.py` | 243 (kept when on ≥ 3 pages) |

### What blocks it

| Class | Definition | Comes from | Expected count |
|---|---|---|---:|
| **Obstacle** | One reason current methods fail. | section 5 bullets (4,684), else paragraph | ~4,700 |
| **Gap** | The precise missing step between section 4 and section 1. One per problem. | section 6 | 1,161 |

### What would close it

| Class | Definition | Comes from | Expected count |
|---|---|---|---:|
| **ResearchDirection** | One active line of work as of 2026. Has `confidence`. | section 7 bullets (5,011) | ~5,000 |
| **FutureDirection** | One strategy proposed for the future. | section 8 bullets (4,032) | ~4,000 |

### Evidence

| Class | Definition | Comes from | Expected count |
|---|---|---|---:|
| **Paper** | One cited work, de-duplicated by DOI, else by normalised title + year. | section 9 lines (14,550) | < 14,550 after de-dup |
| **WorkedExample** | The concrete instance worked through on the page. One per problem. | section 10 | 1,161 |

### Things that look alike and are not

| Pair | Difference |
|---|---|
| Result vs Concept | A Result is a claim *about this problem* ("verified for the first 3×10¹² zeros"); a Concept is a shared object (the zeta function). |
| Obstacle vs Gap | Obstacles are many reasons methods fail; the Gap is the single missing step. |
| ResearchDirection vs FutureDirection | Section 7 = what people work on now; section 8 = what is proposed next. |
| Problem with `kind: theorem` vs Result | Some pages are titled after a theorem (36, e.g. "Casselman-Wallach Theorem"); they are still Problems (the catalog lists them for the technique or the gap they closed). |
| Topic vs Subtopic vs MSC code | Topic is the catalog's folder; Subtopic is a catalog scope line under it; an MSC code is an external classification we map to. |

## Relations

| Relation | From → To | Meaning | Method |
|---|---|---|---|
| `IN_TOPIC` | Problem → Topic | the page's folder | catalog |
| `HAS_RESULT` | Problem → Result | section 4 | parsed |
| `HAS_OBSTACLE` | Problem → Obstacle | section 5 | parsed |
| `HAS_GAP` | Problem → Gap | section 6 | parsed |
| `HAS_RESEARCH` | Problem → ResearchDirection | section 7 | parsed |
| `HAS_FUTURE` | Problem → FutureDirection | section 8 | parsed |
| `HAS_EXAMPLE` | Problem → WorkedExample | section 10 | parsed |
| `CITES {role}` | Problem → Paper | section 9 line, with its cleaned role tag | parsed |
| `INVOLVES` | Problem → Concept | concept named in section 2 | list-matched |
| `RELATED_TO {kind, evidence}` | Problem → Problem | another page's title appears in this page; `kind` from the sentence (implies / equivalent / generalizes / special-case / related) | title-matched + keyword-classified |
| `CLASSIFIED_AS` | Topic or Problem → TaxonomyTerm | subtopic, MSC2020, arXiv, ACM CCS code | mapped / keyword-classified |
| `PART_OF_LIST` | Problem → TaxonomyTerm | Millennium, Hilbert, Smale, Erdős list | list-matched |
| `BROADER` | TaxonomyTerm → TaxonomyTerm | SKOS hierarchy inside one scheme (e.g. MSC `11M` → `11`) | catalog / mapped |
| `FROM_SOURCE` | every node → DataSource | provenance | catalog |

Measured evidence for `RELATED_TO`: 756 title mentions on 468 pages, 215 across topics. Pages
containing the relation words: "implies" 572, "equivalent to" 327, "generaliz…" 89, "special case
of" 22. A relation word only sets `kind` when it is in the same sentence as the matched title;
otherwise `kind: related`. `implies` and `implied_by` also need the sentence to say which side
the page itself is on ("this conjecture implies X" vs "X implies this conjecture"); when it does
not, the kind falls back to `related`.

## Rules

1. Every node has an `id`, `provenance`, `source` and `method`; every page-derived node has a `source_url` at the pinned commit.
2. Every Problem has exactly one `IN_TOPIC`, one `HAS_GAP`, one `HAS_EXAMPLE`, and a `status` from the four catalog values.
3. Every coded property takes a value from [`taxonomy.md`](taxonomy.md); unknown values fail the build.
4. No DOI, arXiv id or MSC code is invented; a Paper without a DOI keeps its raw citation.
5. No external records are imported. External vocabularies name and map things only.
6. A `RELATED_TO` edge never points from a problem to itself, and records its `evidence` (the sentence).
7. Claims flagged `*(frontier — verify)*` (2,283) keep `confidence: frontier-verify`.

## Alignment with other vocabularies

| # | Vocabulary | Used for | Example mapping |
|---|---|---|---|
| 1 | Project ontology (`kg:`) | all labels and relations above | `kg:Problem`, `kg:HAS_GAP` |
| 2 | PROV-O | provenance fields | `source_url` ~ `prov:wasDerivedFrom`; DataSource `rdfs:subClassOf prov:Entity` |
| 3 | SKOS | taxonomies and code lists | TaxonomyTerm `rdfs:subClassOf skos:Concept`; `BROADER` ~ `skos:broader`; code `notation` ~ `skos:notation` |
| 4 | Dublin Core | titles, dates, subjects | `title` ~ `dcterms:title`; `CLASSIFIED_AS` ~ `dcterms:subject` |
| 5 | FOAF | (people deferred to v2) | declared, used by Paper authors string only |
| 6 | Schema.org | papers | Paper `rdfs:subClassOf schema:ScholarlyArticle` |
| 7 | CiTO | citation roles | `CITES {role: foundational}` ~ `cito:citesAsAuthority`; `survey` ~ `cito:citesAsRecommendedReading` |
| 8 | OntoMathPRO | maths classes | Problem ~ OntoMathPRO "Problem", Concept ~ "Mathematical object", Result ~ "Statement" (class IRIs to be looked up when the mappings are declared) |
| 9 | OMDoc | statement kinds | `kind: conjecture` ~ `omdoc:conjecture`; `kind: theorem` ~ `omdoc:theorem`; WorkedExample ~ `omdoc:example` |

The mappings are declared as 38 subject–predicate–object triples in
[`schema/conformance.json`](../schema/conformance.json) and checked by `python -m etl.conformance`.

Wikidata is used as a reading reference only (e.g. Q1201, Riemann hypothesis) and is not counted.

## Changing the ontology

A new class or relation needs: a definition here, a row in `schema.md`, its values in
`taxonomy.md` if coded, a mapping row above, and a scope question that needs it.
