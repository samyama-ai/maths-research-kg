# Maths Research Knowledge Graph

**34,089 nodes. 77,351 edges. 1,161 open and hard problems in mathematics, what is proved toward each, what blocks it, and how they connect, from 1 source.**

> Part of the **Samyama** ecosystem — loaded into and queried via the graph engine at [samyama-ai/samyama-graph](https://github.com/samyama-ai/samyama-graph).
> This repo holds the loader and source-data specifics for the KG.

<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-blue" alt="License"></a>

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
ResearchDirection 5,074 · FutureDirection 4,323 · WorkedExample 1,161 · Paper 11,555 ·
Concept 243 · TaxonomyTerm 110 · DataSource 1

**Edge types** (14) -- IN_TOPIC · HAS_RESULT · HAS_OBSTACLE · HAS_GAP · HAS_RESEARCH · HAS_FUTURE ·
HAS_EXAMPLE · CITES 14,550 · INVOLVES 5,435 · RELATED_TO 673 · CLASSIFIED_AS 340 · PART_OF_LIST 44 ·
BROADER 51 · FROM_SOURCE 34,088

**Data sources** -- `samyama-ai/maths_research` @ `6a4b298` (licence: none stated; open question).
MSC2020, arXiv categories and ACM CCS are used as topic-level mappings only; no external records
are imported.

The design is in [`docs/`](docs/) (ontology, taxonomy, coding systems, standards, scope, schema);
indexes are in [`schema/maths_research_kg.cypher`](schema/maths_research_kg.cypher).

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

python -m etl.download_data          # clone the catalog at the pinned commit into data/
python -m etl.build_graph            # parse it into build/graph.json (~25 s)
python -m etl.engine_load --url http://localhost:8097 --fresh   # load into Samyama (~80 s)
python -m benchmarks.smoke_questions # answer 16 scope questions on the engine
pytest                               # run tests
```

A local engine: `docker run -d -p 127.0.0.1:8097:8080 ghcr.io/samyama-ai/samyama-graph:latest samyama --host 0.0.0.0 --cors-origin https://graph.samyama.cloud`

## Structure
```
etl/          # download_data, catalog (parser), rules, taxonomies, concepts, build_graph, engine_load
schema/       # cypher indexes
mcp_server/   # MCP server exposing the KG
benchmarks/   # scope questions run on the engine
docs/         # design: ontology, taxonomy, coding systems, standards, scope, schema
tests/        # pytest
pyproject.toml
```

## Known limits (v1)

- Every catalog page is `provenance: synthesized`; the graph records what the pages say, not whether it is true.
- `RELATED_TO.kind` is read from the sentence that names the other problem, so a few `implies` edges point the other way.
- 2 problems have no concept (Casas-Alvero, Lempel-Ziv parallelization); the concept list is curated in `etl/concepts.py`.
- The Yang–Mills mass gap, one of the seven Millennium problems, has no page in the catalog.
