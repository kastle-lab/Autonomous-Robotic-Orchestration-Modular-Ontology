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
`prepared/`. The itemized YARRRML files in
`scripts/materialization/mappings/` map agents, objects, hardware metadata,
capabilities, component relations, NIST task-board parts, and physical
specifications. The output is `deliverables/materialized/nist-tsk-1.nt` in
N-Triples format; the ontology is loaded separately.

Capability individuals are deterministic per hardware serial and existing
capability class. Agent hardware uses `hasCapability`; attachable objects use
`enablesCapability`. Components use the imported reified `PO-Component-Type`
pattern. Archetypes are not asserted in the materialized graph.

The current source fields omitted from physical specifications are robot speed
and operating range, attachment extension range, electrical current, and the
vision sensor's field of view, resolution, frame rate, and other descriptive
sensor properties. They remain in their source CSVs and are not converted into
new ontology terms.
