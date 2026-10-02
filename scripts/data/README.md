# Scenario 1 data readiness

The corrected data supports **synthetic, symbolic testing** of
[example scenario 1](../../example-scenario/example-scenario-1.md), including
CSV validation, Morph-KGC materialization, SHACL checks, and expected-answer
SPARQL competency queries. It does **not** establish that the listed robots can
physically assemble every component.

Verified on 2026-10-01 with Morph-KGC 2.10.0, pySHACL 0.31.0, and RDFLib 7.2.1:
source validation passed, 9,946 triples survived the RML round-trip comparison,
SHACL conformed, all 20 CQ checks passed, and all 12 regression tests passed.
Re-run these checks whenever the data, mappings, or ontology changes.

## Run the checks

From the repository root, the source checks need only Python 3.10 or later:

```sh
python3 scripts/validation/validate_sources.py
python3 -m unittest discover -s scripts/validation -p 'test_*.py' -v
```

Install [the pinned dependencies](../validation/requirements.txt) in your Python
environment and run the complete check:

```sh
python3 -m pip install -r scripts/validation/requirements.txt
python3 scripts/validation/run_scenario.py --output /tmp/scenario-1-validation
```

The output directory contains normalized CSVs, an instantiated RML mapping,
`morph.ini`, `scenario.ttl`, a source-checksum manifest, a SHACL report, and
`validation-report.json` with the actual and expected CQ results. The validator
returns a nonzero exit status on failure. Source CSVs are never rewritten by
these commands.

To prepare and materialize separately:

```sh
python3 scripts/materialization/prepare_scenario.py --output /tmp/scenario-1
python3 -m morph_kgc /tmp/scenario-1/morph.ini
```

The Python normalizer contains the ontology-specific translation and expands
JSON arrays into scalar rows; the three RML maps convert those rows to RDF.
This is an explicit staging pipeline, not a claim that the original CSVs can
be materialized correctly without mappings. Morph-KGC's
[official documentation](https://morph-kgc.readthedocs.io/en/stable/documentation/)
describes the INI configuration and `materialize` API used here.

## Audit findings and corrections

The original eight CSVs parsed successfully and had no row-width errors. They
contained 20 assembly work packages, 100 atomic steps, 107 planned actions,
41 BOM components, 41 dimension records, and nine hardware records. Component
joins and score sums were consistent, subject to the issues below.

| Finding before repair | Resolution |
| --- | --- |
| All 107 `predecessor_action_id` values disagreed with the serial plan order; 26 were self-references and three referenced nonexistent actions 108–110. | Replaced with the immediate preceding action, with an empty first predecessor. |
| Seven recovery actions referenced missing task steps and had no parent work-package ID. | Added seven recovery rows to `task_steps.csv`, assigned `task_recovery`, and filled their local step dependencies. |
| `event_H_displacement` was referenced but had no record or effects. | Added an explicitly synthetic event at 167 seconds, between actions 26 and 27, attributed to H. It removes RobS reachability and changes the component from localized to displaced. |
| The returned component never transitioned back to the localized state required for resumption. | Action 33 is now `verify_and_resume_assembly`, requires vision and the returned/paused conditions, and explicitly restores the localized and not-paused facts. Its existing three-second duration is a synthetic estimate. |
| Six before-state labels and two after-state labels were blank. | Filled from existing state IDs/labels; named the displaced state explicitly. |
| Four task part numbers contained `supplier_choice`, while the corresponding BOM part numbers were unknown. | Removed the placeholder from tasks 17–20; these part numbers remain unknown. |
| RobS/RobM identifiers had no CSV join to physical serials, and capability availability was absent. | Added scenario agent configuration from the scenario document and separately labeled assumed capability availability. |
| Initial states, reachability, availability, and assignment conditions had no explicit source. | Added 45 synthetic initial facts, allowing the full trace to be replayed without silently assuming missing preconditions. |

`predecessor_step_id` in `task_steps.csv` expresses a local work-package order.
`predecessor_action_id` expresses the global schedule, including the recovery
interruption. The materialized `dependsOnTask` and `hasNextTask` use that global
schedule, so `task_06_step_2` immediately depends on `recovery_step_7`.

Hardware specification files, BOM values, and supplied dimensions were not
rewritten. The ontology and its import were not changed.

## Synthetic assumptions and provenance

[scenario-1](scenario-1/) contains the added fixtures. `agents.csv` reproduces
the scenario's serial-number assignments and H's Bystander role. All capability
availability, initial planning facts, and event timing/effects are labeled with
a `basis` column. No random generation is used. Generated manifests record the
normalizer version and SHA-256 hashes of the CSVs, ontology, and local import.

Both robots are assumed to have vision, picking, placing, reaching, pressing,
and rotation capabilities. Only RobM is assumed to navigate. These assumptions
make capability queries testable; they are not equipment certifications.
Assembly assignment to RobS comes from the supplied plan and scenario policy.
The capability data alone also admits RobM for manipulation, so it does not
prove a unique or optimal agent selection.

`currentState` describes the **initial snapshot only**, with explicit
`unspecified` placeholders for entities whose initial state is not supplied.
Component histories use `hasState`; action before/after states and 109 replay
snapshots preserve the trace separately. Do not interpret the union of all
historical states as simultaneous `currentState` assertions.

## Ontology and mapping decisions

The declared vocabulary in `robo-ont.rdf` uses:

```text
https://github.com/kastle-lab/Autonomous-Robotic-Orchestration-Modular-Ontology/
```

This differs from both the `lod/ontology#` namespace in the repository README
and the XML default namespace near the RDF file header. The validator checks
mapped classes and properties against the actual RDF declarations.

| Source concept | Mapping and constraint |
| --- | --- |
| Board row such as `task_01` | A compound **Goal** with five atomic **Tasks**, retaining the supplied resource URI. `hasTask` has domain Goal, and there is no task-to-subtask property. Task decomposition CQs must use this Goal hierarchy or require an ontology extension. |
| `goal_assemble`, families, recovery | Goals connected by `hasSubGoal`. The recovery work package contains seven atomic tasks. |
| Task capability requirements | The scenario links capability-bearing Tasks to named ontology Archetypes; `pause_assembly` has no explicit Archetype. Planner action capability arrays, including vision for release/verification, are expanded and linked to the ontology's shared `requirement*` individuals. |
| Agent capability availability | Hardware and agents link to those same `requirement*` individuals. Multiple hardware parts may appear as `enabledBySpatialThing` values because the maximum-one restriction was removed. Eligibility queries match the shared individuals directly. |
| Task execution and participation | Planner actions are Action instances, distinct from Task instances. Tasks provide Worker roles assumed by their agents. H assumes a Bystander role at the first recovery task. |
| Instruction text | `hasInstructionText` is used on Goals; atomic task instructions use `rdfs:label`. Applying that property to Task would infer a disjoint Goal type. |
| Names and serials | Hardware has a Metadata node containing `hasName` and `hasSerial`. Those properties are not applied directly to Agent. |
| Robot measurements | Typed Specification/Threshold/Unit nodes preserve original values and units. Metadata connects to them through application annotation `ex:reportedSpecification`. Direct `SpatialThing hasSpec Specification` would infer Capability, which is disjoint with SpatialThing. Associating these measurements with specific capabilities still requires a verified interpretation. |
| BOM objects and holes | BOM entries become Objects; task-board holes become Features hosted by the board. Recovery zones become Environment instances. Physical targets are not typed as the ontology's Target **role**. |
| Dimensions | Known measurements are attached to Geometry via unit-bearing application annotations. A nut row's repeated bolt length is attached to its related bolt geometry. Unknown dimensions stay absent. |
| Events, action times, state transitions, equipment configuration, scores | Explicit application annotation properties under `https://example.org/nist-atb1/vocab/`. They are not presented as native ontology vocabulary. The current RDF file has no declared Event class or action-to-task/transition properties. |

The graph uses the ontology's native terms wherever their domains and ranges
fit. Application annotations preserve additional scenario information without
silently changing the schema. Consumers requiring exclusively core-ontology
predicates cannot recover all event/execution information from this ontology
alone.

## CQ coverage

The [queries](../validation/cqs/) contain 20 executable checks with committed
expected answers. They cover all 107 tasks in sequence, the recovery boundary,
agent configuration, capability candidates, worker assignments, goal ancestry,
decomposition counts, object requirements, planned retrieval time, displacement,
restored reachability, and all 20 final verified component states.

| CQ family in `deliverables/use-case.md` | Coverage and limit |
| --- | --- |
| Agents needed for a goal/task | Assigned workers are RobS and RobM; no optimization or proof of the minimum necessary team. |
| Which agent can perform a task | Capability-class matching. Navigation returns RobM; picking returns both robots under synthetic assumptions. Physical suitability remains unverified. |
| Task sequence, dependencies, achievable goals | Positive checks over the full trace and its goal hierarchy. |
| Shared dependencies across goals | Expected empty answer for this serial scenario; no positive branching example. |
| Decomposable work, at least X steps, atomic tasks | Goal-to-Task decomposition: twenty groups of five plus one recovery group of seven; 107 atomic Tasks. Native Task-to-Task decomposition is unavailable. |
| Collaboration | The recovery work package involves both robots sequentially. No simultaneous cooperative manipulation case is supplied. |
| Collision priority | Not covered: no collision geometry, priority policy, or collision event. |
| Agent state after a failed task | Not covered: this is an exogenous component displacement, not a failed robot action; agent failure states are absent. |
| Alternative paths | Not covered: only one serial plan, with no alternative-route graph. |
| Estimated task duration by agent | Synthetic scheduled durations are available. RobM's five retrieval actions total 87 seconds; this is not measured performance. |
| Object classification and requirements | Object/Feature classes and task/goal/object joins are checked. Rich object taxonomies are absent. |

## Remaining physical-data gaps

- All 20 tasks have empty target frame, XYZ, force-limit, and torque-limit
  fields. The dimension table alone cannot establish reachability, fit,
  collision freedom, or insertion feasibility.
- Component masses, calibrated poses, grasp geometry, tool mounting,
  friction, sensing calibration, and suitable force/torque control are absent.
  A symbolic `cap_press` or `cap_rotate` assertion cannot replace them.
- RobS's arm camera field is blank, while its gripper says `None`. The assumed
  vision capability needs a confirmed sensing arrangement. RobM's base camera
  does not by itself prove that its arm can localize and grasp a part.
- The stationary gripper lists a 20–45 mm stroke range, while peg transverse
  dimensions are smaller. Confirm the meaning of those fields and the grasp
  arrangement before using them as eligibility constraints.
- Robotiq form-fit/friction payload entries are 5 and 2.5 under headers labeled
  **Grams**, alongside maximum payloads of 5000 and 2500 grams. This may be a
  unit mismatch; values were preserved because the original source has not
  been verified. Do not silently multiply them by 1000.
- Fabrication stock lengths and assembled peg lengths can differ; dimensions
  contain fabrication notes. Several rows say dimensions were not supplied.
  The original attached/source documents are not present here for provenance
  verification, so these values are treated as supplied, not independently
  verified NIST or manufacturer facts.

## What validation proves

The source validator checks identifiers, joins, dimensions/clearance arithmetic,
score sums, action timing, dependencies, required capabilities, event boundaries,
and ground-fact preconditions/effects. Every component has exactly one symbolic
state throughout replay and reaches its final verified state.

The materialization check compares every normalized row with the actual
Morph-KGC output. SHACL checks required scenario fields, role and task links,
state/cardinality constraints, cycles, units/datatypes, and named disjoint types
after RDFS subclass/domain/range inference. The local imported ontology is
loaded alongside the main ontology without a network fetch.

These checks do not constitute complete OWL DL reasoning or a complete SHACL
translation of the ontology. In particular, this fixture does not explicitly
fill every existential restriction: Goal deadlines/success-state nodes and
specifications for every synthetic capability remain absent. OWL's open-world
semantics allow missing explicit fillers; an application needing them must add
source data and corresponding shape requirements. Use a DL reasoner such as
HermiT for a separate full consistency check before treating this as a complete
ontology validation result.
