# Standards

The external standards the Maths Research KG follows, and how each is checked.

The nine vocabulary alignments are in [`ontology.md`](ontology.md#alignment-with-other-vocabularies).
The five taxonomies and ten code lists are in [`taxonomy.md`](taxonomy.md). Every coding system (format, location, counts, checks) is listed in [`coding-systems.md`](coding-systems.md).

Every rule below is a check in `python -m etl.conformance` (`etl/conformance.py`, spec in
[`schema/conformance.json`](../schema/conformance.json)).

## Standards and specification groups (6)

| Group | Conformance rule |
|---|---|
| PROV-O | Every node has `source`, `provenance`, `method`, `retrieved_at`, `source_date`; page-derived nodes have a commit-pinned `source_url`; every node but the DataSource has exactly one `FROM_SOURCE`. A field and edge mapping, not a full PROV-O serialisation. |
| SKOS | Every TaxonomyTerm has `scheme` and `notation`; `BROADER` only inside one scheme; Topic scheme stays flat. |
| RDF/RDFS (declared mappings) | Each vocabulary mapping is declared as a subject–predicate–object triple (`rdfs:subClassOf`, `rdfs:subPropertyOf`, `rdfs:seeAlso`, or `kg:mapsTo`); every mapping names a schema term and a declared vocabulary. No RDF export or OWL reasoning is claimed. |
| Dublin Core / ISO 15836 | `title`, `date`, `subject` correspondences declared and checked. |
| ISO 26324 (DOI) | DOI matches `10.<4–9 digits>/<suffix>`; taken as written in the citation; never invented. 3,997 present. |
| ISO 8601 | `retrieved_at`, `source_date` are `YYYY-MM-DD`; page dates keep the catalog's `YYYY-MM` and validate as year-month. |

## Codes and identifiers

| Code | Standard | On | Rule |
|---|---|---|---|
| DOI | ISO 26324 | `Paper.doi` | as written; 3,997 lines on 519 pages |
| arXiv id | arXiv identifier scheme (`YYMM.NNNNN`, or old `archive/NNNNNNN`) | `Paper.arxiv_id` | as written; 285 new-style + 36 old-style present |
| MSC2020 code | MSC2020 (zbMATH Open / AMS) | `TaxonomyTerm.notation`, scheme `msc2020` | 2-digit, `NNX`, or `NNXNN`; only codes listed in taxonomy.md |
| arXiv category | arXiv category taxonomy | `TaxonomyTerm.notation`, scheme `arxiv` | e.g. `math.NT`, `cs.CC` |
| ACM CCS concept | ACM CCS 2012 | `TaxonomyTerm.notation`, scheme `acm-ccs` | topic 10 only |
| Dates | ISO 8601 | see above | |
| Source version | Git commit SHA-1 | `DataSource.version`, every `source_url` | `6a4b298fc057fe449dee31667c066c269c9209d4` |
| Source location | URL | `source_url` | `https://github.com/samyama-ai/maths_research/blob/<commit>/<file>` |
| Formulas | LaTeX (`$…$`, `$$…$$`) | text properties | kept as written; `\\#` escaping as in the catalog |

## Identifiers

| Node | id pattern | Example |
|---|---|---|
| Topic | `topic:<slug>` | `topic:01-number-theory` |
| Problem | `<topic>/<slug>` (catalog id) | `01-number-theory/abc-conjecture` |
| Result, Obstacle, ResearchDirection, FutureDirection | `<problem id>#s<section>-<n>` | `01-number-theory/riemann-hypothesis#s4-1` |
| Gap, WorkedExample | `<problem id>#s6`, `#s10` | `…/riemann-hypothesis#s6` |
| Paper | `doi:<doi>` if present, else `paper:<hash of normalised title+year>` | `doi:10.1007/…` |
| Concept | `concept:<kebab-name>` | `concept:elliptic-curve` |
| TaxonomyTerm | `<scheme>:<notation>` | `msc2020:11`, `arxiv:math.NT`, `list:millennium` |
| DataSource | `datasource:maths_research` | |

## What is not used (and why)

| Standard | Why not in v1 |
|---|---|
| zbMATH Open document ids, MathSciNet MR numbers | not in the catalog; looking them up would import external records |
| Wikidata QIDs | external records; used only as a reading reference |
| OEIS A-numbers | only 4 pages mention OEIS |
| MathML / OpenMath | formulas stay as LaTeX strings; no conversion |
| ISO 80000-2 (maths symbols) | we do not normalise notation |
| Per-problem MSC2020 codes | the catalog has none; assigning 1,161 codes is v2 work |
| ORCID | people are out of scope in v1 |

## Licences

| Resource | Licence |
|---|---|
| `maths_research` catalog | **no LICENSE file — open question for Naresh** |
| MSC2020 | CC BY-NC-SA (zbMATH Open / AMS); we use code numbers and names as mapping only |
| arXiv category taxonomy, ACM CCS | public classification schemes; codes used for mapping only |
| This repo | Apache-2.0 |

## Provenance and boundary rules

1. Graph data comes only from the pinned `maths_research` catalog.
2. External standards are used to name, validate and map; no external records are imported.
3. Every page is `synthesized`; the graph never upgrades a claim to verified.
4. Every derived value records its rule (`*_method`).
