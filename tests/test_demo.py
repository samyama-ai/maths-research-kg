"""Tests for the demo script (no engine)."""
from __future__ import annotations

import re

from demo import demo


def test_story_has_ten_steps_and_one_refusal():
    assert len(demo.STORY) == 10
    assert all(step[2] in demo.BASIS for step in demo.STORY)
    assert [step[2] for step in demo.STORY].count("none") == 1


def test_no_inline_edge_filters():
    # engine 1.11.0 drops inline edge property filters under ORDER BY ... LIMIT (docs/engine-notes.md)
    for title, _, _, _, cypher in demo.STORY:
        assert not re.search(r"-\[\w*:\w+\s*\{", cypher), title


def test_write_cypher_and_cells(tmp_path):
    text = demo.write_cypher(tmp_path / "q.cypher").read_text(encoding="utf-8")
    assert text.count(";\n") == 10
    assert demo.cell(1234) == "1,234" and demo.cell(None) == "-"
    assert demo.cell("**Bold.** " + "x" * 100).startswith("Bold. ") and len(demo.cell("y" * 100)) == 44
