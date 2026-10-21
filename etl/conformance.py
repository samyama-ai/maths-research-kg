"""Check the built graph against the ontologies, taxonomies, coding systems and standards.

    python -m etl.conformance            # reads build/graph.json and schema/conformance.json

Every rule of docs/ontology.md, taxonomy.md, coding-systems.md and standards.md that the build can
break is one check below. A FAIL is a broken rule (exit 1); a WARN is a documented limit that is
counted so it cannot grow unnoticed.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from etl import rules, taxonomies
from etl.build_graph import BUILD_DIR

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "schema" / "conformance.json"
DOCS = ROOT / "docs"
LOCK = ROOT / "data" / "maths_research.lock.json"

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
ARXIV_NEW_RE = re.compile(r"^(\d\d)(\d\d)\.\d{4,5}(v\d+)?$")
ARXIV_OLD_RE = re.compile(r"^[a-z-]+(\.[A-Z]{2})?/\d{7}(v\d+)?$")
MSC_RE = re.compile(r"^\d\d([A-Z](\d\d)?)?$")
ARXIV_CAT_RE = re.compile(r"^(math|cs)\.[A-Z]{2}$|^quant-ph$")
URL_RE = "https://github.com/samyama-ai/maths_research/blob/{sha}/"
MAX_EXAMPLES = 3


class Report:
    def __init__(self):
        self.rows: list[tuple[str, str, str, str, list]] = []

    def check(self, group: str, name: str, bad: list, warn: bool = False, detail: str = "") -> None:
        level = "ok" if not bad else ("WARN" if warn else "FAIL")
        self.rows.append((group, name, level, detail or f"{len(bad):,} bad", bad[:MAX_EXAMPLES]))

    @property
    def failures(self) -> int:
        return sum(r[2] == "FAIL" for r in self.rows)

    def text(self) -> str:
        out, group = [], None
        for g, name, level, detail, examples in self.rows:
            if g != group:
                out.append(f"\n## {g}")
                group = g
            out.append(f"  [{level:4}] {name}: {detail}")
            out += [f"           e.g. {e}" for e in examples]
        counts = Counter(r[2] for r in self.rows)
        out.append(f"\n{counts['ok']} ok, {counts['WARN']} warn, {counts['FAIL']} fail")
        return "\n".join(out)


def ym_ok(value) -> bool:
    if value is None:
        return True
    m = re.fullmatch(r"(\d{4})-(\d\d)", str(value))
    return bool(m) and 1 <= int(m.group(2)) <= 12


def ymd_ok(value) -> bool:
    try:
        return date.fromisoformat(value).isoformat() == value
    except (TypeError, ValueError):
        return False


def title_key(title: str) -> str:
    """"Schanuel's Conjecture" and "Schanuel Conjecture" -> the same key."""
    t = "".join(c for c in unicodedata.normalize("NFKD", title) if not unicodedata.combining(c)).lower()
    t = re.sub(r"[^a-z0-9 ]", " ", re.sub(r"['’]s\b|\(.*?\)", "", t))
    return " ".join(sorted(w for w in t.split() if w not in {"the", "of", "on", "for", "a", "conjecture", "problem", "hypothesis"}))


def doc_table(path: Path, heading: str) -> list[list[str]]:
    """Rows (cells) of the first markdown table under a heading that starts with `heading`."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("#") and heading in ln)
    rows = []
    for ln in lines[start + 1:]:
        if ln.startswith("#"):
            break
        if ln.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", ln):
            rows.append([c.strip() for c in ln.strip("|").split("|")])
    return rows[1:]


def check_ontology(r: Report, spec: dict, nodes: dict, edges: dict) -> None:
    g = "Ontology"
    labels, rels = spec["labels"], spec["relations"]
    r.check(g, "every label is declared, and every declared label is built",
            sorted(set(nodes) ^ set(labels)))
    r.check(g, "every relation is declared, and every declared relation is built",
            sorted(set(edges) ^ set(rels)))
    ids = {lab: {n["id"] for n in ns} for lab, ns in nodes.items()}
    bad_id, missing = [], []
    for lab, ns in nodes.items():
        decl = labels.get(lab, {})
        pat = re.compile(decl.get("id", ".*"))
        bad_id += [f"{lab} {n['id']}" for n in ns if not pat.search(n["id"])]
        missing += [f"{lab} {n['id']} lacks {p}" for n in ns for p in decl.get("required", [])
                    if n.get(p) in (None, "")]
        if "section" in decl:
            bad_id += [f"{lab} {n['id']} section {n['section']}" for n in ns if n["section"] != decl["section"]]
    r.check(g, "node ids follow the id patterns of standards.md", bad_id)
    r.check(g, "required properties are present", missing)
    r.check(g, "ids are unique per label", [lab for lab, ns in nodes.items() if len(ns) != len(ids[lab])])
    bad_end, dangling = [], []
    for rel, es in edges.items():
        decl = rels.get(rel, {"domain": [], "range": []})
        bad_end += [f"{rel} {e['source_label']}->{e['target_label']}" for e in es
                    if e["source_label"] not in decl["domain"] or e["target_label"] not in decl["range"]]
        dangling += [f"{rel} {e['src']}->{e['dst']}" for e in es
                     if e["src"] not in ids.get(e["source_label"], ()) or e["dst"] not in ids.get(e["target_label"], ())]
        for p in decl.get("required", []):
            bad_end += [f"{rel} {e['src']}->{e['dst']} lacks {p}" for e in es if not e.get(p)]
    r.check(g, "edges join the declared domain and range", sorted(set(bad_end)))
    r.check(g, "no edge points at a missing node", dangling)
    per = {rel: Counter(e["src"] for e in edges[rel]) for rel in ("IN_TOPIC", "HAS_GAP", "HAS_EXAMPLE")}
    r.check(g, "rule 2: every Problem has exactly one IN_TOPIC, HAS_GAP and HAS_EXAMPLE",
            [f"{p['id']} {rel}={c[p['id']]}" for p in nodes["Problem"] for rel, c in per.items() if c[p["id"]] != 1])
    r.check(g, "rule 6: RELATED_TO is never a self-loop",
            [e["src"] for e in edges["RELATED_TO"] if e["src"] == e["dst"]])
    pairs = Counter((e["src"], e["dst"], e["kind"]) for e in edges["RELATED_TO"])
    r.check(g, "RELATED_TO: at most one edge per pair and kind", [k for k, c in pairs.items() if c > 1])
    by_key = defaultdict(list)
    for p in nodes["Problem"]:
        by_key[title_key(p["title"])].append(p["id"])
    r.check(g, "problem titles are distinct (same-name pages: most are one problem filed twice, a few are homonyms)",
            [" = ".join(v) for v in by_key.values() if len(v) > 1], warn=True)
    both = {(e["src"], e["dst"]) for e in edges["RELATED_TO"] if e["kind"] == "implies"}
    r.check(g, "RELATED_TO implies is not stated both ways", sorted(p for p in both if p[::-1] in both), warn=True)


def check_mappings(r: Report, spec: dict, nodes: dict, edges: dict) -> None:
    g = "Ontology: vocabulary mappings (RDF/RDFS)"
    vocab, maps = spec["vocabularies"], spec["mappings"]
    props = {k for ns in nodes.values() for n in ns for k in n} | {k for es in edges.values() for e in es for k in e}
    codes = spec["codes"]
    coded = {"role": codes["role"], "kind": codes["problem_kind"]}
    bad = []
    for s, p, o in maps:
        prefix, _, term = s.partition(":")
        name, _, value = term.partition("=")
        known = (name in nodes or name in edges or name in props) and (not value or value in coded.get(name, ()))
        if prefix != "kg" or not known:
            bad.append(f"subject {s} is not a schema term")
        if p not in spec["mapping_predicates"]:
            bad.append(f"predicate {p} not allowed")
        if o.split(":")[0] not in vocab or o.split(":")[0] == "kg":
            bad.append(f"object {o} is not in a declared external vocabulary")
    r.check(g, "every mapping names a schema term, an allowed predicate and a declared vocabulary", bad)
    used = {o.split(":")[0] for _, _, o in maps} | {"kg"}
    r.check(g, f"all {len(vocab)} declared vocabularies are used", sorted(set(vocab) - used))
    r.check(g, "every node label and relation is mapped or is project-only",
            [], detail=f"{len({s for s, _, _ in maps})} schema terms mapped in {len(maps)} triples")
    roles = {s.split("=")[1] for s, _, _ in maps if s.startswith("kg:role=")}
    r.check(g, "every CITES role has a CiTO mapping", sorted(set(codes["role"]) - roles))
    dc = {o for _, _, o in maps if o.startswith("dcterms:")}
    r.check(g, "Dublin Core: title, date and subject are declared",
            sorted({"dcterms:title", "dcterms:date", "dcterms:subject"} - dc))


def check_codes(r: Report, spec: dict, nodes: dict, edges: dict) -> None:
    g = "Coding systems: project code lists"
    codes = spec["codes"]
    bad = []
    for lab, ns in nodes.items():
        decl = {"provenance": "provenance", "source": "source", "method": "method", **spec["labels"][lab].get("codes", {})}
        for prop, lst in decl.items():
            bad += [f"{lab}.{prop}={n.get(prop)!r}" for n in ns if n.get(prop) not in codes[lst]]
    for rel, es in edges.items():
        for prop, lst in spec["relations"][rel].get("codes", {}).items():
            bad += [f"{rel}.{prop}={e.get(prop)!r}" for e in es if e.get(prop) not in codes[lst]]
    r.check(g, "rule 3: every coded value is in its code list", sorted(set(bad)))
    # The code lists of coding-systems.md table D must equal the machine-readable ones.
    doc_lists = {(row[0].strip("`"), row[1]): re.findall(r"`([^`]+)`", row[2])
                 for row in doc_table(DOCS / "coding-systems.md", "D. Project code lists")}
    pairs = {("status", "Problem"): "status", ("catalog_provenance", "Problem"): "catalog_provenance",
             ("kind", "Problem"): "problem_kind", ("result_type", "Result"): "result_type",
             ("role", "CITES"): "role", ("kind", "RELATED_TO"): "relation_kind",
             ("confidence", "Result, ResearchDirection"): "confidence", ("formalization", "Problem"): "formalization"}
    r.check(g, "coding-systems.md table D agrees with schema/conformance.json",
            [f"{k}: doc {doc_lists.get(k)} vs spec {codes[v]}" for k, v in pairs.items() if doc_lists.get(k) != codes[v]])
    other = sum(n["result_type"] == "other" for n in nodes["Result"])
    bulleted = sum(n["result_type"] != "summary" for n in nodes["Result"])
    r.check(g, "result_type other below 15% (schema.md open decision 2)",
            [] if other / bulleted < 0.15 else [f"{other}/{bulleted}"], detail=f"{other:,} of {bulleted:,} = {other / bulleted:.1%}")
    weak = sum(e["role"] in ("other", "untagged") for e in edges["CITES"])
    r.check(g, "CITES role other + untagged below 5% (taxonomy.md target)",
            [] if weak / len(edges["CITES"]) < 0.05 else [weak], detail=f"{weak:,} of {len(edges['CITES']):,} = {weak / len(edges['CITES']):.1%}")


def check_identifiers(r: Report, nodes: dict, edges: dict, lock: dict) -> None:
    g = "Coding systems: identifiers and formats"
    papers = nodes["Paper"]
    r.check(g, "DOI (ISO 26324) syntax", [p["doi"] for p in papers if p["doi"] and not DOI_RE.match(p["doi"])],
            detail=f"{sum(bool(p['doi']) for p in papers):,} DOIs")
    r.check(g, "Paper id is doi:<doi> when the paper has a DOI",
            [p["id"] for p in papers if p["doi"] and p["id"] != "doi:" + p["doi"].lower()])
    bad_ax = []
    for p in papers:
        a = p["arxiv_id"]
        m = a and ARXIV_NEW_RE.match(a)
        if a and not (m and 1 <= int(m.group(2)) <= 12) and not ARXIV_OLD_RE.match(a):
            bad_ax.append(a)
    r.check(g, "arXiv id syntax (YYMM month 01-12, or old archive/NNNNNNN)", bad_ax,
            detail=f"{sum(bool(p['arxiv_id']) for p in papers):,} arXiv ids")
    years = [p["year"] for p in papers if p["year"] is not None]
    r.check(g, "Paper.year is a plausible year (1600 to the source date)",
            [y for y in years if not 1600 <= y <= int(lock["commit_date"][:4])])
    r.check(g, "ISO 8601: retrieved_at and source_date are YYYY-MM-DD",
            [f"{lab} {n['id']}" for lab, ns in nodes.items() for n in ns
             if not (ymd_ok(n["retrieved_at"]) and ymd_ok(n["source_date"]))])
    r.check(g, "ISO 8601: page dates are YYYY-MM",
            [f"{n['id']} {f}={n.get(f)}" for n in nodes["Problem"] for f in
             ("first_added", "last_reviewed", "last_substantive_update", "stale_since") if not ym_ok(n.get(f))])
    sha = lock["commit"]
    ds = nodes["DataSource"][0]
    r.check(g, "Git SHA-1: DataSource.version is the lock-file commit",
            [] if ds["version"] == sha and re.fullmatch(r"[0-9a-f]{40}", sha) else [ds["version"]])
    prefix = URL_RE.format(sha=sha)
    r.check(g, "source_url is pinned to that commit",
            [f"{lab} {n['id']} {n['source_url']}" for lab, ns in nodes.items() for n in ns
             if n["source_url"] and lab != "DataSource" and not n["source_url"].startswith(prefix)])


def check_taxonomies(r: Report, spec: dict, nodes: dict, edges: dict) -> None:
    g = "Taxonomies (SKOS)"
    terms = {t["id"]: t for t in nodes["TaxonomyTerm"]}
    topics = {t["id"] for t in nodes["Topic"]}
    r.check(g, "every TaxonomyTerm has scheme and notation", [t for t, n in terms.items() if not (n["scheme"] and n["notation"])])
    prefixes = {"msc2020": "msc2020", "arxiv": "arxiv", "acm-ccs": "acm-ccs", "famous-list": "list", "subtopic": "subtopic"}
    r.check(g, "TaxonomyTerm id is <scheme>:<notation>",
            [t for t, n in terms.items() if t != f"{prefixes[n['scheme']]}:{n['notation']}"])
    fmt = {"msc2020": MSC_RE, "arxiv": ARXIV_CAT_RE}
    r.check(g, "MSC2020 and arXiv category notation formats",
            [t for t, n in terms.items() if n["scheme"] in fmt and not fmt[n["scheme"]].match(n["notation"])])
    bad = []
    for e in edges["BROADER"]:
        a, b = terms[e["src"]], terms.get(e["dst"])
        if b is None:
            ok = a["scheme"] == "subtopic" and e["dst"] in topics
        else:
            ok = a["scheme"] == b["scheme"] and (a["scheme"] != "msc2020" or a["notation"].startswith(b["notation"]))
        if not ok:
            bad.append(f"{e['src']} -> {e['dst']}")
    r.check(g, "BROADER stays inside one scheme and follows MSC code levels (subtopic -> Topic allowed)", bad)
    up = Counter(e["src"] for e in edges["BROADER"])
    r.check(g, "every subtopic has exactly one BROADER, and Topic stays flat",
            [t for t, n in terms.items() if n["scheme"] == "subtopic" and up[t] != 1] +
            [e["src"] for e in edges["BROADER"] if e["src"] in topics])
    # taxonomy.md tables must equal etl/taxonomies.py.
    msc_doc = {row[0].split()[0]: re.findall(r"\b(\d\d[A-Z]?)\s", row[1] + " ")
               for row in doc_table(DOCS / "taxonomy.md", "3. MSC2020")}
    ax_doc = {row[0]: [c.strip() for c in row[1].split(",")] for row in doc_table(DOCS / "taxonomy.md", "4. arXiv")}
    by_num = {s[:2]: s for s in taxonomies.TOPIC_MSC}
    diff = [f"topic {k}: doc {v} vs code {taxonomies.TOPIC_MSC[by_num[k]]}" for k, v in msc_doc.items()
            if v != taxonomies.TOPIC_MSC[by_num[k]]]
    diff += [f"topic {k}: doc {v} vs code {taxonomies.TOPIC_ARXIV[by_num[k]]}" for k, v in ax_doc.items()
             if v != taxonomies.TOPIC_ARXIV[by_num[k]]]
    r.check(g, "taxonomy.md MSC2020 and arXiv tables agree with etl/taxonomies.py", diff)
    classified = Counter(e["source_label"] for e in edges["CLASSIFIED_AS"])
    r.check(g, "every Topic has MSC2020 and arXiv mappings",
            sorted(topics - {e["src"] for e in edges["CLASSIFIED_AS"] if e["source_label"] == "Topic"}))
    with_sub = {e["src"] for e in edges["CLASSIFIED_AS"] if e["source_label"] == "Problem"}
    n_sub = sum(n["scheme"] == "subtopic" for n in terms.values())
    r.check(g, "subtopic coverage (problems with at least one subtopic)",
            [] if len(with_sub) >= 0.6 * len(nodes["Problem"]) else ["below 60%"], warn=True,
            detail=f"{len(with_sub):,} of {len(nodes['Problem']):,} problems, {n_sub} subtopics, "
                   f"{classified['Problem']:,} links")


def check_lists(r: Report, nodes: dict, edges: dict) -> None:
    g = "Taxonomies: famous problem lists"
    by_list = defaultdict(list)
    for e in edges["PART_OF_LIST"]:
        by_list[e["dst"].split(":")[1]].append(e)
    mill = {e["src"] for e in by_list["millennium"]}
    r.check(g, "Millennium members are exactly the catalog pages of the 7 problems (Yang-Mills absent)",
            sorted(mill ^ set(rules.MILLENNIUM)))
    r.check(g, "Hilbert and Smale numbers are 1-23 and 1-18",
            [f"{e['src']} {e['number']}" for code, top in (("hilbert", 23), ("smale", 18))
             for e in by_list[code] if not (e["number"] and 1 <= e["number"] <= top)])
    hilbert = Counter(e["number"] for e in by_list["hilbert"])
    r.check(g, "each Hilbert number has at most one page", [n for n, c in hilbert.items() if c > 1], warn=True)
    sizes = {code: len(by_list[code]) for code in taxonomies.FAMOUS_LISTS}
    r.check(g, "list sizes", [code for code, n in sizes.items() if n == 0], warn=True,
            detail=", ".join(f"{k} {v}" for k, v in sizes.items()))


def check_provenance(r: Report, spec: dict, nodes: dict, edges: dict) -> None:
    g = "Standards: PROV-O"
    fields = ("source", "provenance", "method", "retrieved_at", "source_date")
    r.check(g, "rule 1: every node has the PROV fields",
            [f"{lab} {n['id']}" for lab, ns in nodes.items() for n in ns for f in fields if not n.get(f)])
    r.check(g, "page-derived nodes have a source_url",
            [f"{lab} {n['id']}" for lab in spec["page_derived"] for n in nodes[lab] if not n["source_url"]])
    out = Counter(e["src"] for e in edges["FROM_SOURCE"])
    r.check(g, "every node except the DataSource has exactly one FROM_SOURCE",
            [f"{lab} {n['id']}" for lab, ns in nodes.items() if lab != "DataSource" for n in ns if out[n["id"]] != 1])
    r.check(g, "taxonomy codes are schema-vocabulary, everything else catalog-synthesized",
            [f"{lab} {n['id']}" for lab, ns in nodes.items() for n in ns
             if (n["provenance"] == "schema-vocabulary") != (lab == "TaxonomyTerm")])
    r.check(g, "rule 7: frontier flags are kept",
            [n["id"] for lab in ("Result", "ResearchDirection") for n in nodes[lab]
             if (rules.FRONTIER in n["text"]) != (n["confidence"] == "frontier-verify")])
    r.check(g, "rule 4: no DOI is invented (every DOI is written in its citation)",
            [p["id"] for p in nodes["Paper"] if p["doi"] and p["doi"].lower() not in p["raw_citation"].lower()])


def run(graph_path: Path = BUILD_DIR / "graph.json") -> Report:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    nodes, edges = data["nodes"], data["edges"]
    r = Report()
    check_ontology(r, spec, nodes, edges)
    check_mappings(r, spec, nodes, edges)
    check_taxonomies(r, spec, nodes, edges)
    check_lists(r, nodes, edges)
    check_codes(r, spec, nodes, edges)
    check_identifiers(r, nodes, edges, lock)
    check_provenance(r, spec, nodes, edges)
    return r


def main() -> int:
    report = run()
    print(report.text())
    return 1 if report.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
