"""Run a first set of scope questions (docs/scope.md) against the loaded engine.

    python -m benchmarks.smoke_questions --url http://localhost:8097
"""
from __future__ import annotations

import argparse

from samyama import SamyamaClient

QUESTIONS = [
    ("Q1 problems per topic",
     "MATCH (p:Problem)-[:IN_TOPIC]->(t:Topic) RETURN t.name, count(p) AS n ORDER BY n DESC"),
    ("Q2 status overall",
     "MATCH (p:Problem) RETURN p.status, count(p) AS n ORDER BY n DESC"),
    ("Q3 most recently solved, by topic",
     "MATCH (p:Problem {status: 'solved-recently'})-[:IN_TOPIC]->(t:Topic) "
     "RETURN t.name, count(p) AS n ORDER BY n DESC LIMIT 3"),
    ("Q12 problems with the most computational results",
     "MATCH (p:Problem)-[:HAS_RESULT]->(r:Result {result_type: 'computational'}) "
     "RETURN p.title, count(r) AS n ORDER BY n DESC LIMIT 5"),
    ("Q16 formalization mentioned",
     "MATCH (p:Problem {formalization: 'mentioned'}) RETURN count(p) AS n"),
    ("Q21 most frontier flags",
     "MATCH (p:Problem) RETURN p.title, p.frontier_flags ORDER BY p.frontier_flags DESC LIMIT 3"),
    ("Q25 hub problems",
     "MATCH (:Problem)-[:RELATED_TO]->(h:Problem) RETURN h.title, count(*) AS n ORDER BY n DESC LIMIT 5"),
    ("Q26 what implies / is equivalent to the Riemann Hypothesis",
     "MATCH (p:Problem)-[r:RELATED_TO]->(h:Problem {id: '01-number-theory/riemann-hypothesis'}) "
     "WHERE r.kind IN ['implies', 'equivalent'] RETURN p.title, r.kind LIMIT 10"),
    ("Q30 most-cited papers",
     "MATCH (:Problem)-[:CITES]->(x:Paper) RETURN x.title, count(*) AS n ORDER BY n DESC LIMIT 5"),
    ("Q35 MSC2020 areas of Number Theory",
     "MATCH (t:Topic {slug: '01-number-theory'})-[:CLASSIFIED_AS]->(m:TaxonomyTerm {scheme: 'msc2020'}) "
     "RETURN m.notation, m.label"),
    ("Q37 Millennium problems and their status",
     "MATCH (p:Problem)-[:PART_OF_LIST]->(:TaxonomyTerm {id: 'list:millennium'}) RETURN p.title, p.status"),
    ("Q43 open, computer-checked, not formalized",
     "MATCH (p:Problem {status: 'open', formalization: 'none-mentioned'})-[:HAS_RESULT]->"
     "(r:Result {result_type: 'computational'}) RETURN p.title, count(r) AS n ORDER BY n DESC LIMIT 5"),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8097")
    client = SamyamaClient.connect(parser.parse_args(argv).url)
    for name, query in QUESTIONS:
        result = client.query_readonly(query)
        print(f"\n## {name}")
        for row in result.records[:10]:
            print("  ", row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
