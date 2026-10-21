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


def subtopic_matcher(notation: str, phrase: str) -> re.Pattern:
    """The scope phrase itself or one of its SUBTOPIC_TERMS."""
    from etl.concepts import pattern
    terms = [t.strip() for t in SUBTOPIC_TERMS.get(notation, "").split(";") if t.strip()]
    return re.compile(subtopic_pattern(phrase).pattern + "|" + pattern(phrase, terms).pattern, re.IGNORECASE)


def subtopic_pattern(phrase: str) -> re.Pattern:
    """Match the phrase or its parts joined by "&"/"and", singular or plural, ignoring case."""
    words = re.sub(r"\(.*?\)", "", phrase).replace("&", " ").lower().split()
    words = [w for w in words if w not in {"and", "of", "the"}]
    stems = [re.escape(w[:-1] if w.endswith("s") and len(w) > 4 else w) for w in words]
    return re.compile(r"\b" + r"\w*\W+(?:\w+\W+){0,2}".join(stems) + r"\w*", re.IGNORECASE)


# Words that put a problem under a subtopic (docs/taxonomy.md "the subtopic phrase or a listed
# synonym"), by notation. Matched like concepts: whole words, any case, optional plural.
SUBTOPIC_TERMS = {
    "01.1": "prime; primes; prime gap; twin prime; prime number theorem; riemann zeta function; goldbach",
    "01.2": "diophantine; integer solution; rational solution; diophantine equation; fermat",
    "01.3": "elliptic curve; mordell-weil; birch and swinnerton-dyer; rank of elliptic curve",
    "01.4": "modular form; cusp form; automorphic form; l-function; hecke",
    "01.5": "class field theory; class number; class group; abelian extension; galois representation; iwasawa",
    "01.6": "arithmetic geometry; rational point; abelian variety; height; arithmetic variety",
    "02.1": "representation theory; irreducible representation; character table; block theory; brauer character",
    "02.2": "finite group; finite simple group; classification of finite; group order; sylow; p-group; solvable group; nilpotent group",
    "02.3": "commutative algebra; ring theory; module theory; noetherian ring; artinian; noetherian; commutative ring; polynomial ring",
    "02.4": "homological algebra; derived category; exact sequence; cohomology; ext; tor",
    "02.5": "lie algebra; associative algebra; jordan algebra; hopf algebra; division algebra; quantum group",
    "03.1": "algebraic variety; projective variety; hypersurface; algebraic curve; moduli space; birational",
    "03.2": "manifold; submanifold",
    "03.3": "symplectic; lagrangian; hamiltonian; contact structure",
    "03.4": "riemannian manifold; riemannian metric; geodesic; einstein metric",
    "03.5": "curvature; ricci; scalar curvature; sectional curvature",
    "03.6": "convex body; polytope; packing; tiling; lattice point; discrete geometry; convex geometry; point set",
    "04.1": "three-manifold; 3-manifold; four-manifold; 4-manifold; surface; low-dimensional; mapping class group",
    "04.2": "homotopy group; homotopy; stable homotopy; homotopy type",
    "04.3": "knot; link; knot invariant; jones polynomial; khovanov; alexander polynomial; braid",
    "04.4": "cell complex; cw complex; simplicial complex; triangulation; cobordism; surgery",
    "04.5": "k-theory; algebraic k-theory; topological k-theory; novikov conjecture; baum-connes",
    "05.1": "fourier; harmonic analysis; kakeya; restriction conjecture; maximal function; singular integral",
    "05.2": "operator algebra; von neumann algebra; c*-algebra",
    "05.3": "complex dynamics; julia set; mandelbrot; dynamical system; ergodic",
    "05.4": "banach space; hilbert space; functional analysis; normed space; sobolev",
    "05.5": "measure theory; measure zero; probability measure; invariant measure; lebesgue; hausdorff dimension; measurable",
    "06.1": "existence of solutions; uniqueness of solutions; existence and uniqueness; well-posedness; weak solution; global existence",
    "06.2": "regularity; smoothness; blow-up; singularity; a priori estimate",
    "06.3": "navier-stokes; euler equations; fluid; incompressible",
    "06.4": "dispersive; wave equation; schrödinger equation; nonlinear schrödinger; kdv; soliton",
    "07.1": "ramsey; ramsey number; monochromatic; colouring; coloring",
    "07.2": "turán number; subgraph; graph density; extremal; turán; forbidden subgraph; extremal number",
    "07.3": "enumerative; generating function; permutation; young tableau; symmetric function",
    "07.4": "design; block design; steiner system; latin square; difference set; hadamard",
    "07.5": "matroid",
    "08.1": "model theory; first-order; definable; o-minimal; stable theory",
    "08.2": "computable; computability; decidable; undecidable; turing degree; recursive",
    "08.3": "cardinal; large cardinal; cardinal arithmetic; continuum; aleph",
    "08.4": "descriptive set theory; borel; analytic set; projective set; polish space",
    "08.5": "proof complexity; proof system; frege; propositional proof",
    "08.6": "consistency strength; consistent with zfc; independent of zfc; independence result; forcing; zfc",
    "09.1": "stochastic differential equation; sde; diffusion; brownian motion; stochastic pde; spde",
    "09.2": "random matrix; random matrices",
    "09.3": "percolation; critical probability; infinite cluster",
    "09.4": "schramm-loewner; sle; conformal invariance; scaling limit",
    "10.1": "p vs np; np-complete; np-hard; polynomial time; complexity class",
    "10.2": "arithmetic circuit; algebraic complexity; permanent; determinant; matrix multiplication",
    "10.3": "cryptographic; one-way function; cryptography; hash; pseudorandom; lattice-based",
    "10.4": "quantum; qubit; quantum algorithm; quantum computation; entanglement; information theory",
}
