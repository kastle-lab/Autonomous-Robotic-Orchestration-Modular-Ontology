# CSV to ontology mapping

Run these commands from the repository root with Python 3.10 or newer:

```sh
python3 -m pip install -r scripts/materialization/requirements.txt
python3 scripts/materialization/prepare_data.py
python3 -m morph_kgc scripts/materialization/mappings/configuration.ini
```

## Synthetic vision accessories

The [vision accessory CSV](../data/robot-vision-accessory-specs.csv) adds two
camera fixtures. Their serials and scenario mounts are synthetic; the camera
specifications come from the linked manufacturer pages.

| Accessory | Synthetic serial | Scenario mount | Selected published specifications |
| --- | --- | --- | --- |
| [RealSense D405](https://www.realsenseai.com/products/d405-series/) | `SYN-D405-001` | RobS arm | 7–50 cm ideal depth range; 87° × 58° depth FOV; up to 1280 × 720 depth output; up to 90 fps in supported modes; 1.55 W depth/IR streaming; 42 × 42 × 23 mm; 60 g |
| [Luxonis OAK-D W](https://docs.luxonis.com/hardware/products/OAK-D%20W) | `SYN-OAKDW-001` | RobM mobile base | Approximately 70 cm–12 m ideal depth range; 150° diagonal stereo FOV; IMX378 12 MP RGB with 120° diagonal FOV; 2.5–3 W base plus camera streaming |

The OAK-D W fixture is the standard USB model with IMX378 RGB and no IR
projector. The published D405 maximum resolution and maximum frame rate are
separate mode limits, not a single 1280 × 720 at 90 fps operating mode.
The original scenario document does not specify these cameras, so the mounts
are test assumptions. Their capability assignments are stated separately in
the hardware capability dataset; camera specifications alone do not establish
integration, calibration, or software readiness.

The ontology has no camera-specific numeric properties. The CSV keeps the
specifications in separate columns, while materialization places a readable
summary in each camera's Metadata `hasDescription` value.

## Hardware capability assignments

The [hardware capability CSV](../data/robot-hardware-capabilities.csv) records
the capability types assigned to every listed hardware serial. These are
scenario modeling assertions supplied for this dataset, not performance
certifications inferred from manufacturer specifications.

| Hardware type | Assigned capability classes |
| --- | --- |
| Cobot arm | Push, Pull, Rotate, Reach, Press |
| Vision sensor | Distance, Vision |
| Gripper | Open, Close, Place, Pick |
| Mobile robot | Navigate, Rotate, Push, Press |

Each capability class resolves to its existing `robo-ont:requirement*`
individual. Hardware uses `enablesCapability` to reference that individual,
and the individual uses `enabledBySpatialThing` to identify every enabling
part. Multiple parts can therefore enable the same capability without being
identified as the same part. Hardware typed as an `Agent` also receives
`hasCapability`. RobS and RobM receive one `hasCapability` link per available
shared individual from their assigned parts, including their cameras. Planner
actions use those same capability individuals for `enablesAction`. The ontology
must be loaded alongside `scenario.nt` for the individuals' class assertions
and Archetype requirements to be queryable. When listing the part that enables
an agent's capability, join the part to that agent through its part-whole
membership; the shared capability may also have enablers belonging to other
agents.

## Archetypes and tasks

The [task-Archetype CSV](../data/scenario-1/task_archetypes.csv) links 106 Tasks
to named Archetypes already present in `robo-ont.rdf`: 82 to Assembler, 22 to
Inspector, and two navigation steps to Explorer. `recovery_step_1`
(`pause_assembly`) has no explicit Archetype, as requested. Preparation rejects
an unknown Archetype or one that does not require the step's stated capability.

Morph-KGC emits task and capability links to ontology individuals without
copying the ontology assertions into `scenario.nt`. Load both files to query
the task-Archetype links and shared capability individuals. The task candidate
query matches each Archetype requirement against an agent's available
capabilities; it does not assert `fulfillsArchetype`.

## Querying the graph

Prefixes abbreviate IRIs in SPARQL. To retrieve the two robots and their
names in Fuseki:

```sparql
PREFIX robo-ont: <https://github.com/kastle-lab/Autonomous-Robotic-Orchestration-Modular-Ontology/lod/ontology#>

SELECT ?agent ?name WHERE {
  ?agent a robo-ont:Agent ;
         robo-ont:hasMetadata/robo-ont:hasName ?name .
  FILTER(?name IN ("RobS", "RobM"))
}
```

To retrieve RobS's equipment and serial numbers:

```sparql
PREFIX robo-ont: <https://github.com/kastle-lab/Autonomous-Robotic-Orchestration-Modular-Ontology/lod/ontology#>
PREFIX robo-r: <https://github.com/kastle-lab/Autonomous-Robotic-Orchestration-Modular-Ontology/lod/resource#>
PREFIX po: <http://daselab.org/ContextualizedWinstonPartWhole#>

SELECT ?equipment ?serial WHERE {
  ?equipment po:isPartOf ?membership ;
             robo-ont:hasMetadata/robo-ont:hasSerial ?serial .
  ?membership a po:PO-Member-Type ;
              po:hasWhole robo-r:RobS .
}
```

This returns serials `NVB6873432`, `4789134Q-14`, and `SYN-D405-001`
without inference. A plain `po:po-member` query would require a reasoner to
infer the shortcut property from the relation instance. If the N-Triples are
loaded into a named graph, add `GRAPH <graph-iri> { ... }` around the patterns
or configure a union default graph.
