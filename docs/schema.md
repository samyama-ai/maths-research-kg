# Maths Research KG — schema v0.1

The physical model: every node label and edge type, with its properties and expected counts.
The meaning of each class is in [`ontology.md`](ontology.md); allowed values of coded properties
are in [`taxonomy.md`](taxonomy.md); id patterns and standards in [`standards.md`](standards.md); code formats in [`coding-systems.md`](coding-systems.md);
the questions this schema must answer are in [`scope.md`](scope.md).

Source: `samyama-ai/maths_research` @ `6a4b298`. Counts are measured on the pages and are
**targets**, to be re-checked after the first build.

## Summary

| | Count |
|---|---:|
| Node labels | 12 |
| Edge types | 14 |
| Expected nodes | ~36,300 (Paper counted before de-dup; Concept not counted) |
| Expected edges | ~37,100, plus one `FROM_SOURCE` per node (~73,000 in all) |

## Diagram

12 node labels and 14 edge types. Arrows point from the edge's start node to its end node;
`{…}` are edge properties.

```text
     (Topic)◄──IN_TOPIC────────────────────────┐
        │                                      │
    CLASSIFIED_AS {method}                     │
        ▼                                      │
 (TaxonomyTerm)──BROADER──►(TaxonomyTerm)      │
                                               │
 (Paper)◄──CITES {role, raw_tag, ordinal}──(Problem)──INVOLVES {method, section}──►(Concept)
                                               │
                                               ├──HAS_RESULT──►(Result)
                                               ├──HAS_OBSTACLE──►(Obstacle)
                                               ├──HAS_GAP──►(Gap)
                                               ├──HAS_RESEARCH──►(ResearchDirection)
                                               ├──HAS_FUTURE──►(FutureDirection)
                                               ├──HAS_EXAMPLE──►(WorkedExample)
                                               ├──CLASSIFIED_AS {method}──►(TaxonomyTerm)
                                               ├──PART_OF_LIST {number, method, evidence}──►(TaxonomyTerm)
                                               ├──RELATED_TO {kind, method, evidence, section}──►(Problem)  [title-matched]
                                               └──FROM_SOURCE──►(DataSource)  [every node]
```

Read it as the four parts of the [core question](scope.md#core-question): **what is known**
(Result, Concept), **what blocks it** (Obstacle, Gap), **what would close it** (ResearchDirection,
FutureDirection), and **how it connects** (RELATED_TO, Paper, TaxonomyTerm).

- `TaxonomyTerm` holds every scheme: subtopic, MSC2020, arXiv, ACM CCS, famous list. `BROADER` also
  links a subtopic term to its `Topic`.
- `FROM_SOURCE` starts at every node, not only Problem.

## Common properties

On every node (from [`ontology.md`](ontology.md#properties-every-thing-has)):

| Property | Type | Required |
|---|---|---|
| `id` | string, unique per label | yes |
| `provenance` | `catalog-synthesized` \| `schema-vocabulary` | yes |
| `source` | `maths_research` \| `project_schema` | yes |
| `method` | code (`parsed`, `title-matched`, `keyword-classified`, `list-matched`, `mapped`, `catalog`) | yes |
| `source_url` | URL at the pinned commit | yes (except TaxonomyTerm) |
| `retrieved_at`, `source_date` | `YYYY-MM-DD` | yes |

Section-derived nodes (Result, Obstacle, Gap, ResearchDirection, FutureDirection, WorkedExample)
also have `section` (int 1–10), `ordinal` (int, position in the section) and `text` (string,
LaTeX kept as written).

## Node labels

| Label | Key properties | Expected | Answers |
|---|---|---:|---|
| **Topic** | `id`, `slug`, `number`, `name`, `scope` | 10 | Q1–3 |
| **Problem** | `id`, `slug`, `title`, `status`, `kind`, `kind_method`, `catalog_provenance`, `first_added`, `last_reviewed`, `last_substantive_update`, `stale_since`, `statement` (section 1), `foundations` (section 2), `history` (section 3), `formalization`, `frontier_flags` (int) | 1,161 | Q4, Q6, Q16 |
| **DataSource** | `id`, `name`, `url`, `version` (commit SHA), `licence`, `retrieved_at` | 1 | Q40 |
| **Result** | + `result_type`, `result_type_method`, `confidence` | ~4,440 | Q11–15 |
| **Concept** | `id`, `name`, `aliases` (list) | open (list to curate; 443 raw candidates) | Q7, Q19, Q29, Q44 |
| **Obstacle** | section-node properties | ~4,700 | Q17–19 |
| **Gap** | section-node properties | 1,161 | Q9, Q41 |
| **ResearchDirection** | + `heading` (bold lead-in, normalised), `confidence` | ~5,000 | Q20–21, Q23 |
| **FutureDirection** | + `heading` | ~4,030 | Q22 |
| **WorkedExample** | section-node properties | 1,161 | Q8 |
| **Paper** | `id`, `raw_citation`, `title`, `authors` (string), `year` (int), `venue`, `doi`, `arxiv_id`, `parse_status` (`parsed` \| `partial` \| `raw`) | < 14,550 after de-dup | Q30–34 |
| **TaxonomyTerm** | `id`, `scheme` (`subtopic`, `msc2020`, `arxiv`, `acm-ccs`, `famous-list`), `notation`, `label` | ~120 (≈55 subtopic, ≈29 MSC, ≈25 arXiv, 1 ACM, 4 lists) | Q5, Q35–39 |

Notes:

- `Problem.status` and the dates are read from frontmatter. Dates stay `YYYY-MM` as in the catalog.
- Sections 1–3 are long prose, kept as text on Problem, not split into nodes.
- `Paper` is merged by `doi` when present, else by normalised title + year. The raw line is always kept.
- `Concept` stays empty in the first build if the list is not ready; the questions that need it stay [partly].

## Edge types

| Edge | From → To | Properties | Expected | Answers |
|---|---|---|---:|---|
| `IN_TOPIC` | Problem → Topic | — | 1,161 | Q1–3 |
| `HAS_RESULT` | Problem → Result | — | ~4,440 | Q11 |
| `HAS_OBSTACLE` | Problem → Obstacle | — | ~4,700 | Q17 |
| `HAS_GAP` | Problem → Gap | — | 1,161 | Q9 |
| `HAS_RESEARCH` | Problem → ResearchDirection | — | ~5,000 | Q20 |
| `HAS_FUTURE` | Problem → FutureDirection | — | ~4,030 | Q22 |
| `HAS_EXAMPLE` | Problem → WorkedExample | — | 1,161 | Q8 |
| `CITES` | Problem → Paper | `role`, `raw_tag`, `role_method`, `ordinal` | 14,550 | Q10, Q30–34 |
| `INVOLVES` | Problem → Concept | `method`, `section` | open | Q7, Q29 |
| `RELATED_TO` | Problem → Problem | `kind`, `method`, `evidence` (the sentence), `section` | ~750 | Q24–28, Q42 |
| `CLASSIFIED_AS` | Topic or Problem → TaxonomyTerm | `method` (`mapped` \| `keyword-classified`) | ~70 topic-level + subtopic links | Q5, Q35–36 |
| `PART_OF_LIST` | Problem → TaxonomyTerm (`famous-list`) | `number` (Hilbert 1–23, Smale 1–18), `method`, `evidence` | small (< 60) | Q37–39 |
| `BROADER` | TaxonomyTerm → TaxonomyTerm, or TaxonomyTerm → Topic (subtopics) | — | ~60 | Q5 |
| `FROM_SOURCE` | every node → DataSource | — | one per node | Q40 |

Direction rules:

- `RELATED_TO` goes from the page that **mentions** to the page **mentioned**. `kind` is read from
  the mentioning sentence, so `implies` means "this page says it implies the other one".
- `RELATED_TO` is never a self-loop. Between the same pair there is at most one edge per `kind`.

## Constraints and indexes

```cypher
// unique ids
CREATE CONSTRAINT FOR (n:Problem) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT FOR (n:Topic) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT FOR (n:Paper) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT FOR (n:TaxonomyTerm) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT FOR (n:Concept) REQUIRE n.id IS UNIQUE;
// lookups used by the scope questions
CREATE INDEX FOR (n:Problem) ON (n.status);
CREATE INDEX FOR (n:Problem) ON (n.kind);
CREATE INDEX FOR (n:Problem) ON (n.title);
CREATE INDEX FOR (n:Result) ON (n.result_type);
CREATE INDEX FOR (n:Paper) ON (n.doi);
CREATE INDEX FOR (n:TaxonomyTerm) ON (n.scheme, n.notation);
```

The exact syntax will be checked against the Samyama engine (as in dbms-research-kg's
`engine-notes.md`) when `schema/maths_research_kg.cypher` is written.

## Example queries

Q2: status per topic

```cypher
MATCH (p:Problem)-[:IN_TOPIC]->(t:Topic)
RETURN t.name, p.status, count(p) AS n ORDER BY t.name, n DESC
```

Q25: the hub problems

```cypher
MATCH (:Problem)-[:RELATED_TO]->(hub:Problem)
RETURN hub.title, count(*) AS mentioned_by ORDER BY mentioned_by DESC LIMIT 10
```

Q43: open problems with computer checks but no formalization

```cypher
MATCH (p:Problem {status: 'open', formalization: 'none-mentioned'})-[:HAS_RESULT]->(r:Result {result_type: 'computational'})
RETURN p.title, count(r) AS checks ORDER BY checks DESC
```

## Data sources

| Source | Licence | Contributes |
|---|---|---|
| `samyama-ai/maths_research` @ `6a4b298` | **none stated (open question)** | every node and edge except taxonomy codes |
| MSC2020, arXiv categories, ACM CCS 2012 | see [`standards.md`](standards.md#licences) | TaxonomyTerm codes and labels only (mapping) |

## Open decisions for v0.2

1. Concept list: who curates it, and how big (start from the 443 recurring bold terms)?
2. `result_type`: second rule pass to bring `other` below ~15%.
3. Should `RELATED_TO` also be made from section 3 "history" mentions, or only from sections 1, 2, 4–8?
4. Per-problem MSC2020 codes (v2).
5. Person nodes (v2).
