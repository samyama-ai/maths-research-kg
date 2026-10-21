"""Narrated terminal demo: the Maths Research knowledge graph on Samyama.

    python -m demo.demo                                   # the server on http://127.0.0.1:8097
    python -m demo.demo --url http://127.0.0.1:8098
    python -m demo.demo --no-pause                        # no pacing, for a log or a test
    python -m demo.demo --write-cypher                    # write the ten queries to demo/queries.cypher

Ten questions about the frontiers of mathematics, in one walk: how open the field is, which fields
are most open, the concepts behind open problems across fields, what blocks Navier-Stokes, where the
computer checks are, the hub problems, what the abc conjecture would settle, a chain from
combinatorics to number theory, the Millennium problems, and a question the graph must refuse.

EVERY NUMBER HERE IS READ FROM THE GRAPH AT RUN TIME. Each step is tagged with what its answer rests
on: text parsed from the catalog page, one of our fixed rules (a curated list or keyword rule), a
title-matched link between pages, or nothing (the graph holds no such data).

The demo needs a server that holds the graph:

    docker run -d --name samyama-maths_research -p 127.0.0.1:8097:8080 ghcr.io/samyama-ai/samyama-graph:latest
    python -m etl.snapshot import --url http://127.0.0.1:8097     # or: python -m etl.engine_load --fresh
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

DEFAULT_URL = "http://127.0.0.1:8097"
GRAPH = "default"                       # engine 1.11.0 serves exactly one graph, named "default"
CYPHER_PATH = Path(__file__).resolve().parent / "queries.cypher"
RH = "01-number-theory/riemann-hypothesis"

BASIS = {
    "parsed": ("parsed from the page", "green"),
    "rule": ("our fixed rule", "magenta"),
    "linked": ("title-matched link", "yellow"),
    "none": ("no such data", "red"),
}

# (title, what to say before it, rests on, rows to show, cypher). Edge properties are filtered in
# WHERE, never inline: engine 1.11.0 drops inline edge filters under ORDER BY ... LIMIT.
STORY = [
    ("How open is mathematics?",
     "1,161 problems, one catalog page each. Their status, as the page header states it.", "parsed", 4,
     "MATCH (p:Problem) RETURN p.status AS status, count(p) AS problems ORDER BY problems DESC"),
    ("Which fields have the most open problems?",
     "The 10 topics of TAXONOMY.md; every problem sits in exactly one.", "parsed", 5,
     ("MATCH (p:Problem {status: 'open'})-[:IN_TOPIC]->(t:Topic) "
      "RETURN t.name AS field, count(p) AS open_problems ORDER BY open_problems DESC, field LIMIT 5")),
    ("Which concepts sit behind open problems in the most fields?",
     "243 curated concepts matched in each page's statement, foundations and obstacles.", "rule", 5,
     ("MATCH (p:Problem {status: 'open'})-[:INVOLVES]->(c:Concept), (p)-[:IN_TOPIC]->(t:Topic) "
      "RETURN c.name AS concept, count(DISTINCT t) AS fields, count(DISTINCT p) AS open_problems "
      "ORDER BY fields DESC, open_problems DESC LIMIT 5")),
    ("What blocks Navier-Stokes regularity?",
     "Section 5 of the page, 'Principal Obstacles', one node per bullet.", "parsed", 4,
     ("MATCH (:Problem {id: '06-pdes/navier-stokes-smoothness'})-[:HAS_OBSTACLE]->(o:Obstacle) "
      "RETURN o.ordinal AS n, o.text AS obstacle ORDER BY n")),
    ("Which open problems have the most computer checks?",
     "Partial results typed by keyword: computational, bound, conditional, special case ...", "rule", 5,
     ("MATCH (p:Problem {status: 'open'})-[:HAS_RESULT]->(r:Result {result_type: 'computational'}) "
      "MATCH (p)-[:IN_TOPIC]->(t:Topic) "
      "RETURN p.title AS problem, t.name AS field, count(r) AS checks ORDER BY checks DESC, problem LIMIT 5")),
    ("Which problems are named by the most other problems?",
     "A page that writes another page's title links to it (longest title wins).", "linked", 5,
     ("MATCH (p:Problem)-[:RELATED_TO]->(h:Problem) "
      "RETURN h.title AS hub, count(DISTINCT p) AS named_by ORDER BY named_by DESC, hub LIMIT 5")),
    ("Which problems would the abc conjecture settle?",
     "Pages whose own sentence says the abc conjecture implies them.",
     "linked", 5,
     ("MATCH (p:Problem)-[r:RELATED_TO]->(:Problem {id: '01-number-theory/abc-conjecture'}) "
      "WHERE r.kind = 'implied_by' RETURN DISTINCT p.title AS problem, p.status AS status ORDER BY problem")),
    ("How does a combinatorics problem reach the Riemann hypothesis?",
     "Two hops of RELATED_TO, across two fields.", "linked", 3,
     ("MATCH (a:Problem {id: '07-combinatorics/erdos-discrepancy-problem'})-[:RELATED_TO]->(m:Problem)"
      f"-[:RELATED_TO]->(b:Problem {{id: '{RH}'}}) "
      "RETURN DISTINCT a.title AS start, m.title AS via, b.title AS reaches")),
    ("Which Millennium Prize Problems are in the catalog?",
     "Membership, not mention: 9 pages say 'Millennium Prize', 6 are on the list.", "rule", 7,
     ("MATCH (p:Problem)-[:PART_OF_LIST]->(:TaxonomyTerm {id: 'list:millennium'}) "
      "RETURN p.title AS problem, p.status AS status ORDER BY problem")),
    ("Who is the leading expert on the abc conjecture?",
     "People are out of scope and every page is synthesized, so the graph says nothing.", "none", 3,
     "MATCH (n:Person)-[:WORKS_ON]->(:Problem {id: '01-number-theory/abc-conjecture'}) RETURN n.name AS expert"),
]

TAKEAWAY = ("Status, fields, shared concepts, obstacles, computer checks, hub problems, what\n"
            "implies what, cross-field chains and famous lists, all answered as graph traversals\n"
            "over one pinned catalog commit. Every row leads back to the page it was read from.")


def cell(value, column: str = "") -> str:
    if value is None:
        return "-"
    if isinstance(value, int) and not isinstance(value, bool):
        return f"{value:,}"
    text = " ".join(str(value).replace("**", "").split())
    width = 78 if column == "obstacle" else 44
    return text if len(text) <= width else text[:width - 1] + "…"


def pause(seconds: float, enabled: bool) -> None:
    """DEMO_PACE tunes the recording's cadence without an edit, as in the sibling KGs."""
    if enabled:
        time.sleep(seconds * float(os.environ.get("DEMO_PACE", "1.0")))


def count(client, pattern: str) -> int:
    return client.query(f"MATCH {pattern} RETURN count(*)", GRAPH).records[0][0]


def run(console: Console, client, paced: bool) -> list[str]:
    """One tall report, the layout of samyama-graph/case_studies/_lib/demo_lib.py."""
    nodes, edges = count(client, "(n)"), count(client, "()-[r]->()")
    problems, papers, concepts = count(client, "(n:Problem)"), count(client, "(n:Paper)"), count(client, "(n:Concept)")
    commit = client.query("MATCH (d:DataSource) RETURN d.version", GRAPH).records[0][0]

    console.print(Panel.fit(
        "[bold]Samyama · Maths Research Knowledge Graph[/bold]\n"
        f"{problems:,} open and hard problems · {papers:,} cited papers · {concepts} concepts · 10 fields\n"
        f"[dim]source: github.com/samyama-ai/maths_research at {str(commit)[:8]} · no LLM extraction[/dim]",
        border_style="cyan"))
    pause(1.4, paced)
    console.print()
    console.rule("[bold cyan]1 · Graph loaded into Samyama")
    pause(0.5, paced)
    console.print(f"  [green]loaded[/green] [bold]{nodes:,}[/bold] nodes · [bold]{edges:,}[/bold] edges")
    pause(1.3, paced)

    wrong = []
    for index, (title, lead, basis, rows, statement) in enumerate(STORY, start=1):
        label, colour = BASIS[basis]
        console.print()
        console.rule(f"[bold cyan]{index + 1} · {title}")
        pause(0.5, paced)
        console.print(f"  [dim]Q{index}.[/dim] [bold white]{title}[/bold white]  [dim]·[/dim] [{colour}]{label}[/{colour}]")
        console.print(f"       [italic dim]{lead}[/italic dim]")
        console.print(f"  [dim]cypher>[/dim] [yellow]{escape(' '.join(statement.split()))}[/yellow]")

        began = time.perf_counter()
        result = client.query(statement, GRAPH)
        took = 1000 * (time.perf_counter() - began)
        if result.records:
            table = Table(show_edge=False, pad_edge=False, box=None, header_style="bold magenta")
            for column in result.columns:
                table.add_column(str(column))
            for row in result.records[:rows]:
                table.add_row(*(cell(v, c) for v, c in zip(row, result.columns, strict=False)))
            console.print(table)
        more = len(result.records) - rows
        note = f" (showing {rows})" if more > 0 else ""
        console.print(f"  [green]→[/green] {len(result.records)} row(s){note} in [bold]{took:.1f} ms[/bold]"
                      + ("  [red]as it must: no such data[/red]" if basis == "none" else ""))
        pause(3.2, paced)
        if bool(result.records) == (basis == "none"):
            wrong.append(f"Q{index}")

    console.print()
    console.print(Panel.fit(f"[bold green]{TAKEAWAY}[/bold green]", border_style="green"))
    console.print("  [dim]Concepts, result types, link kinds and list membership are our rules over the\n"
                  "  catalog's words; every page is synthesized, so the graph records what it says.[/dim]")
    pause(1.6, paced)
    return wrong


def write_cypher(path: Path = CYPHER_PATH) -> Path:
    """The ten queries in full, in the order the demo runs them, ready to paste into Insight."""
    lines = ["// The ten queries of the demo, in the order it runs them.",
             "// Written by `python -m demo.demo --write-cypher`. Do not edit: edit STORY in demo/demo.py.", ""]
    for step, (title, lead, basis, _rows, statement) in enumerate(STORY, start=1):
        lines += [f"// {step}. {title}  (rests on: {BASIS[basis][0]})", f"// {lead}", statement + ";", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def connect(url: str):
    from samyama import SamyamaClient
    client = SamyamaClient.connect(url)
    try:
        nodes = count(client, "(n)")
    except Exception as exc:  # any failure here means no usable server
        raise click.ClickException(f"cannot query {url} ({exc}); start a server and load the graph "
                                   "(see the top of demo/demo.py)") from exc
    if not nodes:
        raise click.ClickException(f"{url} holds an empty graph: python -m etl.snapshot import --url {url}")
    return client


@click.command()
@click.option("--url", default=DEFAULT_URL, show_default=True, help="Samyama server holding the graph.")
@click.option("--no-pause", is_flag=True, help="Do not pace the output.")
@click.option("--write-cypher", "only_write", is_flag=True, help="Write the ten queries to demo/queries.cypher and exit.")
def main(url, no_pause, only_write):
    if only_write:
        click.echo(f"wrote {write_cypher()}")
        return
    wrong = run(Console(width=100), connect(url), not no_pause)
    if wrong:
        click.echo(f"these steps did not return what they must: {', '.join(wrong)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
