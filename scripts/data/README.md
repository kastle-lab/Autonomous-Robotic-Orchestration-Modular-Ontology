# Scenario 1 source data

These CSVs support synthetic, symbolic testing of
[example scenario 1](../../example-scenario/example-scenario-1.md). 

## Current materialization and checks

Run from the repository root:

```sh
python3 -m pip install -r scripts/materialization/requirements.txt
python3 scripts/materialization/prepare_data.py
python3 -m morph_kgc scripts/materialization/configuration.ini
```

`prepare_data.py` reads the source CSVs and the maintained
`prepared/agents.csv`, then writes only derived mapping tables under
`prepared/`. It creates deterministic capability-to-specification links from
the source hardware's declared capabilities and matching physical fields. The
itemized YARRRML files in
`scripts/materialization/mappings/` map agents, objects, hardware metadata,
capabilities, component relations, NIST task-board parts, and physical
specifications. The output is `deliverables/materialized/nist-tsk-1.nt` in
N-Triples format; the ontology is loaded separately.

Capability individuals are deterministic per hardware serial and existing
capability class. Agent hardware uses `hasCapability`; attachable objects use
`enablesCapability`. Components use the imported reified `PO-Component-Type`
pattern. Archetypes are not asserted in the materialized graph.

Arm operating range is mapped with the existing `workingRadius` kind; the
existing `millimeter` unit is retained. Mobile robot speed and operating range
are not mapped to capability specifications because the source uses km/h and
km, and the ontology has no suitable existing unit/specification-kind
combination for those values. Attachment extension range is blank in the
current source rows. Electrical current and vision field of view, resolution,
and other descriptive sensor properties are not materialized because the
existing specification-kind and unit vocabularies do not provide direct
representations for them. The numeric depth-camera frame rate is represented
by the existing `frequency` kind and `hertz` unit. No new
controlled-vocabulary individuals are created.
