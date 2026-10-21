# Engine notes (Samyama 1.11.0)

Behaviour of `ghcr.io/samyama-ai/samyama-graph` 1.11.0 found while loading and testing this graph.

## 1. Inline edge filters are dropped under `ORDER BY … LIMIT`

An inline property map on a relationship is ignored when the query groups and then sorts with a
limit. The same filter written in `WHERE` works.

```cypher
// wrong: 26 (every citation of the book, any role)
MATCH (p:Problem)-[c:CITES {role: 'survey'}]->(x:Paper)
RETURN x.id, count(c) AS n ORDER BY n DESC LIMIT 1

// right: 17
MATCH (p:Problem)-[c:CITES]->(x:Paper) WHERE c.role = 'survey'
RETURN x.id, count(c) AS n ORDER BY n DESC LIMIT 1
```

Without `ORDER BY … LIMIT` both forms give 17; `count(*)` over the inline form gives the right
total (2,226). Inline **node** filters (`(p:Problem {status: 'open'})`) were correct in every
query we tried. So `benchmarks/` always filters edge properties in `WHERE`.

## 2. Loading

- `MATCH … WHERE n.id = '…'` with literal ids uses the index; matching on `UNWIND` rows does not,
  so `etl/engine_load.py` writes edges as literal-match `MERGE`s in batches of 50.
- `/api/snapshot/import` adds to whatever is loaded; import only into an empty engine.
- Variable-length paths (`-[:RELATED_TO*1..3]->`) and `length(p)` work; `OPTIONAL MATCH … WHERE`
  and `EXISTS { … }` work.
