"""The topic-level mappings of docs/taxonomy.md (MSC2020, arXiv, ACM CCS) and the famous lists."""
from __future__ import annotations

import re
from pathlib import Path

MSC2020 = {
    "03": "Mathematical logic and foundations", "05": "Combinatorics", "11": "Number theory",
    "13": "Commutative algebra", "14": "Algebraic geometry",
    "16": "Associative rings and algebras", "17": "Nonassociative rings and algebras",
    "18": "Category theory; homological algebra", "19": "K-theory", "20": "Group theory and generalizations",
    "26": "Real functions", "30": "Functions of a complex variable",
    "35": "Partial differential equations", "37": "Dynamical systems and ergodic theory",
    "42": "Harmonic analysis on Euclidean spaces", "46": "Functional analysis", "47": "Operator theory",
    "51": "Geometry", "52": "Convex and discrete geometry", "53": "Differential geometry",
    "54": "General topology", "55": "Algebraic topology", "57": "Manifolds and cell complexes",
    "60": "Probability theory and stochastic processes", "68": "Computer science",
    "76": "Fluid mechanics", "81": "Quantum theory", "81P": "Foundations, quantum information and its processing",
    "82": "Statistical mechanics, structure of matter", "94": "Information and communication theory, circuits",
}

TOPIC_MSC = {
    "01-number-theory": ["11"],
    "02-algebra-group-theory": ["20", "16", "17", "18", "13"],
    "03-geometry": ["14", "53", "52", "51"],
    "04-topology": ["57", "55", "54", "19"],
    "05-analysis": ["26", "30", "42", "46", "47", "37"],
    "06-pdes": ["35", "76"],
    "07-combinatorics": ["05"],
    "08-logic-set-theory": ["03"],
    "09-probability": ["60", "82"],
    "10-theoretical-cs": ["68", "94", "81P"],
}

TOPIC_ARXIV = {
    "01-number-theory": ["math.NT"],
    "02-algebra-group-theory": ["math.GR", "math.RA", "math.RT", "math.CT"],
    "03-geometry": ["math.AG", "math.DG", "math.MG", "math.SG"],
    "04-topology": ["math.GT", "math.AT", "math.KT"],
    "05-analysis": ["math.CA", "math.CV", "math.FA", "math.OA", "math.DS"],
    "06-pdes": ["math.AP"],
    "07-combinatorics": ["math.CO"],
    "08-logic-set-theory": ["math.LO"],
    "09-probability": ["math.PR"],
    "10-theoretical-cs": ["cs.CC", "cs.DS", "cs.CR", "quant-ph"],
}

ACM_CCS = {"10-theoretical-cs": ("theory-of-computation", "Theory of computation")}

FAMOUS_LISTS = {
    "millennium": "Millennium Prize Problems (Clay, 2000)",
    "hilbert": "Hilbert's problems (1900)",
    "smale": "Smale's problems (1998)",
    "erdos": "Erdős problems",
}


def read_topics(root: Path) -> list[dict]:
    """The rows of TAXONOMY.md: number, name, slug, scope."""
    rows = []
    for line in (root / "TAXONOMY.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (\d\d) \| ([^|]+) \| \[`([^`]+)`\][^|]*\| ([^|]+) \|", line)
        if m:
            rows.append({"number": m.group(1), "name": m.group(2).strip(),
                         "slug": m.group(3), "scope": m.group(4).strip()})
    return rows


def subtopics(scope: str) -> list[str]:
    """"Fourier analysis, operator algebras & K-theory" -> its phrases, as written."""
    return [p.strip() for p in re.split(r",|;", scope) if p.strip()]


def subtopic_pattern(phrase: str) -> re.Pattern:
    """Match the phrase or its parts joined by "&"/"and", singular or plural, ignoring case."""
    words = re.sub(r"\(.*?\)", "", phrase).replace("&", " ").lower().split()
    words = [w for w in words if w not in {"and", "of", "the"}]
    stems = [re.escape(w[:-1] if w.endswith("s") and len(w) > 4 else w) for w in words]
    return re.compile(r"\b" + r"\w*\W+(?:\w+\W+){0,2}".join(stems) + r"\w*", re.IGNORECASE)
