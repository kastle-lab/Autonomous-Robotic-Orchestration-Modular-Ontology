# Scenario-1

This scenario aims to assess the KG and Orchestrator's abilities.

## Scenario description: KG and Orchestrator Assessment - Low complexity

This experimental setup includes 3 agents, each playing a different role.

Agent 11 is a stationary robotic agent that will be participating in the role of “ worker” (RobS)
Agent 2 is a mobile robotic agent that will be participating in the role of “ worker” (RobM)
Agent 3 is a human agent that will be participating in the role of “Bystander” (H)

The goal of this example scenario is to simulate the Orchestrator appropriately identifying the correct robot for a given job and correct/reassign agents when a deviation occurs.

## Desired Experimental Outcome
User gives AIO instructions to assemble the NIST Task Board #1
AIO uses its available world knowledge and available agents to assign the appropriate agent(s) to complete the tasks. For this scenario, the appropriate selection is RobS.

The assigned agent (RobS) will then work to complete the task based on the orchestrator's decisions and instructions.

During task board assembly, H will move a component out of RobS's reach.

AIO then uses this new world knowledge to assign RobM to navigate to, pick up, and move the task board component back to a reachable position for RobS.

Then, RobS is expected to resume working on the task board until completion.

## Robot and attachements
- `RobS`: NVB6873432	myCobot280PI	Robot Arm with the 4789134Q-14	MyCobotAdaptiveGripper	Gripper attachment.
- `RobM`: JHF-3434-FDAF	myAGV2023PI	Mobile Robot with the NVB68712F3	myCobot280PI	Robot Arm attached to it using the 4901700342	MyCobotFlexibleGripper attachment.
