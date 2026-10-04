# Autonomous-Robotic-Orchestration-Modular-Ontology

The Autonomous Robotic Orchestration Modular Ontology is intended for use with autonomous systems which require robotic orchestration to enable multi-agent systems (MAS) to be governed and commanded by an AI Orchestrator. The ontology empowers the orchestrator to understand its environment, decompose high-level goals into atomic subtasks, and assign agents based on specific capabilities. Ultimately, this framework is engineered for high reusability and generality, providing a mechanism to facilitate the merging of existing ontologies across diverse domains to support increasingly complex autonomous operations.

## Key Resources

- [Ontology](deliverables/ontology/robo-ont.rdf) is the aggregate OWL ontology artifact.
- [Ontology axioms](deliverables/ontology/Autonomous-Robotic-Orchestration-Modular-Ontology_axioms.md) provides the ontology axioms in natural language.
- [Full schema PDF](deliverables/patterns/full-schema.pdf) provides a visual representation of the complete ontology schema.
- [Key notions](deliverables/key-notions.md) documents the central concepts represented in the ontology.
- [Use case](deliverables/use-case.md) describes the motivating use case for the ontology, including the appropriate research and ontology related questions.

## Repository Map

| Directory                                               | Intent                                                                                                     |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [deliverables](deliverables/)                           | Contains the ontology, ontology documentation, schema visualizations, and materialized RDF/TTL artifacts.  |
| [deliverables/materialized](deliverables/materialized/) | Contains the materialized scenario n-triples.                                                              |
| [deliverables/ontology](deliverables/ontology/)         | Contains the aggregate OWL ontology and its axiomatization in natural language.                            |
| [deliverables/patterns](deliverables/patterns/)         | Contains GraphML and PDF visualizations of the complete ontology and its individual patterns.              |
| [deliverables/queries](deliverables/queries/)           | Contains SPARQL competency-question queries for the materialized graph.                                    |
| [example-scenario](example-scenario/)                   | Documents the example scenario represented by the materialized graph.                                      |
| [scripts](scripts/)                                     | Contains scripts, source data, mappings, and utilities used to generate and materialize the ontology data. |
| [scripts/axiomatization](scripts/axiomatization/)       | Contains the scripts used to convert ontology axioms into natural language and apply them to the ontology programatically.                                 |
| [scripts/materialization](scripts/materialization/)     | Contains the scenario data preparation, mapping, and validation tools.                                     |

## Ontology Patterns

The ontology is organized around several core patterns:

| Pattern                                                                                | Description                                                                                                                                                                       |
| -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Archetype](deliverables/patterns/archetype-pattern/archetype-pattern.pdf)             | Representing the thematic capabilities of a robotic agent (E.g., Explorer, Hauler, Designer, Painter, etc.).                                                                      |
| [Capability](deliverables/patterns/capability-pattern/capability-pattern.pdf)          | Represents metadata associated with the modeled resources.                                                                                                                        |
| [Goal-Task](deliverables/patterns/goal-task-pattern/goal-task-pattern.pdf)             | Represents the desired outcome or terminal state toward which one or more tasks are directed; Anchors decomposition hierarchies and provides semantics for task sequencing order. |
| [Role](deliverables/patterns/role-pattern/role-pattern.pdf)                            | Represents the immediate characteristics and participation of a SpatialThing in a specific context (i.e, a Task providing a Role).                                                |
| [Spatial-Thing](deliverables/patterns/spatial-thing/spatial-thing-pattern.pdf)         | Represents a physical thing that exists in time and space.                                                                                                                        |
| [Specification](deliverables/patterns/specification-pattern/specification-pattern.pdf) | Represents a quantified boundary or measurable limit.                                                                                                                             |

## Namespaces

| Prefix | Namespace |
| ------ | --------- |
| `robo-ont` | `https://github.com/kastle-lab/Autonomous-Robotic-Orchestration-Modular-Ontology/lod/ontology#` |
| `robo-r` | `https://github.com/kastle-lab/Autonomous-Robotic-Orchestration-Modular-Ontology/lod/resource#` |
| `po` | `http://daselab.org/ContextualizedWinstonPartWhole#` |

`robo-ont` abbreviates the classes and properties declared in `robo-ont.rdf`.
The ontology document IRI is the same base without the trailing `#`.
`robo-r` identifies scenario resources, while `po` abbreviates the imported
part-whole ontology. See the [query examples](scripts/materialization/README.md#querying-the-graph).

## Tooling

[Morph-KGC](https://github.com/morph-kgc/morph-kgc) materializes an RDF graph in N-Triples from the scenario CSV data and YARRRML mapping.
The [CSV mapping workflow](scripts/materialization/README.md) contains the preparation, configuration, and materialization commands.
The [competency-question queries](deliverables/queries/README.md) can be run against the materialized graph.

## Validation Status

<p>
  <a href="http://oops.linkeddata.es">
    <img src="https://oops.linkeddata.es/images/conformance/oops_important.png"
      alt="free pitfalls were found" height="69.6" width="100" />
  </a>
</p>

The ontology has been checked with OOPS and detected no critical pitfalls. Important pitfalls that do remain are intended to preserve reuse or are rolification properties.

## License

This repository is licensed under the terms in [LICENSE](LICENSE).
