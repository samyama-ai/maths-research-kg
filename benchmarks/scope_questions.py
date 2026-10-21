"""Run all 48 scope questions (docs/scope.md) on the loaded engine and check each answer.

    python -m benchmarks.scope_questions --url http://localhost:8097    # writes benchmarks/scope_results.md

Each question is a Cypher query plus a check. Where a check needs a reference value, the value is
counted from the raw catalog files (frontmatter lines, folder sizes, section headings) without the
build's parser, so a parser bug cannot pass its own test. Edge properties are filtered with WHERE,
never inline: on engine 1.11.0 an inline edge filter is dropped under ORDER BY ... LIMIT
(docs/engine-notes.md). Questions 45-48 must be refused: their
check proves the graph holds nothing that would answer them.
"""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

from samyama import SamyamaClient

from etl.download_data import CATALOG_DIR

OUT = Path(__file__).resolve().parent / "scope_results.md"
ABC = "01-number-theory/abc-conjecture"
RH = "01-number-theory/riemann-hypothesis"
PNP = "10-theoretical-cs/p-vs-np"
# A section-9 tag that the role rules map to `foundational` (etl/rules.py ROLE_RULES: survey and book win).
FOUNDATIONAL_TAG = r"^- \*\*\[(?![^\]]*(survey|review|exposit|lecture|notes|book|monograph))[^\]]*" \
                   r"(foundational|original|classic|seminal|historical|key|milestone|background)"


def raw_catalog(root: Path = CATALOG_DIR) -> dict:
    """Reference counts read straight from the files."""
    files = sorted(f for f in (root / "topics").glob("*/*.md") if f.name != "README.md")
    texts = {f: f.read_text(encoding="utf-8") for f in files}
    status = Counter(re.search(r"^status:\s*([\w-]+)", t, re.MULTILINE).group(1) for t in texts.values())
    return {
        "problems": len(files),
        "per_topic": Counter(f.parent.name for f in files),
        "status": status,
        "solved_recently": Counter(f.parent.name for f, t in texts.items()
                                   if re.search(r"^status:\s*solved-recently", t, re.MULTILINE)),
        "with_example": sum(bool(re.search(r"^## 10\.", t, re.MULTILINE)) for t in texts.values()),
        "with_gap": sum(bool(re.search(r"^## 6\.", t, re.MULTILINE)) for t in texts.values()),
        "lean": sum(bool(re.search(r"\b(Lean|Coq|Rocq|Isabelle|mathlib|Mathlib)\b", t)) for t in texts.values()),
        "refs": sum(len(re.findall(r"^- ", t.split("## 9.", 1)[1].split("\n## ", 1)[0], re.MULTILINE))
                    for t in texts.values() if "## 9." in t),
        "with_foundational": sum(bool(re.search(FOUNDATIONAL_TAG, t.split("## 9.", 1)[-1], re.IGNORECASE | re.MULTILINE))
                                 for t in texts.values() if "## 9." in t),
        "last_reviewed": max(re.search(r"^last_reviewed:\s*(\S+)", t, re.MULTILINE).group(1) for t in texts.values()),
    }


def total(rows, col=-1):
    return sum(r[col] for r in rows)


def q(mark, text, cypher, check=None):
    return {"mark": mark, "text": text, "cypher": cypher, "check": check or (lambda rows, raw: (bool(rows), ""))}


QUESTIONS = {
    1: q("yes", "Problems per topic",
         "MATCH (p:Problem)-[:IN_TOPIC]->(t:Topic) RETURN t.slug, count(p) AS n ORDER BY n DESC",
         lambda rows, raw: ({r[0]: r[1] for r in rows} == dict(raw["per_topic"]), "equals the folder sizes")),
    2: q("yes", "Status, overall and per topic",
         "MATCH (p:Problem) RETURN p.status, count(p) AS n ORDER BY n DESC",
         lambda rows, raw: ({r[0]: r[1] for r in rows} == dict(raw["status"]), "equals the frontmatter status lines")),
    3: q("yes", "Topic with the most recently solved problems",
         ("MATCH (p:Problem {status: 'solved-recently'})-[:IN_TOPIC]->(t:Topic) "
          "RETURN t.slug, count(p) AS n ORDER BY n DESC LIMIT 3"),
         lambda rows, raw: (rows[0][1] == max(raw["solved_recently"].values()), "top count equals the files")),
    4: q("partly", "Problems by kind (from the title)",
         "MATCH (p:Problem) RETURN p.kind, count(p) AS n ORDER BY n DESC",
         lambda rows, raw: (total(rows) == raw["problems"], "every problem has one kind")),
    5: q("partly", "Subtopics with the most open problems",
         ("MATCH (p:Problem {status: 'open'})-[:CLASSIFIED_AS]->(s:TaxonomyTerm {scheme: 'subtopic'}) "
          "RETURN s.notation, s.label, count(p) AS n ORDER BY n DESC LIMIT 5")),
    6: q("yes", "Statement, status and kind of the abc conjecture",
         f"MATCH (p:Problem {{id: '{ABC}'}}) RETURN p.title, p.status, p.kind, p.statement",
         lambda rows, raw: (rows[0][1] == "open" and "a + b = c" in rows[0][3].replace("$", ""), "status open; statement read")),
    7: q("partly", "Concepts of the abc conjecture",
         f"MATCH (:Problem {{id: '{ABC}'}})-[:INVOLVES]->(c:Concept) RETURN c.name ORDER BY c.name"),
    8: q("yes", "Worked example of the abc conjecture (and coverage)",
         "MATCH (:Problem)-[:HAS_EXAMPLE]->(w:WorkedExample) RETURN count(w)",
         lambda rows, raw: (rows[0][0] == raw["with_example"], "one per page with a section 10")),
    9: q("yes", "Gap of the Riemann hypothesis (and coverage)",
         "MATCH (:Problem)-[:HAS_GAP]->(g:Gap) RETURN count(g)",
         lambda rows, raw: (rows[0][0] == raw["with_gap"], "one per page with a section 6")),
    10: q("yes", "Papers cited by the abc conjecture, with role",
          f"MATCH (:Problem {{id: '{ABC}'}})-[c:CITES]->(x:Paper) RETURN c.ordinal, c.role, x.title ORDER BY c.ordinal"),
    11: q("yes", "Partial results toward the Riemann hypothesis",
          f"MATCH (:Problem {{id: '{RH}'}})-[:HAS_RESULT]->(r:Result) RETURN r.ordinal, r.result_type, r.text ORDER BY r.ordinal"),
    12: q("partly", "Problems with the most computer checks",
          ("MATCH (p:Problem)-[:HAS_RESULT]->(r:Result {result_type: 'computational'}) "
           "RETURN p.title, count(r) AS n ORDER BY n DESC LIMIT 5")),
    13: q("partly", "Conditional results per topic",
          ("MATCH (t:Topic)<-[:IN_TOPIC]-(p:Problem)-[:HAS_RESULT]->(r:Result {result_type: 'conditional'}) "
           "RETURN t.slug, count(r) AS n ORDER BY n DESC")),
    14: q("partly", "Problems with a counterexample result",
          ("MATCH (p:Problem)-[:HAS_RESULT]->(r:Result {result_type: 'counterexample'}) "
           "RETURN p.title, p.status, count(r) AS n ORDER BY n DESC LIMIT 5")),
    15: q("partly", "Best-known bounds per topic",
          ("MATCH (t:Topic)<-[:IN_TOPIC]-(p:Problem)-[:HAS_RESULT]->(r:Result {result_type: 'bound'}) "
           "RETURN t.slug, count(DISTINCT p) AS problems, count(r) AS bounds ORDER BY bounds DESC")),
    16: q("yes", "Problems that mention Lean / Coq / Isabelle",
          "MATCH (p:Problem {formalization: 'mentioned'}) RETURN count(p)",
          lambda rows, raw: (rows[0][0] == raw["lean"], "equals a grep of the files")),
    17: q("yes", "Principal obstacles for P vs NP",
          f"MATCH (:Problem {{id: '{PNP}'}})-[:HAS_OBSTACLE]->(o:Obstacle) RETURN o.ordinal, o.text ORDER BY o.ordinal"),
    18: q("yes", "Obstacles per problem, by topic",
          ("MATCH (t:Topic)<-[:IN_TOPIC]-(p:Problem)-[:HAS_OBSTACLE]->(o:Obstacle) "
           "RETURN t.slug, count(DISTINCT p) AS problems, count(o) AS obstacles ORDER BY obstacles DESC")),
    19: q("partly", "Concepts named in obstacles across the most topics",
          ("MATCH (p:Problem)-[r:INVOLVES]->(c:Concept), (p)-[:IN_TOPIC]->(t:Topic) WHERE r.in_obstacles = true "
           "RETURN c.name, count(DISTINCT t) AS topics, count(DISTINCT p) AS problems "
           "ORDER BY topics DESC, problems DESC LIMIT 5")),
    20: q("yes", "Current research on the Riemann hypothesis",
          f"MATCH (:Problem {{id: '{RH}'}})-[:HAS_RESEARCH]->(r:ResearchDirection) RETURN r.heading, r.confidence ORDER BY r.ordinal"),
    21: q("yes", "Frontier-verify claims, and the problems with the most",
          "MATCH (p:Problem) RETURN p.title, p.frontier_flags ORDER BY p.frontier_flags DESC LIMIT 3"),
    22: q("yes", "Future work proposed for the abc conjecture",
          f"MATCH (:Problem {{id: '{ABC}'}})-[:HAS_FUTURE]->(f:FutureDirection) RETURN f.ordinal, f.text ORDER BY f.ordinal"),
    23: q("partly", "Research directions that recur across problems",
          ("MATCH (p:Problem)-[:HAS_RESEARCH]->(r:ResearchDirection) WHERE r.heading IS NOT NULL "
           "RETURN r.heading, count(DISTINCT p) AS problems ORDER BY problems DESC LIMIT 8")),
    24: q("partly", "Problems that mention the Riemann hypothesis",
          (f"MATCH (p:Problem)-[r:RELATED_TO]->(:Problem {{id: '{RH}'}}) "
           "RETURN p.title, r.kind, r.evidence"),
          lambda rows, raw: (all(re.search(r"(?<!generali[sz]ed )(?<!grand )riemann hypothesis", r[2], re.IGNORECASE)
                                 for r in rows), "every evidence names RH itself, not GRH")),
    25: q("partly", "Hub problems (named by the most others)",
          ("MATCH (p:Problem)-[:RELATED_TO]->(h:Problem) RETURN h.title, count(DISTINCT p) AS n "
           "ORDER BY n DESC LIMIT 5")),
    26: q("partly", "What implies, or is equivalent to, the Riemann hypothesis",
          (f"MATCH (p:Problem)-[r:RELATED_TO]->(:Problem {{id: '{RH}'}}) WHERE r.kind IN ['implies', 'equivalent'] "
           "RETURN p.title, r.kind")),
    27: q("partly", "Most connected topic pairs",
          ("MATCH (ta:Topic)<-[:IN_TOPIC]-(a:Problem)-[:RELATED_TO]->(b:Problem)-[:IN_TOPIC]->(tb:Topic) "
           "WHERE ta.id <> tb.id RETURN ta.slug, tb.slug, count(*) AS n ORDER BY n DESC LIMIT 5")),
    28: q("partly", "Shortest chain of related problems from the Erdős discrepancy problem to RH",
          ("MATCH p = (:Problem {id: '07-combinatorics/erdos-discrepancy-problem'})-[:RELATED_TO*1..3]->"
           f"(:Problem {{id: '{RH}'}}) RETURN length(p) AS hops ORDER BY hops LIMIT 1"),
          lambda rows, raw: (rows[0][0] == 2, "2 hops, via the Chowla conjecture")),
    29: q("partly", "Problems sharing the most concepts with the Riemann hypothesis",
          (f"MATCH (:Problem {{id: '{RH}'}})-[:INVOLVES]->(c:Concept)<-[:INVOLVES]-(p:Problem) "
           "RETURN p.title, count(c) AS shared ORDER BY shared DESC LIMIT 5")),
    30: q("yes", "Papers cited by the most problems",
          "MATCH (p:Problem)-[:CITES]->(x:Paper) RETURN x.id, x.title, count(DISTINCT p) AS n ORDER BY n DESC LIMIT 5"),
    31: q("yes", "Papers cited across the most topics",
          ("MATCH (t:Topic)<-[:IN_TOPIC]-(:Problem)-[:CITES]->(x:Paper) "
           "RETURN x.title, count(DISTINCT t) AS topics ORDER BY topics DESC LIMIT 5")),
    32: q("yes", "Surveys covering the most problems",
          ("MATCH (p:Problem)-[c:CITES]->(x:Paper) WHERE c.role = 'survey' "
           "RETURN x.id, x.title, count(DISTINCT p) AS n ORDER BY n DESC LIMIT 5"),
          lambda rows, raw: (rows[0][2] == 17, "Kanamori is cited as a survey by 17 of its 26 citing pages")),
    33: q("yes", "References with a DOI or arXiv id",
          ("MATCH (:Problem)-[c:CITES]->(x:Paper) "
           "RETURN count(c) AS refs, count(x.doi) AS with_doi, count(x.arxiv_id) AS with_arxiv"),
          lambda rows, raw: (rows[0][0] == raw["refs"], "reference lines equal the section-9 bullets")),
    34: q("yes", "Problems that cite no foundational work",
          ("MATCH (p:Problem) OPTIONAL MATCH (p)-[c:CITES]->(:Paper) WHERE c.role = 'foundational' "
           "WITH p, count(c) AS f WHERE f = 0 RETURN count(p)"),
          lambda rows, raw: (rows[0][0] == raw["problems"] - raw["with_foundational"], "equals a scan of the reference tags")),
    35: q("yes", "MSC2020 areas of Number Theory, and problems under MSC 11",
          ("MATCH (m:TaxonomyTerm {id: 'msc2020:11'})<-[:CLASSIFIED_AS]-(:Topic)<-[:IN_TOPIC]-(p:Problem) "
           "RETURN m.label, count(p)"),
          lambda rows, raw: (rows[0][1] == raw["per_topic"]["01-number-theory"], "all number theory pages")),
    36: q("yes", "arXiv categories for a paper on P vs NP",
          (f"MATCH (:Problem {{id: '{PNP}'}})-[:IN_TOPIC]->(:Topic)-[:CLASSIFIED_AS]->(a:TaxonomyTerm {{scheme: 'arxiv'}}) "
           "RETURN a.notation ORDER BY a.notation"),
          lambda rows, raw: ("cs.CC" in [r[0] for r in rows], "includes cs.CC")),
    37: q("partly", "Millennium Prize Problems in the catalog",
          "MATCH (p:Problem)-[:PART_OF_LIST]->(:TaxonomyTerm {id: 'list:millennium'}) RETURN p.title, p.status",
          lambda rows, raw: (len(rows) == 6, "6 of 7; Yang-Mills has no page")),
    38: q("partly", "Hilbert's problems in the catalog, with status",
          ("MATCH (p:Problem)-[l:PART_OF_LIST]->(:TaxonomyTerm {id: 'list:hilbert'}) "
           "RETURN l.number, p.title, p.status ORDER BY l.number"),
          lambda rows, raw: ({r[0] for r in rows} >= {1, 12, 14}, "includes the 1st, 12th and 14th")),
    39: q("partly", "Erdős problems, by status",
          ("MATCH (p:Problem)-[:PART_OF_LIST]->(:TaxonomyTerm {id: 'list:erdos'}) "
           "RETURN p.status, count(p) AS n ORDER BY n DESC")),
    40: q("yes", "Source page, commit and method of a fact",
          (f"MATCH (r:Result {{id: '{RH}#s4-1'}})-[:FROM_SOURCE]->(d:DataSource) "
           "RETURN r.source_url, r.method, r.result_type_method, d.version"),
          lambda rows, raw: (rows[0][3] in rows[0][0], "the URL is pinned to the DataSource commit")),
    41: q("partly", "Open problems with many results but a short gap",
          ("MATCH (g:Gap)<-[:HAS_GAP]-(p:Problem {status: 'open'})-[:HAS_RESULT]->(r:Result) "
           "WITH p, g, count(r) AS results WHERE results >= 8 RETURN p.title, results, size(g.text) AS gap_chars "
           "ORDER BY gap_chars LIMIT 5")),
    42: q("partly", "Open problems linked to a recently solved one",
          ("MATCH (p:Problem {status: 'open'})-[:RELATED_TO]->(s:Problem {status: 'solved-recently'}) "
           "RETURN p.title, s.title LIMIT 5")),
    43: q("partly", "Open problems with computer checks but no formalization",
          ("MATCH (p:Problem {status: 'open', formalization: 'none-mentioned'})-[:HAS_RESULT]->"
           "(r:Result {result_type: 'computational'}) RETURN p.title, count(r) AS n ORDER BY n DESC LIMIT 5")),
    44: q("partly", "Concepts in the most open problems across 3 or more topics",
          ("MATCH (p:Problem {status: 'open'})-[:INVOLVES]->(c:Concept), (p)-[:IN_TOPIC]->(t:Topic) "
           "WITH c, count(DISTINCT t) AS topics, count(DISTINCT p) AS open_problems WHERE topics >= 3 "
           "RETURN c.name, topics, open_problems ORDER BY open_problems DESC LIMIT 5")),
    45: q("refuse", "Is the Riemann hypothesis true?",
          f"MATCH (p:Problem {{id: '{RH}'}}) RETURN p.status, p.catalog_provenance",
          lambda rows, raw: (rows[0] == ["open", "synthesized"], "graph holds only the catalog's status (open, synthesized)")),
    46: q("refuse", "Who is the leading expert on problem X?",
          "MATCH (n:Person) RETURN count(n)",
          lambda rows, raw: (rows[0][0] == 0, "no Person nodes")),
    47: q("refuse", "How many citations does paper P have?",
          "MATCH (x:Paper) WHERE x.citation_count IS NOT NULL OR x.cited_by IS NOT NULL RETURN count(x)",
          lambda rows, raw: (rows[0][0] == 0, "no citation counts imported")),
    48: q("refuse", "What happened on problem X after the pinned commit?",
          "MATCH (p:Problem) RETURN max(p.last_reviewed)",
          lambda rows, raw: (rows[0][0] <= raw["last_reviewed"] <= "2026-09", "nothing reviewed after the commit")),
}


def short(value, width=90) -> str:
    text = re.sub(r"\s+", " ", str(value))
    return text if len(text) <= width else text[:width - 1] + "…"


def run(url: str) -> tuple[list[dict], str]:
    client = SamyamaClient.connect(url)
    raw = raw_catalog()
    results, lines = [], ["# Scope questions: results", "",
                          ("Generated by `python -m benchmarks.scope_questions`. One query per question of "
                          "[`docs/scope.md`](../docs/scope.md); `check` compares the answer with the raw catalog "
                          "files where a reference value exists."), ""]
    for n, item in QUESTIONS.items():
        try:
            rows = [list(r) for r in client.query_readonly(item["cypher"]).records]
            ok, note = item["check"](rows, raw)
            error = None
        except Exception as exc:  # noqa: BLE001  a failed query or check is a failed question, not a crash
            rows, ok, note, error = [], False, "", f"{type(exc).__name__}: {exc}"
        results.append({"n": n, "ok": ok, "rows": len(rows)})
        lines += [f"## Q{n} [{item['mark']}] {item['text']}", f"```cypher\n{item['cypher']}\n```",
                  f"**{'pass' if ok else 'FAIL'}**, {len(rows)} rows" + (f": {note}" if note else "")
                  + (f"; {error}" if error else ""), ""]
        lines += [f"- {' | '.join(short(v, 60 if len(row) > 2 else 90) for v in row)}" for row in rows[:3]]
        lines.append("")
    passed = sum(r["ok"] for r in results)
    lines[5:5] = [f"**{passed} of {len(results)} questions pass.**", ""]
    return results, "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8097")
    results, text = run(parser.parse_args(argv).url)
    OUT.write_text(text + "\n", encoding="utf-8")
    for r in results:
        if not r["ok"]:
            print(f"FAIL Q{r['n']} ({r['rows']} rows)")
    print(f"{sum(r['ok'] for r in results)} of {len(results)} pass; wrote {OUT.relative_to(OUT.parent.parent)}")
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
