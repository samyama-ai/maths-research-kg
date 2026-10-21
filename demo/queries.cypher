// The ten queries of the demo, in the order it runs them.
// Written by `python -m demo.demo --write-cypher`. Do not edit: edit STORY in demo/demo.py.

// 1. How open is mathematics?  (rests on: parsed from the page)
// 1,161 problems, one catalog page each. Their status, as the page header states it.
MATCH (p:Problem) RETURN p.status AS status, count(p) AS problems ORDER BY problems DESC;

// 2. Which fields have the most open problems?  (rests on: parsed from the page)
// The 10 topics of TAXONOMY.md; every problem sits in exactly one.
MATCH (p:Problem {status: 'open'})-[:IN_TOPIC]->(t:Topic) RETURN t.name AS field, count(p) AS open_problems ORDER BY open_problems DESC, field LIMIT 5;

// 3. Which concepts sit behind open problems in the most fields?  (rests on: our fixed rule)
// 243 curated concepts matched in each page's statement, foundations and obstacles.
MATCH (p:Problem {status: 'open'})-[:INVOLVES]->(c:Concept), (p)-[:IN_TOPIC]->(t:Topic) RETURN c.name AS concept, count(DISTINCT t) AS fields, count(DISTINCT p) AS open_problems ORDER BY fields DESC, open_problems DESC LIMIT 5;

// 4. What blocks Navier-Stokes regularity?  (rests on: parsed from the page)
// Section 5 of the page, 'Principal Obstacles', one node per bullet.
MATCH (:Problem {id: '06-pdes/navier-stokes-smoothness'})-[:HAS_OBSTACLE]->(o:Obstacle) RETURN o.ordinal AS n, o.text AS obstacle ORDER BY n;

// 5. Which open problems have the most computer checks?  (rests on: our fixed rule)
// Partial results typed by keyword: computational, bound, conditional, special case ...
MATCH (p:Problem {status: 'open'})-[:HAS_RESULT]->(r:Result {result_type: 'computational'}) MATCH (p)-[:IN_TOPIC]->(t:Topic) RETURN p.title AS problem, t.name AS field, count(r) AS checks ORDER BY checks DESC, problem LIMIT 5;

// 6. Which problems are named by the most other problems?  (rests on: title-matched link)
// A page that writes another page's title links to it (longest title wins).
MATCH (p:Problem)-[:RELATED_TO]->(h:Problem) RETURN h.title AS hub, count(DISTINCT p) AS named_by ORDER BY named_by DESC, hub LIMIT 5;

// 7. Which problems would the abc conjecture settle?  (rests on: title-matched link)
// Pages whose own sentence says the abc conjecture implies them.
MATCH (p:Problem)-[r:RELATED_TO]->(:Problem {id: '01-number-theory/abc-conjecture'}) WHERE r.kind = 'implied_by' RETURN DISTINCT p.title AS problem, p.status AS status ORDER BY problem;

// 8. How does a combinatorics problem reach the Riemann hypothesis?  (rests on: title-matched link)
// Two hops of RELATED_TO, across two fields.
MATCH (a:Problem {id: '07-combinatorics/erdos-discrepancy-problem'})-[:RELATED_TO]->(m:Problem)-[:RELATED_TO]->(b:Problem {id: '01-number-theory/riemann-hypothesis'}) RETURN DISTINCT a.title AS start, m.title AS via, b.title AS reaches;

// 9. Which Millennium Prize Problems are in the catalog?  (rests on: our fixed rule)
// Membership, not mention: 9 pages say 'Millennium Prize', 6 are on the list.
MATCH (p:Problem)-[:PART_OF_LIST]->(:TaxonomyTerm {id: 'list:millennium'}) RETURN p.title AS problem, p.status AS status ORDER BY problem;

// 10. Who is the leading expert on the abc conjecture?  (rests on: no such data)
// People are out of scope and every page is synthesized, so the graph says nothing.
MATCH (n:Person)-[:WORKS_ON]->(:Problem {id: '01-number-theory/abc-conjecture'}) RETURN n.name AS expert;
