"""Tests for the conformance rules and the rules they caught (no engine; the full check runs on
build/graph.json when it exists)."""
from __future__ import annotations

import json

import pytest

from etl import conformance, rules
from etl.build_graph import BUILD_DIR, sentence_around, title_matcher
from etl.catalog import Page, parse_reference


def test_spec_is_self_consistent():
    spec = json.loads(conformance.SPEC.read_text(encoding="utf-8"))
    assert set(spec["page_derived"]) <= set(spec["labels"])
    for rel in spec["relations"].values():
        assert set(rel["domain"]) | set(rel["range"]) <= set(spec["labels"])
    for label in spec["labels"].values():
        assert set(label.get("codes", {}).values()) <= set(spec["codes"])
    assert {o.split(":")[0] for _, _, o in spec["mappings"]} == set(spec["vocabularies"]) - {"kg"}


def test_year_skips_ids_and_page_ranges():
    year = lambda line: parse_reference(line)["year"]
    assert year("- **[Recent]** Y. Li. *Canonical bases.* arXiv:1501.00688 (2015).") == 2015
    assert year("- **[Key]** P. Anderson. *Absence of Diffusion.* Phys. Rev. 109, 1492–1505, 1958.") == 1958
    assert year("- **[F]** A. Lenstra (eds.). *The NFS.* Lecture Notes in Mathematics 1554, Springer, 1993.") == 1993


def test_implies_needs_the_side_of_the_page():
    s = "Andrica's conjecture implies Legendre's conjecture."
    assert rules.directed_kind(s, s.index("Legendre"), "Andrica's Conjecture") == "implies"
    s = "The ABC conjecture implies Pillai's conjecture."
    assert rules.directed_kind(s, s.index("ABC"), "Pillai's Conjecture") == "implied_by"
    s = "Schanuel's conjecture implies the algebraic independence of e and pi."
    assert rules.directed_kind(s, 0, "Six Exponentials Theorem") == "related"
    s = "Hence the conjecture implies the Hopf conjecture."
    assert rules.directed_kind(s, s.index("Hopf"), "Singer Conjecture") == "implies"


def test_title_match_stops_at_dashes():
    pages = [Page(path=None, id="a/lang", topic="a", front={"title": "Lang Conjecture"})]
    matcher, _ = title_matcher(pages)
    assert not matcher.search("the weak Bombieri–Lang conjecture implies uniform bounds")
    assert matcher.search("Lang conjecture (1974)")
    sentence, pos = sentence_around("First. Then the Lang conjecture holds. End", 16, 31)
    assert sentence == "Then the Lang conjecture holds." and sentence[pos:].startswith("Lang")


def test_famous_list_rules():
    ch = "Hilbert's first problem (1900) asked for a proof of CH."
    assert rules.list_memberships("x/ch", "Continuum Hypothesis", ch)[0][:2] == ("hilbert", 1)
    assert rules.list_memberships("x/sic", "SIC-POVM", "an instance of Hilbert's 12th problem") == []
    assert rules.list_memberships("x/e", "Erdős-Szekeres Conjecture", "")[0][0] == "erdos"
    assert rules.list_memberships("x/r", "Random Walk on Erdős–Rényi Graphs", "") == []
    assert rules.list_memberships("x/h", "Empty Hexagon", "Erdős (1978) asked whether")[0][0] == "erdos"


def test_title_key_and_doc_tables():
    assert conformance.title_key("Schanuel's Conjecture") == conformance.title_key("Schanuel Conjecture")
    rows = conformance.doc_table(conformance.DOCS / "coding-systems.md", "D. Project code lists")
    assert len(rows) == 10


@pytest.mark.skipif(not (BUILD_DIR / "graph.json").exists(), reason="run python -m etl.build_graph first")
def test_built_graph_conforms():
    report = conformance.run()
    assert report.failures == 0, report.text()
