// Maths Research Knowledge Graph — schema (docs/schema.md v0.1)
// Node labels: Topic, Problem, DataSource, Result, Obstacle, Gap, ResearchDirection,
//              FutureDirection, WorkedExample, Paper, TaxonomyTerm, Concept
// Edge types:  IN_TOPIC, HAS_RESULT, HAS_OBSTACLE, HAS_GAP, HAS_RESEARCH, HAS_FUTURE, HAS_EXAMPLE,
//              CITES, INVOLVES, RELATED_TO, CLASSIFIED_AS, PART_OF_LIST, BROADER, FROM_SOURCE
// Syntax checked on Samyama engine 1.11.0.
CREATE INDEX ON :Topic(id);
CREATE INDEX ON :Problem(id);
CREATE INDEX ON :DataSource(id);
CREATE INDEX ON :Result(id);
CREATE INDEX ON :Obstacle(id);
CREATE INDEX ON :Gap(id);
CREATE INDEX ON :ResearchDirection(id);
CREATE INDEX ON :FutureDirection(id);
CREATE INDEX ON :WorkedExample(id);
CREATE INDEX ON :Paper(id);
CREATE INDEX ON :TaxonomyTerm(id);
CREATE INDEX ON :Concept(id);
CREATE INDEX ON :Problem(status);
CREATE INDEX ON :Paper(doi);
