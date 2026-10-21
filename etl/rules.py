"""The coded values of docs/taxonomy.md: each rule is a keyword list, first match wins."""
from __future__ import annotations

import re
import unicodedata

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


CASE_LEAD_RE = re.compile(r"^\*\*[^*]{2,160}?\*\*")
CASE_VERB_RE = re.compile(r"\b(proved|proven|showed|shown|established|verified|confirmed|holds|is true|true for)\b",
                          re.IGNORECASE)


def result_type(text: str) -> str:
    return result_type_with_method(text)[0]


def result_type_with_method(text: str) -> tuple[str, str]:
    """Keyword rules first; a section-4 bullet that matches none but opens with a bold case name
    ("**p-solvable groups:** true") or states a proof is a special case, the section's own heading."""
    value = first_match(text, RESULT_RULES, "other")
    if value != "other":
        return value, "bullet-keyword"
    if CASE_LEAD_RE.match(text) or CASE_VERB_RE.search(text):
        return "special_case", "bullet-lead-in"
    return "other", "bullet-keyword"


def problem_kind(title: str) -> str:
    return first_match(title, KIND_RULES, "question")


def relation_kind(sentence: str) -> str:
    return first_match(sentence, RELATION_RULES, "related")


IMPLIES_RE = re.compile(r"\bimpl(y|ies|ied|ying)\b", re.IGNORECASE)
IMPLIED_BY_RE = re.compile(r"implied by|follows from|consequence of|would follow", re.IGNORECASE)
SELF_RE = re.compile(r"\b(it|this|the) (conjecture|hypothesis|problem|statement|question|theorem)\b|^\W*it\b",
                     re.IGNORECASE)
NAME_STOP_RE = re.compile(r"\b(conjecture|hypothesis|problem|program|programme|theorem|lemma|question|the|on|of)\b.*",
                          re.IGNORECASE)


def fold(text: str) -> str:
    """Lower case, no accents, en/em dashes as hyphens: "Lindelöf" == "Lindelof"."""
    text = unicodedata.normalize("NFKD", text.replace("–", "-").replace("—", "-"))
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def names_self(text: str, own_title: str) -> bool:
    """Does `text` name the page itself: its title, its short name ("Vandiver") or "the conjecture"?"""
    short = NAME_STOP_RE.sub("", own_title).strip(" '’s-")
    low = fold(text)
    return (fold(own_title) in low or (len(short) >= 4 and fold(short) in low)
            or bool(SELF_RE.search(text)))


def directed_kind(sentence: str, pos: int, own_title: str) -> str:
    """RELATED_TO.kind with its direction: the edge goes from this page to the problem named at
    `pos`. "This conjecture implies X" -> implies; "X implies this conjecture" -> implied_by.
    When the sentence does not say which side this page is on, the kind is `related`."""
    kind = relation_kind(sentence)
    if kind not in ("implies", "implied_by"):
        return kind
    verb = (IMPLIES_RE if kind == "implies" else IMPLIED_BY_RE).search(sentence)
    other_after = pos >= verb.end()
    self_before, self_after = names_self(sentence[:verb.start()], own_title), names_self(sentence[verb.end():], own_title)
    if other_after and self_before:
        return kind
    if not other_after and self_after:
        return "implied_by" if kind == "implies" else "implies"
    return "related"


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


# The page's own statement names the list entry as its subject: "Hilbert's first problem (1900)
# asked ...", "(Hilbert's 16th problem, first part)". A passing mention ("an instance of
# Hilbert's 12th problem") is not membership.
SUBJECT_RE = r"(?:\s*\(\d{{4}}\))?\s*(?:asked|asks|,\s*(?:first|second) part)"
ERDOS_TITLE_RE = re.compile(r"erd[őo]s", re.IGNORECASE)
ERDOS_NOT_RE = re.compile(r"r[ée]nyi|cardinal|ko.rado", re.IGNORECASE)
ERDOS_POSED_RE = re.compile(r"erd[őo]s[^.]{0,40}\b(asked|conjectured|posed|offered)\b", re.IGNORECASE)


def stated_member(statement: str, who: str, limit: int) -> tuple[int, str] | None:
    """(number, sentence) when section 1 names "<who>'s N-th problem" as the page's subject."""
    for m in re.finditer(NUMBERED_RE.format(who=who), statement, re.IGNORECASE):
        if re.match(SUBJECT_RE.format(), statement[m.end():]):
            n = int(m.group(1)) if m.group(1) else NUMBER_WORDS.get(m.group(2).lower())
            if n and 1 <= n <= limit:
                left = max(statement.rfind(". ", 0, m.start()) + 2, statement.rfind("\n", 0, m.start()) + 1)
                right = statement.find(". ", m.end())
                return n, statement[left:right + 1 if right != -1 else None].strip()
    return None


def list_memberships(page_id: str, title: str, statement: str) -> list[tuple[str, int | None, str]]:
    """(list code, number, evidence) for each famous list this page IS on (not merely mentions)."""
    out = []
    if page_id in MILLENNIUM:
        out.append(("millennium", None, f"catalog page for the Millennium problem {MILLENNIUM[page_id]}"))
    for who, code, limit in (("Hilbert", "hilbert", 23), ("Smale", "smale", 18)):
        n, evidence = numbered_problem(title, who, limit), title
        if not n and (hit := stated_member(statement, who, limit)):
            n, evidence = hit
        if n:
            out.append((code, n, evidence[:200]))
    # Erdős problems: posed by Erdős (named for him as a conjecture or problem, or the statement
    # says he asked it), not objects named after him (Erdős–Rényi graphs, Erdős cardinals).
    if ERDOS_TITLE_RE.search(title) and not ERDOS_NOT_RE.search(title):
        out.append(("erdos", None, title))
    elif (m := ERDOS_POSED_RE.search(statement[:600])):
        out.append(("erdos", None, m.group(0)))
    return out
