# Competency-question queries

| Query | Related CQ | Query file | Description |
| --- | --- | --- | --- |
| 1 | CQ-02 | [Agents matching named Archetypes](cq-1-agents-matching-archetypes.rq) | Finds agents matching inferred archetypes. |
| 2 | CQ-02 | [Agent capabilities and their sources](cq-2-agent-capabilities-and-enabling-parts.rq) | Lists direct and attached-part capabilities. |
| 3 | CQ-02 | [Agents that can Pull](cq-3-agents-with-pull-capability.rq) | Finds agents with Pull directly or through attached parts. |
| 4 | CQ-02 | [Agents that can Navigate](cq-4-agents-with-navigate-capability.rq) | Finds agents with Navigate directly or through attached parts. |
| 5 | CQ-02 (supporting) | [Physical specifications for hardware and objects](cq-5-hardware-physical-specifications.rq) | Lists physical specifications and units. |
| 6 | CQ-16 | [Object metadata](cq-6-object-metadata.rq) | Lists descriptive object metadata. |
| 7 | CQ-02 | [Agent capabilities and where they come from](cq-7-agent-effective-capabilities-interim.rq) | Lists capabilities and their source parts. |
| 8 | CQ-02 (supporting) | [Specifications for capabilities](cq-8-capability-specifications.rq) | Lists specifications directly linked to capabilities. |

## Use-case competency questions

The following 19 questions are listed in the same order as the
[use case](../use-case.md#competency-questions). The IDs are assigned here for
reference. The query files support only a subset of these questions. Queries
marked “supporting” provide information for a CQ but do not answer it alone.

| ID | Area | Competency question |
| --- | --- | --- |
| CQ-01 | Robot capability requirements | What set of `agents` are required to complete `primary goal` _y_? |
| CQ-02 | Robot capability requirements | Which `agent` can perform `task` _z_? |
| CQ-03 | Robot capability requirements | What `agents` are required to complete `task` _x_? |
| CQ-04 | Task analysis and decomposition | What is the sequence (`task list`) of `tasks` required to complete `primary goal` _g_? |
| CQ-05 | Task analysis and decomposition | What are the `dependent tasks` for `task` _z_? |
| CQ-06 | Task analysis and decomposition | What `goals` can be achieved from `task` _X_? |
| CQ-07 | Task analysis and decomposition | Which `tasks` share common `dependent tasks` across different `goals`? |
| CQ-08 | Task analysis and decomposition | What `tasks` are decomposable? |
| CQ-09 | Task analysis and decomposition | What `tasks` consist of at least _X_ `tasks`? |
| CQ-10 | Task analysis and decomposition | What `tasks` are the atomic-level `tasks`? |
| CQ-11 | Task analysis and decomposition | Which `task(s)` require collaboration between multiple `agents`? |
| CQ-12 | Environment and execution | Which `agent` has `priority` to do `task` _z_ if `agent` _A_ and `agent` _B_ are in conflict? |
| CQ-13 | Environment and execution | What were the `states` of the `agent` following a failed `task`? |
| CQ-14 | Environment and execution | What is an alternative `path` from `task` _x_ to `task` _y_? |
| CQ-15 | Environment and execution | What should be the estimated `time` to complete `task` _x_ by `agent` _A_? |
| CQ-16 | Object and environment analysis | What are the `classifications` or `categories` of a set of `objects`? |
| CQ-17 | Object and environment analysis | What `objects` are required to complete `task` _x_? |
| CQ-18 | Object and environment analysis | What `task(s)` can be achieved by the presence of `object` _o_? |
| CQ-19 | Object and environment analysis | What `objects` are required for `goal` _g_? |

Notes:

- Queries 3, 4, and 7 follow attached-part links up to two levels deep.
- With reasoning enabled, Query 8 may also show inherited capabilities and
  their specifications.
