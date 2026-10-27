# Competency-question queries

The competency questions in [the use case](../use-case.md#competency-questions)
remain unchanged. This directory contains queries supported by the NIST TSK-1
materialization, plus one interim capability-composition query. Queries run in
Fuseki or another SPARQL 1.1 endpoint after loading the ontology and
`deliverables/materialized/nist-tsk-1.nt`.

| Query | Previous entry | Query file | Current graph coverage |
| --- | --- | --- | --- |
| 1 | CQ 2 | [Agents matching named Archetypes](cq-1-agents-matching-archetypes.rq) | Requires ontology reasoning over direct agent capabilities. Archetype links are not asserted in the N-Triples graph. |
| 2 | CQ 4 | [Canonical agent capabilities and enablers](cq-2-agent-capabilities-and-enabling-parts.rq) | Uses `Agent hasCapability Capability`; attached capability closure is not inferred. Enablers may be unbound in this asserted graph. |
| 3 | CQ 5 | [Agents with Pull](cq-3-agents-with-pull-capability.rq) | Includes direct capabilities and capabilities on reified component descendants up to two links deep. |
| 4 | CQ 6 | [Agents with Navigate](cq-4-agents-with-navigate-capability.rq) | Includes direct capabilities and capabilities on reified component descendants up to two links deep. |
| 5 | CQ 7 | [Hardware and object physical specifications](cq-5-hardware-physical-specifications.rq) | Reads generic Threshold values, specification kinds, and optional units; covers serialized hardware and NIST objects. |
| 6 | CQ 17 | [Object metadata](cq-6-object-metadata.rq) | Returns descriptive metadata properties and values, including names, tags, and serials where present. |
| 7 | Interim | [Effective agent capabilities with provenance](cq-7-agent-effective-capabilities-interim.rq) | Manually combines direct agent capabilities and capabilities on components up to two links deep; each row identifies its source. |

Queries 1 and 2 preserve the ontology-level patterns. Query 1 reads inferred
`fulfillsArchetype` links, and Query 2 reads `hasCapability` links. The current
materialized graph contains direct agent capability links but no inferred
archetypes or capabilities copied from components. Query 7 is the temporary
SPARQL traversal for examining the combined capability set before the ontology
supports that closure; it does not add triples to the graph. The missing
capability inheritance is tracked by [issue #15](https://github.com/kastle-lab/Autonomous-Robotic-Orchestration-Modular-Ontology/issues/15).

The interim and capability-specific queries follow the reified component
relations and explicitly require `PO-Component-Type` at each step. They cover
the one- and two-link component assemblies present in NIST TSK-1. Extend their
patterns if deeper component assemblies are added.

The physical-specification query does not filter for lower, nominal, or upper
threshold subclasses because the current mapping types every threshold only as
`Threshold`. The object metadata query returns properties on each object's
`Metadata` resource and omits the structural `rdf:type Metadata` statement.

Queries requiring task, goal, assignment, execution-state, or object-feature
geometry records were removed because those records are absent from the NIST
TSK-1 materialization. The associated competency questions remain in the use
case. Draft issues for the missing data are being prepared for review; no issues
will be posted without approval.
