"""Tests for the catalog parser and the coding rules (no network, no engine)."""
from __future__ import annotations

from etl import rules
from etl.build_graph import title_matcher
from etl.catalog import (
    Page,
    bullets,
    lead_in,
    paper_id,
    parse_frontmatter,
    parse_reference,
    split_sections,
)


def test_frontmatter_and_sections():
    text = ('---\nid: 01-number-theory/x\ntitle: "X Conjecture"\nstatus: open   # comment\n---\n\n# X\n\n'
            "## 1. Problem Statement\n\nClaim.\n\n## 9. Key References\n\n- **[Survey]** A. *T.* J, 2001.\n")
    front, body = parse_frontmatter(text)
    assert front == {"id": "01-number-theory/x", "title": "X Conjecture", "status": "open"}
    sections = split_sections(body)
    assert sections[1] == "Claim." and sections[9].startswith("- **[Survey]**")


def test_bullets_keep_continuation_lines_and_lead_in():
    items = bullets("Intro.\n\n- **Numerics.** first\n  more\n* second\n")
    assert items == ["**Numerics.** first\n  more", "second"]
    assert lead_in(items[0]) == "Numerics"
    assert bullets("only prose") == []


def test_reference_parse_and_identity():
    ref = parse_reference("- **[SOTA / Recent]** Stewart, C. L., & Yu, K. *On the abc conjecture.* "
                          "Mathematische Annalen, 2001. https://doi.org/10.1007/S002080100235")
    assert ref["raw_tag"] == "SOTA / Recent" and ref["year"] == 2001
    assert ref["title"] == "On the abc conjecture" and ref["parse_status"] == "parsed"
    assert paper_id(ref) == "doi:10.1007/s002080100235"
    no_doi = parse_reference("- **[Survey]** Granville, A. *It's as easy as abc.* Notices, 2002.")
    same = parse_reference("- **[Foundational]** Granville, A. *It's as Easy as ABC* AMS Notices 2002")
    assert paper_id(no_doi) == paper_id(same)          # merged by title + year
    assert parse_reference("- **[Survey]** arXiv:2101.01234 preprint")["arxiv_id"] == "2101.01234"


def test_role_rules():
    assert rules.role("Foundational") == "foundational"
    assert rules.role("SOTA / Recent") == "sota"
    assert rules.role("Survey / Book") == "survey"
    assert rules.role("Weird") == "other"
    assert rules.role(None) == "untagged"


def test_kind_result_and_relation_rules():
    assert rules.problem_kind("abc Conjecture") == "conjecture"
    assert rules.problem_kind("Infinitude of Wagstaff Primes") == "question"
    assert rules.result_type("Verified up to 10^13 by computer search") == "computational"
    assert rules.result_type("Assuming GRH, the bound holds") == "conditional"
    assert rules.result_type("A counterexample was found in 2019") == "counterexample"
    assert rules.relation_kind("Andrica's conjecture implies Legendre's conjecture.") == "implies"
    assert rules.relation_kind("RH is equivalent to Λ ≤ 0") == "equivalent"
    assert rules.relation_kind("see also the twin prime conjecture") == "related"


def test_famous_lists_need_membership_not_mention():
    assert rules.list_memberships("10-theoretical-cs/p-vs-np", "P vs NP", "")[0][0] == "millennium"
    assert rules.list_memberships("x/euler", "Euler Regularity", "Like the Millennium Prize Problem...") == []
    hit = rules.list_memberships("x/h10", "Hilbert's Tenth Problem", "")
    assert hit[0][:2] == ("hilbert", 10)
    assert rules.numbered_problem("Hilbert's 14th problem asks", "Hilbert", 23) == 14
    assert rules.numbered_problem("Hilbert's 99th problem", "Hilbert", 23) is None


def test_title_match_prefers_the_longest_title():
    pages = [Page(path=None, id="a/rh", topic="a", front={"title": "Riemann Hypothesis"}),
             Page(path=None, id="a/grh", topic="a", front={"title": "Generalized Riemann Hypothesis"})]
    matcher, by_title = title_matcher(pages)
    found = [by_title[m.group(1).lower()] for m in matcher.finditer("Assuming the Generalized Riemann Hypothesis")]
    assert found == ["a/grh"]


def test_formalization_and_confidence():
    assert rules.formalization("formalised in Lean 4") == "mentioned"
    assert rules.formalization("a formalism for lean manufacturing") == "none-mentioned"
    assert rules.confidence("new bound *(frontier — verify)*") == "frontier-verify"


def test_concept_matching():
    from etl import concepts
    names = {name for name, _ in concepts.table()}
    assert "elliptic curve" in names and len(names) == len(concepts.table())   # no duplicates
    pat = concepts.pattern("navier-stokes equations", ["navier-stokes"])
    assert pat.search(concepts.strip_math("the 3D Navier–Stokes equations"))   # en-dash
    padic = concepts.pattern("p-adic number", ["p-adic"])
    assert padic.search(concepts.strip_math("over the $p$-adic integers"))
    assert not concepts.pattern("knot", []).search("knotted")                  # whole words only
    assert concepts.pattern("elliptic curve", []).search("Elliptic Curves over Q")  # case, plural
    assert concepts.concept_id("Calabi-Yau manifold") == "concept:calabi-yau-manifold"


def test_result_type_falls_back_to_named_case():
    assert rules.result_type_with_method("**$p$-solvable groups:** true, by Fong reduction.") == \
        ("special_case", "bullet-lead-in")
    assert rules.result_type_with_method("Proven by Weil in the 1940s.") == ("special_case", "bullet-lead-in")
    assert rules.result_type_with_method("WASEP with small asymmetry (Bertini 1997).") == ("other", "bullet-keyword")
    assert rules.result_type_with_method("Upper bound O(n log n)") == ("bound", "bullet-keyword")
