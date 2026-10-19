"""Build the Maths Research graph from the pinned catalog into build/graph.json.

    python -m etl.build_graph

Nodes and edges follow docs/schema.md v0.1. Every node carries the provenance fields of
docs/ontology.md; every coded value comes from etl/rules.py or etl/taxonomies.py.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from etl import rules, taxonomies
from etl.catalog import bullets, lead_in, paper_id, parse_reference, read_catalog
from etl.download_data import CATALOG_DIR, check_catalog, read_lock

BUILD_DIR = Path(__file__).resolve().parent.parent / "build"
SOURCE_URL = "https://github.com/samyama-ai/maths_research/blob/{sha}/{path}"
SECTION_NODES = {5: ("Obstacle", "HAS_OBSTACLE"), 7: ("ResearchDirection", "HAS_RESEARCH"),
                 8: ("FutureDirection", "HAS_FUTURE")}
LINK_SECTIONS = (1, 2, 3, 4, 5, 6, 7, 8)


class Graph:
    def __init__(self, base: dict):
        self.base = base
        self.nodes: dict[str, dict[str, dict]] = defaultdict(dict)
        self.edges: dict[str, dict[tuple, dict]] = defaultdict(dict)

    def node(self, node_label: str, node_id: str, method: str, url: str | None, /, **props) -> str:
        record = {"id": node_id, **self.base, "method": method, "source_url": url, **props}
        if node_label == "TaxonomyTerm":
            record.update(provenance="schema-vocabulary", source="project_schema")
        self.nodes[node_label].setdefault(node_id, record)
        return node_id

    def edge(self, rel: str, src: tuple[str, str], dst: tuple[str, str], key=(), **props) -> None:
        self.edges[rel].setdefault((src[1], dst[1], *key), {
            "source_label": src[0], "src": src[1], "target_label": dst[0], "dst": dst[1], **props})


def sentence_around(text: str, start: int, end: int) -> str:
    left = max(text.rfind(". ", 0, start), text.rfind("\n", 0, start)) + 1
    stops = [i for i in (text.find(". ", end), text.find("\n", end)) if i != -1]
    return text[left:min(stops) + 1 if stops else len(text)].strip()


def title_matcher(pages) -> tuple[re.Pattern, dict[str, str]]:
    """One regex over all titles, longest first, so "Generalized Riemann Hypothesis" wins over
    "Riemann Hypothesis". Titles shorter than 8 characters are left out (too ambiguous)."""
    by_title = {}
    for p in pages:
        t = re.sub(r"\s*\(.*?\)\s*", " ", p.title).strip()
        if len(t) >= 8:
            by_title.setdefault(t.lower(), p.id)
    alts = sorted(by_title, key=len, reverse=True)
    return re.compile(r"(?<![\w-])(" + "|".join(re.escape(t) for t in alts) + r")(?![\w-])", re.IGNORECASE), by_title


def build(root: Path = CATALOG_DIR) -> Graph:
    sha = check_catalog(root)
    lock = read_lock(root)
    base = {"provenance": "catalog-synthesized", "source": "maths_research",
            "retrieved_at": lock["fetched_at"][:10], "source_date": lock["commit_date"][:10]}
    g = Graph(base)
    url = lambda rel: SOURCE_URL.format(sha=sha, path=rel)
    pages = read_catalog(root)

    ds = g.node("DataSource", "datasource:maths_research", "catalog", lock["repo"],
                name="maths_research", version=sha, licence="none stated")

    # Taxonomies: topics, subtopics, MSC2020, arXiv, ACM CCS, famous lists.
    sub_patterns = []
    for t in taxonomies.read_topics(root):
        tid = g.node("Topic", f"topic:{t['slug']}", "catalog", url("TAXONOMY.md"), slug=t["slug"],
                     number=int(t["number"]), name=t["name"], scope=t["scope"])
        for i, phrase in enumerate(taxonomies.subtopics(t["scope"]), 1):
            sid = g.node("TaxonomyTerm", f"subtopic:{t['number']}.{i}", "catalog", url("TAXONOMY.md"),
                         scheme="subtopic", notation=f"{t['number']}.{i}", label=phrase)
            g.edge("BROADER", ("TaxonomyTerm", sid), ("Topic", tid))
            sub_patterns.append((sid, t["slug"], taxonomies.subtopic_pattern(phrase)))
        for code in taxonomies.TOPIC_MSC[t["slug"]]:
            mid = g.node("TaxonomyTerm", f"msc2020:{code}", "mapped", None, scheme="msc2020",
                         notation=code, label=taxonomies.MSC2020[code])
            g.edge("CLASSIFIED_AS", ("Topic", tid), ("TaxonomyTerm", mid), method="mapped")
            if len(code) > 2:
                parent = g.node("TaxonomyTerm", f"msc2020:{code[:2]}", "mapped", None, scheme="msc2020",
                                notation=code[:2], label=taxonomies.MSC2020[code[:2]])
                g.edge("BROADER", ("TaxonomyTerm", mid), ("TaxonomyTerm", parent))
        for code in taxonomies.TOPIC_ARXIV[t["slug"]]:
            aid = g.node("TaxonomyTerm", f"arxiv:{code}", "mapped", None, scheme="arxiv",
                         notation=code, label=code)
            g.edge("CLASSIFIED_AS", ("Topic", tid), ("TaxonomyTerm", aid), method="mapped")
        if t["slug"] in taxonomies.ACM_CCS:
            code, label = taxonomies.ACM_CCS[t["slug"]]
            cid = g.node("TaxonomyTerm", f"acm-ccs:{code}", "mapped", None, scheme="acm-ccs",
                         notation=code, label=label)
            g.edge("CLASSIFIED_AS", ("Topic", tid), ("TaxonomyTerm", cid), method="mapped")
    for code, label in taxonomies.FAMOUS_LISTS.items():
        g.node("TaxonomyTerm", f"list:{code}", "catalog", None, scheme="famous-list",
               notation=code, label=label)

    matcher, by_title = title_matcher(pages)
    for page in pages:
        rel_path = page.path.relative_to(root).as_posix()
        u = url(rel_path)
        s = page.sections
        whole = "\n".join(s.values())
        pid = g.node("Problem", page.id, "parsed", u, slug=page.id.split("/")[1], title=page.title,
                     status=page.front.get("status"), kind=rules.problem_kind(page.title),
                     kind_method="title-keyword", catalog_provenance=page.front.get("provenance"),
                     first_added=page.front.get("first_added"),
                     last_reviewed=page.front.get("last_reviewed"),
                     last_substantive_update=page.front.get("last_substantive_update"),
                     stale_since=page.front.get("stale_since") or None,
                     statement=s.get(1), foundations=s.get(2), history=s.get(3),
                     formalization=rules.formalization(whole),
                     frontier_flags=whole.count(rules.FRONTIER))
        P = ("Problem", pid)
        g.edge("IN_TOPIC", P, ("Topic", f"topic:{page.topic}"))

        # Section 4: results.
        items = bullets(s.get(4, ""))
        if items:
            for n, item in enumerate(items, 1):
                rid = g.node("Result", f"{pid}#s4-{n}", "parsed", u, section=4, ordinal=n, text=item,
                             result_type=rules.result_type(item), result_type_method="bullet-keyword",
                             confidence=rules.confidence(item))
                g.edge("HAS_RESULT", P, ("Result", rid))
        elif s.get(4):
            rid = g.node("Result", f"{pid}#s4", "parsed", u, section=4, ordinal=1, text=s[4],
                         result_type="summary", result_type_method="no-bullets",
                         confidence=rules.confidence(s[4]))
            g.edge("HAS_RESULT", P, ("Result", rid))

        # Sections 5, 7, 8: one node per bullet, or one for the whole section.
        for sec, (label, rel) in SECTION_NODES.items():
            items = bullets(s.get(sec, "")) or ([s[sec]] if s.get(sec) else [])
            for n, item in enumerate(items, 1):
                extra = {"heading": lead_in(item)} if sec in (7, 8) else {}
                if sec == 7:
                    extra["confidence"] = rules.confidence(item)
                nid = g.node(label, f"{pid}#s{sec}-{n}", "parsed", u, section=sec, ordinal=n, text=item, **extra)
                g.edge(rel, P, (label, nid))

        for sec, label, rel in ((6, "Gap", "HAS_GAP"), (10, "WorkedExample", "HAS_EXAMPLE")):
            if s.get(sec):
                nid = g.node(label, f"{pid}#s{sec}", "parsed", u, section=sec, ordinal=1, text=s[sec])
                g.edge(rel, P, (label, nid))

        # Section 9: papers.
        n = 0
        for line in s.get(9, "").splitlines():
            if not line.startswith("- "):
                continue
            n += 1
            ref = parse_reference(line)
            paper = g.node("Paper", paper_id(ref), "parsed", u, **{k: v for k, v in ref.items() if k != "raw_tag"})
            g.edge("CITES", P, ("Paper", paper), key=(n,), role=rules.role(ref["raw_tag"]),
                   raw_tag=ref["raw_tag"], role_method="tag-keyword", ordinal=n)

        # Subtopics, famous lists, related problems.
        head = " ".join([page.title, s.get(1, ""), s.get(2, "")])
        for sid, slug, pattern in sub_patterns:
            if slug == page.topic and pattern.search(head):
                g.edge("CLASSIFIED_AS", P, ("TaxonomyTerm", sid), method="keyword-classified")
        for code, number, evidence in rules.list_memberships(page.id, page.title, s.get(1, "")):
            g.edge("PART_OF_LIST", P, ("TaxonomyTerm", f"list:{code}"), number=number,
                   method="list-matched", evidence=evidence)
        for sec in LINK_SECTIONS:
            text = s.get(sec, "")
            for m in matcher.finditer(text):
                other = by_title[m.group(1).lower()]
                if other == pid:
                    continue
                sentence = sentence_around(text, m.start(), m.end())
                kind = rules.relation_kind(sentence)
                g.edge("RELATED_TO", P, ("Problem", other), key=(kind,), kind=kind,
                       method="title-matched", evidence=sentence[:500], section=sec)

    for label, nodes in g.nodes.items():
        if label != "DataSource":
            for node_id in nodes:
                g.edge("FROM_SOURCE", (label, node_id), ("DataSource", ds))
    return g


def write(g: Graph, path: Path) -> dict:
    data = {"nodes": {k: list(v.values()) for k, v in g.nodes.items()},
            "edges": {k: list(v.values()) for k, v in g.edges.items()}}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def summary(data: dict) -> str:
    lines = [f"{k:18} {len(v):>7,}" for k, v in sorted(data["nodes"].items())]
    lines.append(f"{'NODES':18} {sum(len(v) for v in data['nodes'].values()):>7,}")
    lines += [f"{k:18} {len(v):>7,}" for k, v in sorted(data["edges"].items())]
    lines.append(f"{'EDGES':18} {sum(len(v) for v in data['edges'].values()):>7,}")
    for label, prop in (("Problem", "kind"), ("Result", "result_type"), ("Problem", "formalization")):
        lines.append(f"{label}.{prop}: {dict(Counter(n[prop] for n in data['nodes'][label]).most_common())}")
    for rel, prop in (("CITES", "role"), ("RELATED_TO", "kind"), ("PART_OF_LIST", "dst")):
        lines.append(f"{rel}.{prop}: {dict(Counter(e[prop] for e in data['edges'][rel]).most_common())}")
    return "\n".join(lines)


def main() -> int:
    data = write(build(), BUILD_DIR / "graph.json")
    print(summary(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

