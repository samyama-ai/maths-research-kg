"""Load build/graph.json into a Samyama engine.

    python -m etl.engine_load --url http://localhost:8097 [--fresh]

Nodes go in with UNWIND + MERGE on id; edges with literal id matches, which use the id index
(on engine 1.11.0 an UNWIND row does not, and is ~1,000x slower; see dbms-research-kg).
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from samyama import SamyamaClient

GRAPH = Path(__file__).resolve().parent.parent / "build" / "graph.json"
SCHEMA = Path(__file__).resolve().parent.parent / "schema" / "maths_research_kg.cypher"


def cypher_string(value) -> str:
    value = str(value).replace("\\", "\\\\").replace("'", "\\'")
    return "'" + value.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t") + "'"


def cypher_literal(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return cypher_string(value)


def cypher_map(record: dict) -> str:
    """A map literal; None values are left out so the property reads as null."""
    return "{" + ", ".join(f"{k}: {cypher_literal(v)}" for k, v in record.items() if v is not None) + "}"


def chunks(items, size):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def load_nodes(client, label: str, records: list[dict], batch: int = 200) -> None:
    for part in chunks(records, batch):
        rows = "[" + ", ".join(cypher_map(r) for r in part) + "]"
        client.query(f"UNWIND {rows} AS row MERGE (n:{label} {{id: row.id}}) SET n += row")


def load_edges(client, rel: str, records: list[dict], batch: int = 50) -> None:
    for part in chunks(records, batch):
        var_of, matches, wheres, merges = {}, [], [], []
        for r in part:
            ends = ((r["source_label"], r["src"]), (r["target_label"], r["dst"]))
            for label, node_id in ends:
                if (label, node_id) not in var_of:
                    var = f"v{len(var_of)}"
                    var_of[(label, node_id)] = var
                    matches.append(f"({var}:{label})")
                    wheres.append(f"{var}.id = {cypher_string(node_id)}")
            props = {k: v for k, v in r.items() if k not in {"source_label", "src", "target_label", "dst"}}
            merges.append(f"MERGE ({var_of[ends[0]]})-[:{rel} {cypher_map(props)}]->({var_of[ends[1]]})")
        client.query(f"MATCH {', '.join(matches)} WHERE {' AND '.join(wheres)} {' '.join(merges)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default="http://localhost:8097")
    parser.add_argument("--fresh", action="store_true", help="delete every node first")
    args = parser.parse_args(argv)
    data = json.loads(GRAPH.read_text(encoding="utf-8"))
    client = SamyamaClient.connect(args.url)
    if args.fresh:
        client.query("MATCH (n) DETACH DELETE n")
    for line in SCHEMA.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("//"):
            client.query(line.rstrip(";"))
    start = time.time()
    for label, records in data["nodes"].items():
        load_nodes(client, label, records)
        print(f"[load] {label:18} {len(records):>7,} nodes  ({time.time() - start:.0f}s)")
    for rel, records in data["edges"].items():
        load_edges(client, rel, records)
        print(f"[load] {rel:18} {len(records):>7,} edges  ({time.time() - start:.0f}s)")
    print(f"[load] engine now: {client.status()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
