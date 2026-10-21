# Maths Research Knowledge Graph

**34,073 nodes. 78,162 edges. 1,161 open and hard problems in mathematics, what is proved toward each, what blocks it, and how they connect, from 1 source.**

> Part of the **Samyama** ecosystem — loaded into and queried via the graph engine at [samyama-ai/samyama-graph](https://github.com/samyama-ai/samyama-graph).
> This repo holds the loader and source-data specifics for the KG.

<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-blue" alt="License"></a>

![Maths Research KG demo](demo/maths-research-kg.gif)

*Ten questions on the live graph, each tagged with what its answer rests on; see [`demo/`](demo/).*

---

We loaded the [`samyama-ai/maths_research`](https://github.com/samyama-ai/maths_research) catalog
(commit `6a4b298`, 10 topics) into one graph, then asked:

> *"Which mathematical concepts sit behind open problems in the most fields?"*

```cypher
MATCH (p:Problem {status: 'open'})-[:INVOLVES]->(c:Concept), (p)-[:IN_TOPIC]->(t:Topic)
RETURN c.name, count(DISTINCT t) AS topics, count(DISTINCT p) AS open_problems
ORDER BY topics DESC, open_problems DESC LIMIT 5
```

| concept | topics | open problems |
|---|---:|---:|
| lattice | 9 | 58 |
| abelian group | 9 | 26 |
| generating function | 9 | 17 |
| prime number | 8 | 78 |
| fourier transform | 8 | 40 |

**One query across every field.** Powered by [Samyama Graph](https://github.com/samyama-ai/samyama-graph).

---

## Schema

**Node labels** (12) -- Problem 1,161 · Topic 10 · Result 4,366 · Obstacle 4,924 · Gap 1,161 ·
ResearchDirection 5,074 · FutureDirection 4,323 · WorkedExample 1,161 · Paper 11,539 ·
Concept 243 · TaxonomyTerm 110 · DataSource 1

**Edge types** (14) -- IN_TOPIC · HAS_RESULT · HAS_OBSTACLE · HAS_GAP · HAS_RESEARCH · HAS_FUTURE ·
HAS_EXAMPLE · CITES 14,550 · INVOLVES 5,435 · RELATED_TO 620 · CLASSIFIED_AS 1,220 · PART_OF_LIST 44 ·
BROADER 51 · FROM_SOURCE 34,072

**Data sources** -- `samyama-ai/maths_research` @ `6a4b298` (licence: none stated; open question).
MSC2020, arXiv categories and ACM CCS are used as topic-level mappings only; no external records
are imported.

What the data is, where it comes from and what it is not for: [`DATASET_CARD.md`](DATASET_CARD.md).
The design is in [`docs/`](docs/) (ontology, taxonomy, coding systems, standards, scope, schema);
indexes are in [`schema/maths_research_kg.cypher`](schema/maths_research_kg.cypher).

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

python -m etl.download_data          # clone the catalog at the pinned commit into data/
python -m etl.build_graph            # parse it into build/graph.json (~25 s)
python -m etl.engine_load --url http://localhost:8097 --fresh   # load into Samyama (~80 s)
python -m etl.conformance            # check the graph against docs/ (ontology, taxonomies, codes, standards)
python -m benchmarks.scope_questions # answer all 48 scope questions on the engine -> benchmarks/scope_results.md
python -m demo.demo                  # the narrated ten-question demo (demo/record.sh makes the GIF)
pytest                               # run tests
```

A local engine: `docker run -d -p 127.0.0.1:8097:8080 ghcr.io/samyama-ai/samyama-graph:latest samyama --host 0.0.0.0 --cors-origin https://graph.samyama.cloud`

## Structure
```
etl/          # download_data, catalog (parser), rules, taxonomies, concepts, build_graph, engine_load, conformance
schema/       # cypher indexes, conformance.json (declared labels, relations, code lists, vocabulary mappings)
mcp_server/   # MCP server exposing the KG
benchmarks/   # scope questions run on the engine
demo/         # the ten-question demo, its queries and the GIF
docs/         # design: ontology, taxonomy, coding systems, standards, scope, schema
tests/        # pytest
pyproject.toml
```

## Known limits (v1)

- Every catalog page is `provenance: synthesized`; the graph records what the pages say, not whether it is true.
- `RELATED_TO.kind` is read from the sentence that names the other problem; `implies` is kept only when the sentence says which side the page is on (13 edges), otherwise `related`.
- 19 pairs of pages share a name; most are one problem filed in two topics (e.g. Schanuel's conjecture in 01 and 05), a few are different problems (Baker's conjecture in 01 and 05). They are kept as the catalog has them.
- Subtopics cover 761 of 1,161 problems; Smale's list has no members, because no page names a Smale problem as its subject.
- On Samyama 1.11.0, filter edge properties in `WHERE`, not inline (see [`docs/engine-notes.md`](docs/engine-notes.md)).
- 2 problems have no concept (Casas-Alvero, Lempel-Ziv parallelization); the concept list is curated in `etl/concepts.py`.
- The Yang–Mills mass gap, one of the seven Millennium problems, has no page in the catalog.
