# Competency-question queries

Each `.rq` filename uses its query's number in the table below. Some queries
expand on the same question in the
[competency-question list](../use-case.md#competency-questions). Run the files in
Fuseki or another SPARQL 1.1 endpoint after loading the ontology and the
materialized scenario. Each query defines its own prefixes. To use a different
example, edit its `VALUES` clause; CQ 14's threshold is in `HAVING`.

| CQ | Query | Current scenario result |
| --- | --- | --- |
| 1 | [Agents for primary goal](cq-1-agents-for-primary-goal.rq) | RobS and RobM |
| 2 | [Agents matching named Archetypes](cq-2-agents-matching-archetypes.rq) | 13 agent-Archetype pairs |
| 3 | [Candidate agents by task Archetype](cq-3-agents-matching-task-archetypes.rq) | 210 task-agent pairs across 106 mapped tasks |
| 4 | [Agent capabilities and enabling parts](cq-4-agent-capabilities-and-enabling-parts.rq) | 26 agent-capability-part rows |
| 5 | [Agents with Pull](cq-5-agents-with-pull-capability.rq) | RobS via its base arm; RobM via its attached arm |
| 6 | [Agents with Navigate](cq-6-agents-with-navigate-capability.rq) | RobM via its mobile base |
| 7 | [Hardware physical specifications](cq-7-hardware-physical-specifications.rq) | 70 numeric measurements with threshold type and unit |
| 8 | [Agents assigned to task](cq-8-agents-assigned-to-task.rq) | RobS for `task_01_step_1` |
| 9 | [Task sequence for goal](cq-9-task-sequence-for-goal.rq) | 107 ordered tasks |
| 10 | [Prerequisites for task](cq-10-prerequisites-for-task.rq) | 33 predecessors of `task_06_step_2` |
| 11 | [Goals containing task](cq-11-goals-containing-task.rq) | 3 related goals |
| 12 | [Shared dependencies across goals](cq-12-shared-dependencies-across-goals.rq) | No rows in the serial plan |
| 13 | [Decomposable work packages](cq-13-decomposable-work-packages.rq) | 27 Goals |
| 14 | [Work packages with at least five tasks](cq-14-work-packages-with-at-least-five-tasks.rq) | 21 Goals |
| 15 | [Atomic tasks](cq-15-atomic-tasks.rq) | 107 Tasks |
| 16 | [Work packages with multiple agents](cq-16-work-packages-with-multiple-agents.rq) | Recovery work package |
| 17 | [Object classifications](cq-17-object-classifications.rq) | 47 named Objects |
| 18 | [Object and hole geometry specifications](cq-18-object-and-hole-geometry-specifications.rq) | 35 numeric dimensions and nominal fit values |
| 19 | [Objects required for task](cq-19-objects-required-for-task.rq) | One Object for `task_01_step_1` |
| 20 | [Tasks requiring object](cq-20-tasks-requiring-object.rq) | 5 Tasks for `round_peg_4` |
| 21 | [Objects required for goal](cq-21-objects-required-for-goal.rq) | 32 Objects for `goal_assemble` |

These queries answer what the **current graph asserts**. CQs 1 and 8 show
assigned agents. CQ 9 orders the atomic tasks beneath the selected primary
goal using their asserted successor links. CQ 10 lists every prerequisite of
the selected task by following its dependency chain. CQ 11
shows goal membership. CQs 13 and 14 query Goals
because work packages are modeled as Goals with atomic Tasks. CQ 16 identifies
participation by multiple agents. CQ 17
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
queries show each enabling part. The graph has no collision-priority policy,
failed-agent state trace, alternative task route, or numeric task-duration
facts. Empty-result queries for those questions would imply evidence the graph
does not contain.
