# Maths Research KG — schema v1.0

The physical model: every node label and edge type, with its properties and expected counts.
The meaning of each class is in [`ontology.md`](ontology.md); allowed values of coded properties
are in [`taxonomy.md`](taxonomy.md); id patterns and standards in [`standards.md`](standards.md); code formats in [`coding-systems.md`](coding-systems.md);
the questions this schema must answer are in [`scope.md`](scope.md).

Source: `samyama-ai/maths_research` @ `6a4b298`. "Built" counts are the graph made by
`python -m etl.build_graph`; `python -m etl.conformance` checks it against this page and
[`schema/conformance.json`](../schema/conformance.json).

## Summary

| | Count |
|---|---:|
| Node labels | 12 |
| Edge types | 14 |
| Built nodes | 34,073 |
| Built edges | 78,162 (44,090 plus one `FROM_SOURCE` per node) |

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
| `source_url` | URL at the pinned commit | page-derived nodes (not Concept, not mapped TaxonomyTerm) |
| `retrieved_at`, `source_date` | `YYYY-MM-DD` | yes |

Section-derived nodes (Result, Obstacle, Gap, ResearchDirection, FutureDirection, WorkedExample)
also have `section` (int 1–10), `ordinal` (int, position in the section) and `text` (string,
LaTeX kept as written).

## Node labels

| Label | Key properties | Built | Answers |
|---|---|---:|---|
| **Topic** | `id`, `slug`, `number`, `name`, `scope` | 10 | Q1–3 |
| **Problem** | `id`, `slug`, `title`, `status`, `kind`, `kind_method`, `catalog_provenance`, `first_added`, `last_reviewed`, `last_substantive_update`, `stale_since`, `statement` (section 1), `foundations` (section 2), `history` (section 3), `formalization`, `frontier_flags` (int) | 1,161 | Q4, Q6, Q16 |
| **DataSource** | `id`, `name`, `source_url` (repo), `version` (commit SHA), `licence`, `retrieved_at` | 1 | Q40 |
| **Result** | + `result_type`, `result_type_method`, `confidence` | 4,366 | Q11–15 |
| **Concept** | `id`, `name`, `aliases` (`; `-separated), `problem_count`, `topic_count` | 243 | Q7, Q19, Q29, Q44 |
| **Obstacle** | section-node properties | 4,924 | Q17–19 |
| **Gap** | section-node properties | 1,161 | Q9, Q41 |
| **ResearchDirection** | + `heading` (bold lead-in), `confidence` | 5,074 | Q20–21, Q23 |
| **FutureDirection** | + `heading` | 4,323 | Q22 |
| **WorkedExample** | section-node properties | 1,161 | Q8 |
| **Paper** | `id`, `raw_citation`, `title`, `authors` (string), `year` (int), `venue`, `doi`, `arxiv_id`, `parse_status` (`parsed` \| `partial` \| `raw`) | 11,539 | Q30–34 |
| **TaxonomyTerm** | `id`, `scheme` (`subtopic`, `msc2020`, `arxiv`, `acm-ccs`, `famous-list`), `notation`, `label`, `terms` (subtopics) | 110 (50 subtopic, 30 MSC, 25 arXiv, 1 ACM, 4 lists) | Q5, Q35–39 |

Notes:

- `Problem.status` and the dates are read from frontmatter. Dates stay `YYYY-MM` as in the catalog.
- Sections 1–3 are long prose, kept as text on Problem, not split into nodes.
- `Paper` is merged by `doi` when present, else by normalised title + year. The raw line is always kept.
- `Concept` is a curated list of 246 names in `etl/concepts.py`; 243 match at least 3 pages and are kept.

## Edge types

| Edge | From → To | Properties | Built | Answers |
|---|---|---|---:|---|
| `IN_TOPIC` | Problem → Topic | — | 1,161 | Q1–3 |
| `HAS_RESULT` | Problem → Result | — | 4,366 | Q11 |
| `HAS_OBSTACLE` | Problem → Obstacle | — | 4,924 | Q17 |
| `HAS_GAP` | Problem → Gap | — | 1,161 | Q9 |
| `HAS_RESEARCH` | Problem → ResearchDirection | — | 5,074 | Q20 |
| `HAS_FUTURE` | Problem → FutureDirection | — | 4,323 | Q22 |
| `HAS_EXAMPLE` | Problem → WorkedExample | — | 1,161 | Q8 |
| `CITES` | Problem → Paper | `role`, `raw_tag`, `role_method`, `ordinal` | 14,550 | Q10, Q30–34 |
| `INVOLVES` | Problem → Concept | `method`, `section`, `sections`, `in_obstacles` | 5,435 | Q7, Q19, Q29 |
| `RELATED_TO` | Problem → Problem | `kind`, `method`, `evidence` (the sentence), `section` | 620 | Q24–28, Q42 |
| `CLASSIFIED_AS` | Topic or Problem → TaxonomyTerm | `method` (`mapped` \| `keyword-classified`) | 1,220 (55 topic-level, 1,165 subtopic) | Q5, Q35–36 |
| `PART_OF_LIST` | Problem → TaxonomyTerm (`famous-list`) | `number` (Hilbert 1–23, Smale 1–18), `method`, `evidence` | 44 | Q37–39 |
| `BROADER` | TaxonomyTerm → TaxonomyTerm, or TaxonomyTerm → Topic (subtopics) | — | 51 | Q5 |
| `FROM_SOURCE` | every node → DataSource | — | 34,072 | Q40 |

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

Samyama 1.11.0 has no constraints and takes `CREATE INDEX ON :Label(prop)`; the indexes it
actually runs are in [`schema/maths_research_kg.cypher`](../schema/maths_research_kg.cypher). Engine
quirks found while testing are in [`engine-notes.md`](engine-notes.md).

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

## Decisions made in v1.0

1. Concept list: curated in `etl/concepts.py` (246 names, 243 kept), matched in sections 1, 2 and 5.
2. `result_type`: second pass by bold lead-in; `other` is 2.6%.
3. `RELATED_TO` is made from sections 1–8 (history included).

Still open (v2): per-problem MSC2020 codes, Person nodes.
