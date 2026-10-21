"""The counts on DATASET_CARD.md must match a fresh build."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from etl.build_graph import BUILD_DIR

CARD = Path(__file__).resolve().parent.parent / "DATASET_CARD.md"
GRAPH = BUILD_DIR / "graph.json"


@pytest.mark.skipif(not GRAPH.exists(), reason="run python -m etl.build_graph first")
def test_card_counts_match_the_build():
    data = json.loads(GRAPH.read_text(encoding="utf-8"))
    nodes = {k: len(v) for k, v in data["nodes"].items()}
    edges = {k: len(v) for k, v in data["edges"].items()}
    card = CARD.read_text(encoding="utf-8")
    num = lambda s: int(s.replace(",", ""))
    head = re.search(r"\*\*([\d,]+) nodes\. ([\d,]+) edges\.", card)
    assert (num(head.group(1)), num(head.group(2))) == (sum(nodes.values()), sum(edges.values()))
    for label, count in re.findall(r"^\| (\w+) \| ([\d,]+) \|", card, re.MULTILINE):
        if label in nodes:
            assert nodes[label] == num(count), label
        elif label in edges:
            assert edges[label] == num(count), label
    row = re.search(r"^\| IN_TOPIC, HAS_GAP, HAS_EXAMPLE \| ([\d,]+) each \|", card, re.MULTILINE)
    assert {edges[r] for r in ("IN_TOPIC", "HAS_GAP", "HAS_EXAMPLE")} == {num(row.group(1))}
