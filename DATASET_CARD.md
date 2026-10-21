---
license: other
pretty_name: Maths Research Knowledge Graph
tags:
  - knowledge-graph
  - samyama
  - property-graph
  - mathematics
  - open-problems
  - research
language:
  - en
size_categories:
  - 10K<n<100K
---

# Dataset Card for `maths-research-kg`

**34,073 nodes. 78,162 edges. 1,161 open and hard problems in mathematics, what is proved toward
each, what blocks it, and how they connect, from 1 source.**

> Part of the **Samyama** ecosystem. This card describes the dataset; the repository
> holds the loader and source-data specifics.

## Summary

A property graph of the frontiers of mathematics, built from one pinned commit of the
[`samyama-ai/maths_research`](https://github.com/samyama-ai/maths_research) catalog: one page per
problem, in 10 fields, each with the same ten sections (statement, foundations, history, partial
results, obstacles, gap, current research, future directions, references, worked example).

| Part | Nodes | What it holds |
|---|---:|---|
| The catalog | 1,171 | 1,161 problems, 10 topics |
| What is known | 4,609 | 4,366 partial results (typed: bound, computational, conditional, …), 243 concepts |
| What blocks it | 6,085 | 4,924 obstacles, 1,161 gaps |
| What would close it | 9,397 | 5,074 current research directions, 4,323 future directions |
| Evidence | 12,700 | 11,539 cited papers (de-duplicated), 1,161 worked examples |
| Classification | 111 | 110 taxonomy terms (subtopics, MSC2020, arXiv, ACM CCS, famous lists), 1 data source |

**The graph records what the catalog says, not what is true.** Every catalog page is marked
`provenance: synthesized` and none is marked `verified`. Every node carries `provenance`,
`source`, `method` and, when it comes from one page, a `source_url` pinned to the commit.

## Intended use

- Exploring where open problems are, what blocks them, and which concepts, papers and problems
  they share across fields.
- Finding research leads: open problems with many partial results, problems linked to recently
  solved ones, computer-checked results not yet formalized.
- Demonstrating graph queries, loaders, MCP tools and agents on a research catalog.

## Not suitable for

- **Deciding whether a mathematical claim is true.** The pages are synthesized, and claims marked
  *(frontier — verify)* (on 2,283 bullets) are flagged by the catalog itself as unchecked.
- **Citation metrics.** Papers are counted only by how often the catalog cites them; no external
  citation counts are imported.
- **Questions about people.** There are no person nodes; author names are kept as written in the
  citation.
- **Anything after the pinned commit** (committed 2026-09-25).

## Structure

**12 node labels** -- Problem, Topic, Result, Obstacle, Gap, ResearchDirection, FutureDirection,
WorkedExample, Paper, Concept, TaxonomyTerm, DataSource

**14 edge types** -- IN_TOPIC, HAS_RESULT, HAS_OBSTACLE, HAS_GAP, HAS_RESEARCH, HAS_FUTURE,
HAS_EXAMPLE, CITES, INVOLVES, RELATED_TO, CLASSIFIED_AS, PART_OF_LIST, BROADER, FROM_SOURCE

| Label | Count | Comes from |
|---|---:|---|
| Problem | 1,161 | one catalog page each |
| Topic | 10 | `TAXONOMY.md` |
| Result | 4,366 | section 4 bullets |
| Obstacle | 4,924 | section 5 bullets |
| Gap | 1,161 | section 6 |
| ResearchDirection | 5,074 | section 7 bullets |
| FutureDirection | 4,323 | section 8 bullets |
| WorkedExample | 1,161 | section 10 |
| Paper | 11,539 | section 9 reference lines (14,550), merged by DOI or title + year |
| Concept | 243 | curated list, matched in sections 1, 2 and 5 |
| TaxonomyTerm | 110 | project taxonomies and mappings |
| DataSource | 1 | the catalog at the pinned commit |

| Edge | Count |
|---|---:|
| CITES | 14,550 |
| INVOLVES | 5,435 |
| HAS_RESEARCH | 5,074 |
| HAS_OBSTACLE | 4,924 |
| HAS_RESULT | 4,366 |
| HAS_FUTURE | 4,323 |
| CLASSIFIED_AS | 1,220 |
| IN_TOPIC, HAS_GAP, HAS_EXAMPLE | 1,161 each |
| RELATED_TO | 620 |
| BROADER | 51 |
| PART_OF_LIST | 44 |
| FROM_SOURCE | 34,072 |

Every property, code list and identifier is in [`docs/`](docs/): [`schema.md`](docs/schema.md),
[`ontology.md`](docs/ontology.md), [`taxonomy.md`](docs/taxonomy.md),
[`coding-systems.md`](docs/coding-systems.md), [`standards.md`](docs/standards.md).

## Provenance and licence

The repository's code is Apache 2.0. **That licence does not cover the data.** The frontmatter is
therefore `license: other`.

| Source | Supplies | Terms |
|---|---|---|
| [`samyama-ai/maths_research`](https://github.com/samyama-ai/maths_research) @ `6a4b298` | every node and edge except taxonomy codes | **no licence stated: open question** |
| MSC2020 (zbMATH Open / AMS) | 30 top-level codes, mapped per topic | CC BY-NC-SA; code numbers and names used as a mapping only |
| arXiv category taxonomy, ACM CCS 2012 | 25 categories, 1 concept, mapped per topic | public classification schemes; codes used as a mapping only |

No external records are imported: no zbMATH, MathSciNet, Wikidata or OEIS data, and no DOI is
looked up. Vocabularies (PROV-O, SKOS, Dublin Core, FOAF, Schema.org, CiTO, OntoMathPRO, OMDoc)
name and map things only; the 38 mappings are in [`schema/conformance.json`](schema/conformance.json).

This is a reading of the stated terms, made on 2026-10-21. It is not legal advice.

## How values are derived

Most values are the catalog's own words. Where a value is our rule over those words, the node or
edge says so in `method` or a `*_method` property.

- **Parsed as written:** status, dates, section text, reference lines, DOIs, arXiv ids.
- **Keyword rules:** `Problem.kind` from the title, `Result.result_type` from the bullet
  (2.6% stay `other`), `CITES.role` from the reference tag (4.8% `other` or untagged).
- **Curated lists:** the 243 concepts, subtopic keywords, famous-list membership (Millennium 6,
  Hilbert 6, Erdős 32, Smale 0).
- **Title-matched links:** `RELATED_TO` when one page writes another page's title (longest title
  wins); its `kind` (implies, equivalent, generalizes, …) is read from that sentence, and
  `implies` is kept only when the sentence says which side the page is on.

No LLM is used to extract anything.

## Personal and sensitive data

None beyond what is published in the catalog. There are no person nodes; names appear only inside
text (citations, history) as the catalog writes them.

## Reproducing

```bash
pip install -e ".[dev]"
python -m etl.download_data                          # clone the catalog at the pinned commit
python -m etl.build_graph                            # build/graph.json
python -m etl.conformance                            # check it against docs/
python -m etl.engine_load --url http://localhost:8097 --fresh
```

A snapshot (`.sgsnap`, 9.5 MB) is made by `python -m etl.snapshot export`; it is not published
and no downloaded data is committed to the repository.

## Known limitations

- **Every page is synthesized.** The graph inherits whatever the pages get wrong.
- **19 pairs of pages share a name.** Most are one problem filed in two topics (e.g. Schanuel's
  conjecture in 01 and 05); a few are different problems (Baker's conjecture in 01 and 05). Both
  are kept, as the catalog has them.
- **Subtopics cover 761 of 1,161 problems.** The catalog's scope lines do not cover every field.
- **The Yang–Mills mass gap has no page**, so 6 of the 7 Millennium problems are present.
- **Links are as good as the title match.** A page that names a problem without its exact title
  is not linked; 2 problems have no concept.
- **Classification is per topic.** No per-problem MSC2020 code is assigned (v2).

## Verification

- `python -m etl.conformance`: 44 checks of the ontology, vocabulary mappings, taxonomies, code
  lists, identifier formats and provenance rules; 0 fail, 3 documented warnings.
- `python -m benchmarks.scope_questions`: all 48 scope questions run on the engine; reference
  values are counted from the raw catalog files, not from the build. 48 of 48 pass
  ([`benchmarks/scope_results.md`](benchmarks/scope_results.md)).
- The counts on this card are checked against a fresh build by the test suite.

## Links

| | |
|---|---|
| Samyama Graph | [github.com/samyama-ai/samyama-graph](https://github.com/samyama-ai/samyama-graph) |
| The Book | [samyama-ai.github.io/samyama-graph-book](https://samyama-ai.github.io/samyama-graph-book/) |
| Contact | [samyama.dev/contact](https://samyama.dev/contact) |
