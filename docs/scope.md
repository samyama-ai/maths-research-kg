# maths-research-kg — scope

## Core question

**Where are the frontiers of mathematics, what has been proved toward each one, what blocks it,
and how are the problems connected across fields?**

- **Data:** `samyama-ai/maths_research`, commit `6a4b298` (committed 2026-09-25, fetched 2026-10-19), 1,161 problem pages in 10 topics.
- **Status counts:** open 577, partially-solved 333, solved-recently 229, empirically-supported 22.
- **No old graph.** Unlike dbms-research-kg there is no earlier snapshot, so the marks below say
  whether the **catalog** can answer the question, measured on the pages on 2026-10-19.
- Class and relation names are from [`ontology.md`](ontology.md); code values from [`taxonomy.md`](taxonomy.md).

| Mark | Meaning |
|---|---|
| **[yes]** | The data is in a clear field or section; the graph answers it directly. |
| **[partly]** | The data is in prose; the graph answers it through a rule (keyword, title match), so the answer can miss or over-count. The note says how. |
| **[no]** | The catalog does not hold it. Kept as a "refuse" question (group J) or for v2. |

Questions 1–44 are marked; group J (45–48) are questions the graph must refuse.

All 48 are run on the engine by `python -m benchmarks.scope_questions`; the answers, and the check
each one passes, are in [`benchmarks/scope_results.md`](../benchmarks/scope_results.md).

## A. Problems and topics

1. What are the 10 topics, and how many problems does each have? **[yes]** `Topic`, `IN_TOPIC`.
2. How many problems are open, partially-solved, solved-recently or empirically-supported, overall and per topic? **[yes]** `Problem.status`. In PDEs (69 vs 32), probability (54 vs 32) and logic (53 vs 46), partially-solved outnumbers open.
3. Which topic has the most recently solved problems? **[yes]** Topology (38).
4. Which problems are conjectures, hypotheses, named problems, theorems or programmes? **[partly]** `Problem.kind` from the title; 469 titles match no keyword and become `question`.
5. Which subtopics (from TAXONOMY.md scope lines) have the most open problems? **[partly]** Subtopic is keyword-classified.

## B. Understanding one problem

6. What does problem X state, what is its status and kind? **[yes]** Section 1, frontmatter.
7. Which concepts does problem X involve? **[partly]** `INVOLVES` → `Concept`, list-matched in section 2.
8. What is the worked example for problem X? **[yes]** `HAS_EXAMPLE` → `WorkedExample` (all 1,161 pages).
9. What is the gap for problem X? **[yes]** `HAS_GAP` (one per page).
10. Which papers does problem X cite, and in which role? **[yes]** `CITES {role}`; role is on the citation, not the paper (the lesson from DBMS Q9).

## C. What is known

11. What partial results exist for problem X? **[yes]** `HAS_RESULT`; 654 pages have bullets, the other 507 one `summary` Result.
12. Which results are computer checks, and which problems have them? **[partly]** `result_type: computational` (378 bullets by keyword).
13. Which results are conditional (e.g. assuming GRH), and on what? **[partly]** `result_type: conditional` (249); the assumed conjecture is linked only when its title is matched.
14. Which problems were disproved or have a counterexample? **[partly]** `result_type: counterexample` (91 bullets); "disproved" appears on 34 pages.
15. Which problems have best-known bounds, and in which topics? **[partly]** `result_type: bound` (1,460 bullets); the bound value stays as LaTeX text.
16. Which problems mention machine-checked (Lean, Coq, Isabelle) progress? **[yes]** `formalization: mentioned`, 29 pages.

## D. What blocks it

17. What are the principal obstacles for problem X? **[yes]** `HAS_OBSTACLE` (4,684 section-5 bullets).
18. Which topics have the most obstacles per problem? **[yes]** Count of `Obstacle` per `Topic`.
19. Which obstacles mention the same concept across different topics? **[partly]** `Obstacle` text matched to the Concept list.

## E. What would close it

20. What is being worked on for problem X right now (2026)? **[yes]** `HAS_RESEARCH` (5,011 bullets).
21. Which claims are flagged *(frontier — verify)*, and which problems have the most? **[yes]** `confidence: frontier-verify` (2,283 flags; the top page has 6).
22. What future work is proposed for problem X? **[yes]** `HAS_FUTURE` (4,032 bullets).
23. Which research directions recur across many problems (e.g. numerics, computational search, formalization)? **[partly]** By normalised bullet heading; 122 headings recur on ≥ 2 pages.

## F. Connections between problems

24. Which problems mention the Riemann hypothesis? **[partly]** `RELATED_TO`; 48 pages say "Riemann hypothesis", but the title match must not also count "Generalized Riemann Hypothesis".
25. Which problems are named by the most other problems (the hubs)? **[partly]** In-degree of `RELATED_TO`: Riemann Hypothesis ~51, Langlands Program 23, Generalized RH 20, Minimal Model Program 18 (before fixing nested titles).
26. Which problems imply, or are equivalent to, problem X? **[partly]** `RELATED_TO.kind` from the sentence; "implies" is on 572 pages, "equivalent to" on 327, but only same-sentence title matches set the kind.
27. Which links cross topics, and which topic pairs are most connected? **[partly]** 215 of 756 title mentions cross topics.
28. What is the shortest chain of related problems from X to Y? **[partly]** Path query on `RELATED_TO`; as good as the title matches.
29. Which problems share the most concepts with problem X? **[partly]** Shared `INVOLVES` neighbours.

## G. Papers

30. Which papers are cited by the most problems? **[yes]** De-duplicated `Paper`; top: Kanamori, *The Higher Infinite* (26), Guy, *Unsolved Problems in Number Theory* (15).
31. Which papers are cited across the most topics? **[yes]** Max today is 5 topics.
32. Which surveys cover the most problems? **[yes]** `CITES {role: survey}`.
33. How many references have a DOI or arXiv id, per topic? **[yes]** 3,997 DOIs, 285 arXiv ids, 14,550 lines.
34. Which problems cite no foundational work, or no recent work? **[yes]** Absence of a `CITES` role.

## H. Classification and standards

35. Which MSC2020 areas does each topic cover, and which problems fall under MSC 11 (number theory)? **[yes]** Topic-level mapping; per-problem MSC is v2.
36. Which arXiv category would a paper on problem X be posted in? **[yes]** Topic → arXiv mapping (topic level).
37. Which problems are Millennium Prize Problems? **[partly]** `PART_OF_LIST`. The phrase "Millennium Prize Problem" is on 7 pages, but 3 of them (Euler regularity, NP vs BQP, BSD analytic) are related problems, not members. The rule must check membership, not mention.
38. Which of Hilbert's 23 problems are in the catalog, and what is their status? **[partly]** Same rule; "Hilbert" is on 171 pages, most are Hilbert spaces.
39. Which problems are Erdős problems? **[partly]** "Erdős" on 149 pages, many are Erdős–Rényi / Erdős–Ko–Rado names.
40. What is the source page, commit and method for any fact in the graph? **[yes]** PROV-O fields on every node.

## I. Finding research opportunities

41. Which open problems have many partial results but a short gap? **[partly]** Count of `Result` vs. length of `Gap` text; length is a weak signal.
42. Which open problems are connected to a recently solved problem? **[partly]** `RELATED_TO` to a `solved-recently` Problem; the technique might transfer.
43. Which open problems have computer checks but no formalization? **[partly]** Q12 + Q16.
44. Which concepts appear in the most open problems across ≥ 3 topics? **[partly]** `INVOLVES` + `IN_TOPIC`.

## J. Questions the graph should NOT answer

45. Is the Riemann hypothesis true? — The graph records what the catalog says, not mathematical truth.
46. Who is the leading expert on problem X? — People are out of scope in v1, and the pages are synthesized.
47. How many citations does paper P have? — No external records are imported.
48. What happened on problem X after June 2026? — Nothing after the pinned commit.

## Summary

| Mark | Count | Questions |
|---|---:|---|
| [yes] | 22 | 1–3, 6, 8–11, 16–18, 20–22, 30–36, 40 |
| [partly] | 22 | 4, 5, 7, 12–15, 19, 23–29, 37–39, 41–44 |
| [no] | 0 | (the refuse group J holds what the catalog lacks) |
| refuse | 4 | 45–48 |

What the [partly] questions need from the build:

1. **Title matching** that prefers the longest title and needs word boundaries (Q24–28).
2. **List membership**, not mentions (Q37–39).
3. **A second pass on `result_type`**, where 37% of bullets are `other` (Q12–15).
4. **A cleaned concept list** (Q7, Q19, Q29, Q44).
