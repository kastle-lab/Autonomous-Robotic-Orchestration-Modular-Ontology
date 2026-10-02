# Competency-question queries

Each `.rq` filename uses the question's order in the
[competency-question list](../use-case.md#competency-questions). Run the files in
Fuseki or another SPARQL 1.1 endpoint after loading the ontology and the
materialized scenario. Each query defines its own prefixes. To use a different
example, edit its `VALUES` clause; CQ 9's threshold is in `HAVING`.

| CQ | Query | Current scenario result |
| --- | --- | --- |
| 1 | [Agents for primary goal](cq-1-agents-for-primary-goal.rq) | RobS and RobM |
| 2 | [Agents matching named Archetypes](cq-2-agents-matching-archetypes.rq) | 13 agent-Archetype pairs |
| 2 | [Candidate agents by task Archetype](cq-2-agents-matching-task-archetypes.rq) | 210 task-agent pairs across 106 mapped tasks |
| 2 | [Agent capabilities and enabling parts](cq-2-agent-capabilities-and-enabling-parts.rq) | 26 agent-capability-part rows |
| 2 | [Agents with Pull](cq-2-agents-with-pull-capability.rq) | RobS via its base arm; RobM via its attached arm |
| 2 | [Agents with Navigate](cq-2-agents-with-navigate-capability.rq) | RobM via its mobile base |
| 2 | [Hardware physical specifications](cq-2-hardware-physical-specifications.rq) | 70 numeric measurements with threshold type and unit |
| 3 | [Agents assigned to task](cq-3-agents-assigned-to-task.rq) | RobS for `task_01_step_1` |
| 4 | [Task sequence for goal](cq-4-task-sequence-for-goal.rq) | 107 ordered tasks |
| 5 | [Prerequisites for task](cq-5-prerequisites-for-task.rq) | 33 predecessors of `task_06_step_2` |
| 6 | [Goals containing task](cq-6-goals-containing-task.rq) | 3 related goals |
| 7 | [Shared dependencies across goals](cq-7-shared-dependencies-across-goals.rq) | No rows in the serial plan |
| 8 | [Decomposable work packages](cq-8-decomposable-work-packages.rq) | 27 Goals |
| 9 | [Work packages with at least five tasks](cq-9-work-packages-with-at-least-five-tasks.rq) | 21 Goals |
| 10 | [Atomic tasks](cq-10-atomic-tasks.rq) | 107 Tasks |
| 11 | [Work packages with multiple agents](cq-11-work-packages-with-multiple-agents.rq) | Recovery work package |
| 16 | [Object classifications](cq-16-object-classifications.rq) | 47 named Objects |
| 16 | [Object and hole geometry specifications](cq-16-object-and-hole-geometry-specifications.rq) | 35 numeric dimensions and nominal fit values |
| 17 | [Objects required for task](cq-17-objects-required-for-task.rq) | One Object for `task_01_step_1` |
| 18 | [Tasks requiring object](cq-18-tasks-requiring-object.rq) | 5 Tasks for `round_peg_4` |
| 19 | [Objects required for goal](cq-19-objects-required-for-goal.rq) | 32 Objects for `goal_assemble` |

These queries answer what the **current graph asserts**. CQs 1 and 3 show
assigned agents. CQ 6
shows goal membership. CQs 8 and 9 query Goals
because work packages are modeled as Goals with atomic Tasks. CQ 11 identifies
participation by multiple agents. CQ 16
gives the broad `Object` class. The geometry
specification query follows hosted Features to Geometry and uses explicit
Threshold types. Values labeled nominal are
specified dimensions.

The hardware capability dataset links RobS, RobM, and their mounted parts to
shared `requirement*` capability individuals in the ontology. The named-Archetype
queries check whether each agent has every individual required by a named
Archetype; they require the ontology and scenario triples to be queryable
together. The task candidate
query uses explicit Task-to-Archetype links; `pause_assembly` has none and
therefore has no candidate row. The capability inventory, Pull, and Navigate
queries show each enabling part. CQs
12–15 have no query here: the graph has no collision-priority policy,
failed-agent state trace, alternative task route, or numeric task-duration
facts. Empty-result queries for those questions would imply evidence the graph
does not contain.
