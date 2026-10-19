"""The curated Concept list (docs/ontology.md: Concept) and how it is matched to problems.

Each line is `name | alias; alias`. The names were picked by hand from the phrases that recur in
sections 1-2 of the pinned catalog (2-3 word phrases on 6 or more pages), plus the standard name
of objects the pages write in several ways. A concept is kept only if it matches at least
MIN_PAGES problem pages; everything else is dropped and reported by the build.

Matching: whole words, any case, spaces or hyphens between words, an optional plural "s"/"es".
Problem titles are not concepts (problems link to each other through RELATED_TO).
"""
from __future__ import annotations

import re

MIN_PAGES = 3
MATCH_SECTIONS = (1, 2, 5)   # statement, foundations, obstacles

CONCEPT_TABLE = """
prime number | primes; prime gap; twin primes; prime factorization
riemann zeta function | zeta function; riemann zeta
l-function | l-functions; dirichlet l-function
elliptic curve
modular form | modular forms; cusp form
automorphic form | automorphic representation
galois group | absolute galois group
galois representation
number field | algebraic number field
class group | ideal class group; class number
algebraic number | algebraic integer
diophantine equation
rational point | rational points
arithmetic progression
euler product
functional equation
analytic continuation
sieve method | sieve theory; large sieve; selberg sieve
p-adic number | p-adic; p-adic numbers
finite field
quadratic form
continued fraction
abelian variety
height function | canonical height; néron-tate height
finite simple group | simple group; finite simple groups
finite group
abelian group
lie algebra
lie group
algebraic group | reductive group; connected reductive group
group ring | group algebra
commutative ring | noetherian ring
polynomial ring
irreducible representation | representation theory; group representation
conjugacy class
automorphism group
vector space
maximal ideal
field extension
hopf algebra
coxeter group | weyl group
braid group
free group
hyperbolic group | gromov hyperbolic
cayley graph
amenable group | amenability
residually finite | residual finiteness
derived category | triangulated category
homological algebra | exact sequence
projective variety | smooth projective variety
algebraic variety
moduli space
line bundle | vector bundle
canonical bundle
kodaira dimension
riemannian manifold | riemannian metric
sectional curvature
scalar curvature
ricci curvature
mean curvature
ricci flow
kähler manifold | kähler metric; compact kähler
complex manifold
symplectic manifold | symplectic form; symplectic structure
hodge structure | hodge theory
calabi-yau manifold | calabi-yau
minimal model
birational geometry | birational
convex body
lattice | lattices; lattice packing
geodesic
minimal surface
mirror symmetry
fundamental group
homotopy group | homotopy groups of spheres
homotopy equivalence | homotopy type
homology sphere
knot | knots; knot invariant
jones polynomial
alexander polynomial
floer homology | heegaard floer; instanton floer
khovanov homology
euler characteristic
simplicial complex | cw complex
cobordism
intersection form
dehn surgery
connected sum
mapping class group
k-theory | algebraic k-theory; topological k-theory
spectral sequence
three-manifold | 3-manifold; hyperbolic 3-manifold
four-manifold | 4-manifold; smooth 4-manifold
heegaard splitting
universal cover
characteristic class | chern class; stiefel-whitney class
morse theory | morse function
hilbert space
banach space
fourier transform | fourier analysis; fourier series
lebesgue measure
hausdorff dimension
harmonic analysis
von neumann algebra | operator algebra; c*-algebra
spectral gap
holomorphic function | analytic function; entire function
conformal map | conformal mapping
maximal function | maximal operator
kakeya set | kakeya
singular integral
ergodic theory | ergodic
dynamical system | dynamical systems
julia set | mandelbrot set; complex dynamics
sobolev space | sobolev inequality; sobolev embedding
power series
orthogonal polynomial | orthogonal polynomials
navier-stokes equations | navier-stokes
euler equations
weak solution
global regularity
global existence
well-posedness | local well-posedness; ill-posedness
initial data
boundary condition | boundary conditions
maximum principle
energy estimate | energy inequality; a priori estimate; a priori bound
finite-time singularity | finite-time blow-up; finite time blow-up; blow-up in finite time; singularity formation
schrödinger equation | nonlinear schrödinger
wave equation
heat equation
elliptic equation | elliptic pde; elliptic operator
parabolic equation
conservation law | conservation laws; conserved quantity
dispersive equation | dispersive estimate
convex integration
free boundary
critical exponent | criticality; scaling-critical
strichartz estimate
mean curvature flow
harmonic map
yang-mills | yang-mills theory
chromatic number | graph coloring; colouring
perfect matching
bipartite graph
complete graph
regular graph
ramsey number | ramsey theory
extremal graph theory | turán number; extremal number
generating function
hypergraph
matroid
tournament
planar graph
graph minor | minor-closed
random graph | erdős-rényi
additive combinatorics | sumset; sum-product
polynomial method
latin square
combinatorial design | block design; steiner system
discrepancy
independent set | independence number
clique
hamiltonian cycle | hamiltonian path
spanning tree
regularity lemma | szemerédi regularity lemma
large cardinal | large cardinals
elementary embedding
inner model
set-theoretic forcing | forcing construction; forcing extension; generic extension; cohen forcing; forcing notion; forcing poset
consistency strength
zfc | zermelo-fraenkel
first-order theory | first-order logic
model theory
turing degree | turing degrees
turing machine
decidability | decidable; undecidable
o-minimality | o-minimal
ordinal | ordinals
cardinal arithmetic
descriptive set theory
axiom of choice
determinacy | axiom of determinacy
ultrafilter
random walk | simple random walk
brownian motion
percolation | bond percolation; site percolation; infinite cluster
scaling limit
gaussian free field | gaussian field
schramm-loewner evolution | sle
random matrix | random matrices; random matrix theory
martingale
markov chain
mixing time
phase transition
partition function
ising model
stochastic differential equation | sde
large deviations | large deviation principle
central limit theorem
branching process | branching random walk
self-avoiding walk
first-passage percolation | first passage percolation
kpz | kardar-parisi-zhang
concentration inequality | concentration of measure; concentration inequalities
point process
gibbs measure
free energy
polynomial time | polynomial-time algorithm; polynomial-time
np-complete | np-completeness; np-hard
boolean circuit | circuit complexity; circuit lower bound
communication complexity
proof complexity
pseudorandomness | pseudorandom generator; derandomization
one-way function
quantum algorithm | quantum computer; quantum computation
approximation algorithm | hardness of approximation; approximation ratio
pcp theorem | pcp; probabilistically checkable proof
interactive proof
matrix multiplication
satisfiability | boolean satisfiability; sat solver; 3-sat; k-sat
parameterized complexity | parametrized complexity; fixed-parameter tractable; fpt
fine-grained complexity
query complexity
arithmetic circuit | algebraic complexity
error-correcting code | error correcting code; coding theory
"""


def table() -> list[tuple[str, list[str]]]:
    rows = []
    for line in CONCEPT_TABLE.strip().splitlines():
        name, _, aliases = line.partition("|")
        rows.append((name.strip(), [a.strip() for a in aliases.split(";") if a.strip()]))
    return rows


def concept_id(name: str) -> str:
    return "concept:" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def pattern(name: str, aliases: list[str]) -> re.Pattern:
    alts = []
    for term in sorted({name, *aliases}, key=len, reverse=True):
        words = [re.escape(w) for w in re.split(r"[\s-]+", term.lower())]
        alts.append(r"[\s-]+".join(words) + r"(?:s|es)?")
    return re.compile(r"(?<![\w-])(?:" + "|".join(alts) + r")(?![\w-])", re.IGNORECASE)


def strip_math(text: str) -> str:
    """Drop LaTeX, so `$\\mathbb{Z}/p$` cannot match a word; keep one-letter math (`$p$-adic` -> p-adic)
    and turn en/em dashes into hyphens (Yang–Mills -> Yang-Mills)."""
    text = re.sub(r"\$([A-Za-z])\$", r"\1", text.replace("–", "-").replace("—", "-"))
    return re.sub(r"\$\$.*?\$\$|\$[^$]*\$", " ", text, flags=re.DOTALL)
