"""The coded values of docs/taxonomy.md: each rule is a keyword list, first match wins."""
from __future__ import annotations

import re

STATUS = ("open", "partially-solved", "solved-recently", "empirically-supported")

ROLE_RULES = [
    ("survey", r"survey|review|expository|exposition|lecture|notes"),
    ("book", r"book|monograph|textbook"),
    ("foundational", r"foundational|original|classic|seminal|historical|key|milestone|background"),
    ("sota", r"sota|recent|state|frontier|current|breakthrough|latest"),
    ("partial", r"partial|special case|verified"),
    ("computational", r"computational|computation|numerical|numerics|computer|algorithm|counterexample"),
    ("technique", r"technique|method|structur|barrier|complexity|theory|technical|rigorous|tool"),
    ("related", r"related|connection|context|see also|application"),
]

RESULT_RULES = [
    ("counterexample", r"counterexample|disprov|refut|false in general|fails for"),
    ("conditional", (r"assum|conditional|under (the )?(grh|rh|generali[sz]ed riemann)|if .{0,60} holds|"
                    r"would follow|modulo")),
    ("computational", (r"comput|numeric|verified (up to|for all|for every)|checked|search|"
                      r"brute.?force|exhaustive|sat solver|machine")),
    ("bound", (r"bound|at least|at most|\\le|\\ge|\\leq|\\geq|\\ll|\\gg|o\(|exponent|rate|"
              r"asymptotic|estimate|improv|growth|\\log|density")),
    ("special_case", (r"case|dimension|for (all )?\$?n|class(es)? of|special|restricted|"
                     r"family|families|when |for small|low-degree|holds for|proved for|proven for|"
                     r"true for|known for|settled for|resolved for|establish")),
]

KIND_RULES = [
    ("conjecture", r"conjecture"),
    ("hypothesis", r"hypothes"),
    ("problem", r"problem"),
    ("programme", r"program"),
    ("theorem", r"theorem|lemma"),
]

RELATION_RULES = [
    ("equivalent", r"equivalent|if and only if|\biff\b"),
    ("implied_by", r"implied by|follows from|consequence of|would follow"),
    ("implies", r"\bimpl(y|ies|ied|ying)\b"),
    ("generalizes", r"generali[sz]"),
    ("special_case", r"special case"),
]

FORMAL_RE = re.compile(r"\b(Lean|Coq|Rocq|Isabelle|mathlib|Mathlib)\b")
FRONTIER = "frontier — verify"

NUMBER_WORDS = {w: i + 1 for i, w in enumerate(
    ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth", "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth", "nineteenth", "twentieth", "twenty-first", "twenty-second", "twenty-third"])}
NUMBERED_RE = r"{who}'?s?\s+(\d{{1,2}})(?:st|nd|rd|th)?\s+problem|{who}'?s?\s+([a-z-]+)\s+problem"

MILLENNIUM = {  # catalog id -> list code; the Yang–Mills mass gap has no page in the catalog
    "10-theoretical-cs/p-vs-np": "p-vs-np",
    "01-number-theory/riemann-hypothesis": "riemann-hypothesis",
    "06-pdes/navier-stokes-smoothness": "navier-stokes",
    "03-geometry/hodge-conjecture": "hodge",
    "01-number-theory/birch-and-swinnerton-dyer-conjecture": "birch-swinnerton-dyer",
    "04-topology/poincare-conjecture": "poincare",
}


def first_match(text: str, rules, default: str) -> str:
    low = text.lower()
    for value, pattern in rules:
        if re.search(pattern, low):
            return value
    return default


def role(raw_tag: str | None) -> str:
    return "untagged" if raw_tag is None else first_match(raw_tag, ROLE_RULES, "other")


def result_type(text: str) -> str:
    return first_match(text, RESULT_RULES, "other")


def problem_kind(title: str) -> str:
    return first_match(title, KIND_RULES, "question")


def relation_kind(sentence: str) -> str:
    return first_match(sentence, RELATION_RULES, "related")


def confidence(text: str) -> str:
    return "frontier-verify" if FRONTIER in text else "stated"


def formalization(text: str) -> str:
    return "mentioned" if FORMAL_RE.search(text) else "none-mentioned"


def numbered_problem(text: str, who: str, limit: int) -> int | None:
    """"Hilbert's tenth problem" / "Hilbert's 10th Problem" -> 10, if 1..limit."""
    for m in re.finditer(NUMBERED_RE.format(who=who), text, re.IGNORECASE):
        n = int(m.group(1)) if m.group(1) else NUMBER_WORDS.get(m.group(2).lower())
        if n and 1 <= n <= limit:
            return n
    return None


def list_memberships(page_id: str, title: str, statement: str) -> list[tuple[str, int | None, str]]:
    """(list code, number, evidence) for each famous list this page IS on (not merely mentions)."""
    out = []
    if page_id in MILLENNIUM:
        out.append(("millennium", None, f"catalog page for the Millennium problem {MILLENNIUM[page_id]}"))
    head = title + " " + statement[:300]
    for who, code, limit in (("Hilbert", "hilbert", 23), ("Smale", "smale", 18)):
        n = numbered_problem(title, who, limit) or numbered_problem(statement[:300], who, limit)
        if n:
            out.append((code, n, head[:200]))
    if re.search(r"erd[őo]s", title, re.IGNORECASE):
        out.append(("erdos", None, title))
    return out
