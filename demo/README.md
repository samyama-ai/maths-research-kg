# Demo

![Maths Research KG demo](maths-research-kg.gif)

Ten queries, one story: where the frontiers of mathematics are, what blocks them, and how the
problems connect across fields. Each answer is tagged with what it rests on, because some values
are the catalog's words and some are our rules over them.

| # | Question | Rests on |
|---:|---|---|
| 1 | How open is mathematics? | parsed from the page |
| 2 | Which fields have the most open problems? | parsed from the page |
| 3 | Which concepts sit behind open problems in the most fields? | our fixed rule |
| 4 | What blocks Navier-Stokes regularity? | parsed from the page |
| 5 | Which open problems have the most computer checks? | our fixed rule |
| 6 | Which problems are named by the most other problems? | title-matched link |
| 7 | Which problems would the abc conjecture settle? | title-matched link |
| 8 | How does a combinatorics problem reach the Riemann hypothesis? | title-matched link |
| 9 | Which Millennium Prize Problems are in the catalog? | our fixed rule |
| 10 | Who is the leading expert on the abc conjecture? | no such data: the graph returns nothing |

**Parsed from the page** is the catalog's own words. **Our fixed rule** is a curated list or
keyword rule of this project (concepts, result types, famous-list membership). A **title-matched
link** is RELATED_TO: one page writes another page's title, and the kind (implies, equivalent, …)
is read from that sentence. **No such data** is a question the graph must refuse.

The ten queries in full are in [`queries.cypher`](queries.cypher), written from the demo itself by
`python -m demo.demo --write-cypher`; edit `STORY` in `demo.py`, not the file.

## Run it

With a server that holds the graph (`python -m etl.engine_load --fresh` or `python -m etl.snapshot import`):

```bash
python -m demo.demo --url http://127.0.0.1:8097            # paced, as recorded
python -m demo.demo --no-pause --url http://127.0.0.1:8097 # no pacing
python -m demo.demo --write-cypher                          # the ten queries -> demo/queries.cypher
```

Every number is read from the graph at run time, including the counts on the title card.

## The recording

One tall screen with the whole report, so nothing scrolls off; the layout and recording settings
of the other Samyama KGs. The finished report is held for 14 seconds before the GIF starts again.
Recorded on 2026-10-21 against the full graph, 34,073 nodes and 78,162 edges, on a Samyama 1.11.0
server.

Needs `asciinema` (`pip install asciinema==2.4.0`), `agg` (github.com/asciinema/agg) and a server
that holds the graph:

```bash
demo/record.sh                                    # http://127.0.0.1:8097
AGG=/path/to/agg demo/record.sh                   # agg not on PATH
GIF_HOLD=20 demo/record.sh                        # a longer hold at the end
```

The height of the recording is measured from the demo's own output. Record it again whenever the
graph changes. The `.cast` file it records from is git-ignored.
