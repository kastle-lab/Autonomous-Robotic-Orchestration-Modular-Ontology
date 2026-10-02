"""Validate the scenario CSVs and prepare scalar tables for Morph-KGC."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / "scripts" / "data"
DEFAULT_OUTPUT = SOURCE_DIR / "prepared"
SCENARIO_PATH = ROOT / "example-scenario" / "example-scenario-1.md"
ONTOLOGY_PATH = ROOT / "deliverables" / "ontology" / "robo-ont.rdf"
ONTOLOGY_NAMESPACE = "https://github.com/kastle-lab/Autonomous-Robotic-Orchestration-Modular-Ontology/lod/ontology#"
RESOURCE_NAMESPACE = "https://github.com/kastle-lab/Autonomous-Robotic-Orchestration-Modular-Ontology/lod/resource#"
SOURCE_TASK_URI_BASE = "https://example.org/nist-atb1/resource/"
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

CAPABILITY_CLASSES = {
    "cap_vision": "Vision",
    "cap_pick": "Pick",
    "cap_place": "Place",
    "cap_reach": "Reach",
    "cap_press": "Press",
    "cap_rotate": "Rotate",
    "cap_navigate": "Navigate",
}

BOARD_INTEGER_FIELDS = (
    "assembly_inserted_threaded_points",
    "assembly_seated_points",
    "assembly_place_points",
    "assembly_max_points",
    "disassembly_removed_points",
    "disassembly_tray_points",
    "disassembly_max_points",
)

BOARD_FLOAT_FIELDS = (
    "target_x_mm",
    "target_y_mm",
    "target_z_mm",
    "force_limit_n",
    "torque_limit_nm",
)

DIMENSION_FIELDS = (
    "diameter_mm",
    "width_mm",
    "height_mm",
    "length_mm",
    "target_hole_diameter_mm",
    "nominal_diametral_clearance_mm",
    "bolt_length_mm",
)

HARDWARE_MEASUREMENTS = {
    "Repeated Positioning Accuracy (±mm)": ("repeatedPositioningAccuracy", "UpperThreshold", "milimeter"),
    "Min Power Output (Volts)": ("voltage", "LowerThreshold", "volt"),
    "Max Power Output (Volts)": ("voltage", "UpperThreshold", "volt"),
    "Power Output Amps": ("current", "NominalThreshold", "ampere"),
    "Speed (km/h)": ("velocity", "NominalThreshold", "kilometre_per_hour"),
    "Operating Range (mm)": ("rangeOfMotion", "NominalThreshold", "milimeter"),
    "Operating Range (km)": ("rangeOfMotion", "NominalThreshold", "kilometre"),
    "DoF (Degree of Freedom)": ("degreesOfFreedom", "NominalThreshold", "count"),
    "Max Payload (Grams)": ("payload", "UpperThreshold", "gram"),
    "Weight (Grams)": ("weight", "NominalThreshold", "gram"),
    "Min Operating Temperature (Celsius)": ("temperature", "LowerThreshold", "celsius"),
    "Max Operating Temperature (Celsius)": ("temperature", "UpperThreshold", "celsius"),
    "Extension Range (mm)": ("rangeOfMotion", "NominalThreshold", "milimeter"),
    "Min Stroke (mm)": ("stroke", "LowerThreshold", "milimeter"),
    "Max Stroke (mm)": ("stroke", "UpperThreshold", "milimeter"),
    "Min Grip Force (N)": ("gripForce", "LowerThreshold", "newton"),
    "Max Grip Force (N)": ("gripForce", "UpperThreshold", "newton"),
    "Form-fit grip payload (Grams)": ("formFitGrip", "UpperThreshold", "gram"),
    "Friction-grip-payload (Grams)": ("frictionGrip", "UpperThreshold", "gram"),
}

for dimension in ("Length", "Width", "Height", "Depth"):
    for suffix, unit in (("mm", "milimeter"), ("cm", "centimeter"), ("in", "inch"), ("inch", "inch")):
        HARDWARE_MEASUREMENTS[f"{dimension} ({suffix})"] = (
            dimension.lower(), "NominalThreshold", unit
        )

VISION_MEASUREMENTS = {
    "Ideal Depth Min (cm)": ("idealDepthRange", "LowerThreshold", "centimeter"),
    "Ideal Depth Max (cm)": ("idealDepthRange", "UpperThreshold", "centimeter"),
    "Depth FOV H (deg)": ("depthFovHorizontal", "NominalThreshold", "degreeAngle"),
    "Depth FOV V (deg)": ("depthFovVertical", "NominalThreshold", "degreeAngle"),
    "Depth FOV D (deg)": ("depthFovDiagonal", "NominalThreshold", "degreeAngle"),
    "Depth Max Frame Rate (fps)": ("depthFrameRate", "UpperThreshold", "frame_per_second"),
    "RGB FOV H (deg)": ("rgbFovHorizontal", "NominalThreshold", "degreeAngle"),
    "RGB FOV V (deg)": ("rgbFovVertical", "NominalThreshold", "degreeAngle"),
    "RGB FOV D (deg)": ("rgbFovDiagonal", "NominalThreshold", "degreeAngle"),
    "Weight (g)": ("weight", "NominalThreshold", "gram"),
}

VISION_NUMERIC_FIELDS = tuple(VISION_MEASUREMENTS)


def read_csv(name: str, required: set[str]) -> list[dict[str, str]]:
    """Read a source without changing it, rejecting malformed or missing columns."""
    path = SOURCE_DIR / name
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not required <= set(reader.fieldnames):
            raise ValueError(f"{name}: missing columns {sorted(required - set(reader.fieldnames or []))}")
        rows = []
        for line_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"{name}:{line_number}: extra CSV cells")
            if any(value is None for value in row.values()):
                raise ValueError(f"{name}:{line_number}: missing CSV cells")
            rows.append({key: value.strip() for key, value in row.items()})
    return rows


def require_id(value: str, context: str) -> str:
    if not ID_PATTERN.fullmatch(value):
        raise ValueError(f"{context}: invalid or empty identifier {value!r}")
    return value


def require_unique(rows: list[dict[str, str]], key: str, source: str) -> dict[str, dict[str, str]]:
    indexed = {}
    for row in rows:
        identifier = require_id(row[key], source)
        if identifier in indexed:
            raise ValueError(f"{source}: duplicate {key} {identifier}")
        indexed[identifier] = row
    return indexed


def parse_string_list(value: str, context: str) -> list[str]:
    try:
        items = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError(f"{context}: invalid JSON list") from error
    if not isinstance(items, list) or any(not isinstance(item, str) for item in items):
        raise ValueError(f"{context}: expected a list of strings")
    return items


def validate_number(value: str, context: str, *, integer: bool = False) -> None:
    if not value:
        return
    try:
        if integer:
            int(value)
        elif not math.isfinite(float(value)):
            raise ValueError("non-finite numeric value")
    except ValueError as error:
        raise ValueError(f"{context}: invalid numeric value {value!r}") from error


def write_csv(directory: Path, name: str, columns: list[str], rows: list[dict[str, str]]) -> None:
    with (directory / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def make_goals(board: list[dict[str, str]]) -> list[dict[str, str]]:
    goals = [{
        "id": "goal_assemble",
        "parent_id": "",
        "label": "Assemble NIST Task Board 1",
        "instruction": "",
        "success_condition": "",
    }]
    families = sorted({row["goal_id"] for row in board})
    for family in families:
        goals.append({
            "id": family,
            "parent_id": "goal_assemble",
            "label": family.removeprefix("goal_").replace("_", " ").title() + " assembly",
            "instruction": "",
            "success_condition": "",
        })
    goals.append({
        "id": "goal_recovery",
        "parent_id": "goal_assemble",
        "label": "Recover displaced component",
        "instruction": "",
        "success_condition": "",
    })
    for row in board:
        expected_uri = SOURCE_TASK_URI_BASE + row["task_id"]
        if row["task_uri"] != expected_uri:
            raise ValueError(f"{row['task_id']}: task_uri does not match the resource namespace")
        for field in BOARD_INTEGER_FIELDS:
            validate_number(row[field], f"{row['task_id']}.{field}", integer=True)
        for field in BOARD_FLOAT_FIELDS:
            validate_number(row[field], f"{row['task_id']}.{field}")
        goals.append({
            "id": row["task_id"],
            "parent_id": row["goal_id"],
            "label": row["component_name"] + " assembly",
            "instruction": row["instruction"],
            "success_condition": row["success_condition"],
        })
    goals.append({
        "id": "task_recovery",
        "parent_id": "goal_recovery",
        "label": "Recovery work package",
        "instruction": "",
        "success_condition": "",
    })
    return goals


def make_goal_links(goals: list[dict[str, str]]) -> list[dict[str, str]]:
    """Materialize descendants because Morph-KGC does not perform OWL inference."""
    parent_by_id = {goal["id"]: goal["parent_id"] for goal in goals}
    links = []
    for descendant_id, parent_id in parent_by_id.items():
        visited = {descendant_id}
        while parent_id:
            if parent_id not in parent_by_id or parent_id in visited:
                raise ValueError(f"Invalid goal hierarchy at {descendant_id}")
            links.append({"ancestor_id": parent_id, "descendant_id": descendant_id})
            visited.add(parent_id)
            parent_id = parent_by_id[parent_id]
    return links


def make_tasks_and_actions(
    steps: list[dict[str, str]],
    plan: list[dict[str, str]],
    goals: set[str],
    objects: set[str],
    targets: set[str],
    archetypes_by_step: dict[str, str],
    archetype_requirements: dict[str, set[str]],
    capability_individuals: dict[str, str],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    steps_by_id = require_unique(steps, "step_id", "task_steps.csv")
    require_unique(plan, "action_id", "planner_output.csv")
    if len(steps) != len(plan):
        raise ValueError("Every task step must have exactly one planned action")
    ordered = sorted(plan, key=lambda row: int(row["plan_step"]))
    if [int(row["plan_step"]) for row in ordered] != list(range(1, len(plan) + 1)):
        raise ValueError("planner_output.csv: plan_step must be a consecutive sequence")
    if {row["step_id"] for row in plan} != set(steps_by_id):
        raise ValueError("Planner and task-step identifiers do not match")
    for step in steps:
        predecessor_id = step["predecessor_step_id"]
        if predecessor_id and (
            predecessor_id not in steps_by_id
            or steps_by_id[predecessor_id]["parent_task_id"] != step["parent_task_id"]
        ):
            raise ValueError(f"{step['step_id']}: invalid local predecessor")

    tasks = []
    actions = []
    action_capabilities = []
    roles = []
    states_by_id = {}
    for index, action in enumerate(ordered):
        step = steps_by_id[action["step_id"]]
        step_id = step["step_id"]
        require_id(action["agent_id"], f"{step_id}.agent_id")
        for field in ("start_time_s", "duration_s", "end_time_s"):
            validate_number(action[field], f"{step_id}.{field}")
        for field in ("preconditions_json", "add_effects_json", "delete_effects_json"):
            parse_string_list(action[field], f"{step_id}.{field}")
        if action["task_id"] != step["parent_task_id"] or action["task_id"] not in goals:
            raise ValueError(f"{step_id}: unknown or mismatched parent goal")
        if action["component_id"] != step["component_id"] or step["component_id"] not in objects:
            raise ValueError(f"{step_id}: component does not match BOM")
        if action["target_id"] != step["target_id"] or (step["target_id"] and step["target_id"] not in targets):
            raise ValueError(f"{step_id}: target does not match source entities")
        previous_action = ordered[index - 1] if index else None
        expected_predecessor = previous_action["action_id"] if previous_action else ""
        if action["predecessor_action_id"] != expected_predecessor:
            raise ValueError(f"{step_id}: predecessor_action_id is not the immediate preceding action")
        previous_step_id = previous_action["step_id"] if previous_action else ""
        next_step_id = ordered[index + 1]["step_id"] if index + 1 < len(ordered) else ""
        task_capability = step["capability_id"]
        if task_capability and task_capability not in CAPABILITY_CLASSES:
            raise ValueError(f"{step_id}: unknown capability {task_capability}")
        archetype_name = archetypes_by_step.get(step_id)
        if task_capability and not archetype_name:
            raise ValueError(f"{step_id}: a capability-bearing step needs an archetype")
        if task_capability:
            required_individual = capability_individuals[CAPABILITY_CLASSES[task_capability]]
            if required_individual not in archetype_requirements[archetype_name]:
                raise ValueError(
                    f"{step_id}: {archetype_name} does not require {required_individual}"
                )
        tasks.append({
            "id": step_id,
            "goal_id": action["task_id"],
            "component_id": step["component_id"],
            "target_id": step["target_id"],
            "instruction": step["instruction"],
            "predecessor_id": previous_step_id,
            "local_predecessor_id": step["predecessor_step_id"],
            "next_id": next_step_id,
            "capability_id": task_capability,
            "agent_id": action["agent_id"],
        })
        actions.append(action)
        roles.append({"step_id": step_id, "agent_id": action["agent_id"], "role_id": f"worker_{step_id}"})
        capabilities = parse_string_list(action["capability_ids_json"], step_id)
        if task_capability and task_capability not in capabilities:
            raise ValueError(f"{step_id}: task capability is absent from planner action")
        for capability in capabilities:
            if capability not in CAPABILITY_CLASSES:
                raise ValueError(f"{step_id}: unknown planner capability {capability}")
            action_capabilities.append({
                "action_id": action["action_id"],
                "capability_id": capability_individuals[CAPABILITY_CLASSES[capability]],
            })
        for suffix in ("before", "after"):
            state_id = action[f"state_{suffix}_id"]
            label = action[f"state_{suffix}"]
            if state_id:
                existing = states_by_id.setdefault(state_id, {"id": state_id, "component_id": action["component_id"], "label": label})
                if existing["component_id"] != action["component_id"] or existing["label"] != label:
                    raise ValueError(f"{step_id}: conflicting state definition {state_id}")
    return tasks, actions, action_capabilities, roles, list(states_by_id.values())


def make_hardware() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    hardware = []
    measures = []
    for filename, name_column, class_name in (
        ("robot-arm-specs.csv", "Robot", "Agent"),
        ("robot-mobile-specs.csv", "Robot", "Agent"),
        ("robot-attachment-specs.csv", "Attachment", "Object"),
    ):
        rows = read_csv(filename, {"Serial", name_column, "Type"})
        for row in rows:
            serial = row["Serial"]
            hardware_id = "hardware_" + require_id(serial, filename)
            if not serial or not row[name_column]:
                raise ValueError(f"{filename}: hardware serial and name are required")
            hardware.append({"id": hardware_id, "serial": serial, "name": row[name_column], "kind": row["Type"], "class_iri": class_name, "camera": row["Equipped Camera"]})
            for column, (kind, threshold_class, unit) in HARDWARE_MEASUREMENTS.items():
                value = row.get(column, "")
                if value:
                    measures.append(make_measurement(
                        hardware_id, column, value, kind, threshold_class, unit
                    ))
            details = [f"Type: {row['Type']}"]
            if row["Equipped Camera"]:
                details.append(f"Equipped Camera: {row['Equipped Camera']}")
            details.extend(
                f"{column}: {row[column]}"
                for column in HARDWARE_MEASUREMENTS
                if row.get(column)
            )
            hardware[-1]["description"] = "; ".join(details)
    vision_hardware, vision_measures = make_vision_hardware()
    hardware.extend(vision_hardware)
    measures.extend(vision_measures)
    if len({row["serial"] for row in hardware}) != len(hardware):
        raise ValueError("Hardware serial numbers are not unique")
    return hardware, measures


def make_measurement(
    owner_id: str,
    source_field: str,
    value: str,
    kind_id: str,
    threshold_class: str,
    unit_id: str,
) -> dict[str, str]:
    """Keep each source value and its declared unit for specification mapping."""
    validate_number(value, f"{owner_id}.{source_field}")
    field_id = re.sub(r"[^a-z0-9]+", "_", source_field.lower()).strip("_")
    return {
        "id": f"measure_{owner_id}_{field_id}",
        "owner_id": owner_id,
        "kind_id": kind_id,
        "threshold_class": threshold_class,
        "label": source_field,
        "value": value,
        "unit_id": unit_id,
    }


def make_vision_hardware() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Retain sourced camera specifications with synthetic fixture identities."""
    rows = read_csv(
        "robot-vision-accessory-specs.csv",
        {"Serial", "Attachment", "Type", "Specification Source", *VISION_NUMERIC_FIELDS},
    )
    hardware = []
    measures = []
    for row in rows:
        serial = require_id(row["Serial"], "robot-vision-accessory-specs.csv")
        if not serial.startswith("SYN-") or not row["Attachment"]:
            raise ValueError(f"Vision fixture {serial}: synthetic serial and product name are required")
        if row["Type"] != "Vision Sensor":
            raise ValueError(f"Vision fixture {serial}: expected Vision Sensor type")
        if not row["Specification Source"].startswith("https://"):
            raise ValueError(f"Vision fixture {serial}: specification source URL is required")
        for field in VISION_NUMERIC_FIELDS:
            validate_number(row[field], f"vision.{serial}.{field}")
        if not row["Ideal Depth Min (cm)"] or not row["Ideal Depth Max (cm)"]:
            raise ValueError(f"Vision fixture {serial}: ideal depth range is required")
        if float(row["Ideal Depth Min (cm)"]) >= float(row["Ideal Depth Max (cm)"]):
            raise ValueError(f"Vision fixture {serial}: invalid ideal depth range")
        details = [
            f"{field}: {value}"
            for field, value in row.items()
            if value and field not in {"Serial", "Attachment", "Type"}
        ]
        hardware.append({
            "id": f"hardware_{serial}",
            "serial": serial,
            "name": row["Attachment"],
            "kind": row["Type"],
            "class_iri": "Object",
            "camera": "",
            "description": "; ".join(details),
        })
        hardware_id = hardware[-1]["id"]
        for column, (kind, threshold_class, unit) in VISION_MEASUREMENTS.items():
            if row[column]:
                measures.append(make_measurement(
                    hardware_id, column, row[column], kind, threshold_class, unit
                ))
        dimensions = row.get("Dimensions (mm)", "")
        if dimensions:
            match = re.fullmatch(
                r"\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*",
                dimensions,
            )
            if not match:
                raise ValueError(f"Vision fixture {serial}: invalid length x depth x height dimensions")
            for kind, value in zip(("length", "depth", "height"), match.groups()):
                measures.append(make_measurement(
                    hardware_id, f"{kind} (mm)", value, kind, "NominalThreshold", "milimeter"
                ))
    return hardware, measures


def make_equipment_links(
    agents: list[dict[str, str]], hardware: list[dict[str, str]]
) -> list[dict[str, str]]:
    """Validate documented equipment and synthetic vision assignments."""
    assignments = read_csv(
        "scenario-1/equipment_assignments.csv",
        {"agent_id", "serial", "mounted_on_serial"},
    )
    hardware_by_serial = {item["serial"]: item for item in hardware}
    synthetic_vision_serials = {
        item["serial"] for item in hardware if item["kind"] == "Vision Sensor"
    }
    agent_ids = {agent["id"] for agent in agents}
    assigned_by_agent: dict[str, set[str]] = {agent_id: set() for agent_id in agent_ids}
    parents_by_agent: dict[str, dict[str, str]] = {agent_id: {} for agent_id in agent_ids}
    links = []
    for row in assignments:
        agent_id = require_id(row["agent_id"], "equipment assignment")
        serial = row["serial"]
        parent_serial = row["mounted_on_serial"]
        if agent_id not in agent_ids or serial not in hardware_by_serial:
            raise ValueError(f"Unknown agent or hardware serial in equipment assignment: {row}")
        if serial in assigned_by_agent[agent_id]:
            raise ValueError(f"Duplicate equipment assignment: {agent_id} {serial}")
        assigned_by_agent[agent_id].add(serial)
        parents_by_agent[agent_id][serial] = parent_serial
        links.append({
            "agent_id": agent_id,
            "equipment_id": hardware_by_serial[serial]["id"],
            "parent_equipment_id": hardware_by_serial[parent_serial]["id"] if parent_serial in hardware_by_serial else "",
            "membership_relation_id": f"member_{agent_id}_{hardware_by_serial[serial]['id']}",
        })

    assigned_serials = [row["serial"] for row in assignments]
    if len(set(assigned_serials)) != len(assigned_serials):
        raise ValueError("One hardware serial is assigned to multiple agents")
    for agent_id, parents in parents_by_agent.items():
        roots = [serial for serial, parent in parents.items() if not parent]
        if len(roots) != 1:
            raise ValueError(f"{agent_id}: expected exactly one root robot")
        for serial, parent in parents.items():
            if parent and parent not in parents:
                raise ValueError(f"{agent_id}: mounted-on serial {parent} is not assigned to this agent")
            visited = {serial}
            while parent:
                if parent in visited:
                    raise ValueError(f"{agent_id}: equipment mounting cycle at {serial}")
                visited.add(parent)
                parent = parents[parent]

    scenario_lines = {}
    for line in SCENARIO_PATH.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^- `([^`]+)`:\s*(.*)$", line)
        if match and match.group(1) in agent_ids:
            scenario_lines[match.group(1)] = match.group(2)
    if set(scenario_lines) != agent_ids:
        raise ValueError("The scenario document is missing an agent equipment description")
    for agent_id, description in scenario_lines.items():
        documented_serials = {
            serial for serial in hardware_by_serial
            if re.search(rf"(?<![A-Za-z0-9-]){re.escape(serial)}(?![A-Za-z0-9-])", description)
        }
        source_serials = assigned_by_agent[agent_id] - synthetic_vision_serials
        if documented_serials != source_serials:
            raise ValueError(f"{agent_id}: equipment assignments differ from the scenario document")
    return links


def load_capability_classes() -> set[str]:
    """Find named capability subclasses declared in the ontology."""
    owl_class = "{http://www.w3.org/2002/07/owl#}Class"
    subclass = "{http://www.w3.org/2000/01/rdf-schema#}subClassOf"
    resource = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
    about = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
    parents_by_iri = {
        element.get(about): {
            parent.get(resource)
            for parent in element.findall(subclass)
            if parent.get(resource)
        }
        for element in ET.parse(ONTOLOGY_PATH).iter(owl_class)
        if element.get(about)
    }
    capability_iris = {ONTOLOGY_NAMESPACE + "Capability"}
    while True:
        subclasses = {
            iri for iri, parents in parents_by_iri.items()
            if parents & capability_iris
        }
        expanded = capability_iris | subclasses
        if expanded == capability_iris:
            break
        capability_iris = expanded
    return {
        iri.removeprefix(ONTOLOGY_NAMESPACE)
        for iri in capability_iris
        if iri.startswith(ONTOLOGY_NAMESPACE)
    }


def load_capability_individuals() -> dict[str, str]:
    """Map capability classes to their shared requirement individuals."""
    rdf_namespace = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    owl_namespace = "http://www.w3.org/2002/07/owl#"
    root = ET.parse(ONTOLOGY_PATH).getroot()
    capability_classes = load_capability_classes()
    specific_capability_classes = capability_classes - {"Capability"}
    capability_individuals = {}
    for node in root.findall(f"{{{owl_namespace}}}NamedIndividual"):
        iri = node.get(f"{{{rdf_namespace}}}about")
        if not iri or not iri.startswith(ONTOLOGY_NAMESPACE + "requirement"):
            continue
        requirement_types = set()
        for item in node.findall(f"{{{rdf_namespace}}}type"):
            class_iri = item.get(f"{{{rdf_namespace}}}resource")
            if class_iri and class_iri.startswith(ONTOLOGY_NAMESPACE):
                class_name = class_iri.removeprefix(ONTOLOGY_NAMESPACE)
                if class_name in specific_capability_classes:
                    requirement_types.add(class_name)
        if len(requirement_types) != 1:
            raise ValueError(f"{iri}: expected one capability subclass type")
        class_name = next(iter(requirement_types))
        individual_name = require_id(
            iri.removeprefix(ONTOLOGY_NAMESPACE), "capability requirement"
        )
        existing = capability_individuals.setdefault(class_name, individual_name)
        if existing != individual_name:
            raise ValueError(f"{class_name}: multiple requirement individuals")
    return capability_individuals


def load_archetype_requirements(capability_individuals: dict[str, str]) -> dict[str, set[str]]:
    """Read named Archetypes and their shared requirement individuals."""
    rdf_namespace = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    owl_namespace = "http://www.w3.org/2002/07/owl#"
    root = ET.parse(ONTOLOGY_PATH).getroot()
    known_requirements = set(capability_individuals.values())
    requirements_by_archetype = {}
    for node in root.findall(f"{{{owl_namespace}}}NamedIndividual"):
        types = {
            item.get(f"{{{rdf_namespace}}}resource")
            for item in node.findall(f"{{{rdf_namespace}}}type")
        }
        if ONTOLOGY_NAMESPACE + "Archetype" not in types:
            continue
        iri = node.get(f"{{{rdf_namespace}}}about")
        if not iri or not iri.startswith(ONTOLOGY_NAMESPACE):
            raise ValueError(f"Archetype must use the ontology namespace: {iri}")
        archetype_name = require_id(iri.removeprefix(ONTOLOGY_NAMESPACE), "Archetype")
        required_individuals = set()
        for relation in node.findall(f"{{{ONTOLOGY_NAMESPACE}}}requiresCapability"):
            required_iri = relation.get(f"{{{rdf_namespace}}}resource")
            if not required_iri or not required_iri.startswith(ONTOLOGY_NAMESPACE):
                raise ValueError(f"{archetype_name}: invalid capability requirement {required_iri}")
            required_name = required_iri.removeprefix(ONTOLOGY_NAMESPACE)
            if required_name not in known_requirements:
                raise ValueError(f"{archetype_name}: unknown capability requirement {required_name}")
            required_individuals.add(required_name)
        if not required_individuals:
            raise ValueError(f"{archetype_name}: no explicit capability requirements")
        requirements_by_archetype[archetype_name] = required_individuals
    return requirements_by_archetype


def make_hardware_capabilities(
    hardware: list[dict[str, str]],
    equipment_links: list[dict[str, str]],
    capability_individuals: dict[str, str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Link each enabler and assembled agent to shared ontology capabilities."""
    source_name = "robot-hardware-capabilities.csv"
    rows = read_csv(source_name, {"Serial", "Capability Class"})
    hardware_by_serial = {item["serial"]: item for item in hardware}
    allowed_classes = load_capability_classes()
    capabilities = []
    capabilities_by_hardware: dict[str, list[str]] = {
        item["id"]: [] for item in hardware
    }
    seen_pairs = set()
    for row in rows:
        serial = row["Serial"]
        class_name = row["Capability Class"]
        if serial not in hardware_by_serial:
            raise ValueError(f"{source_name}: unknown hardware serial {serial}")
        if class_name not in allowed_classes or class_name == "Capability":
            raise ValueError(f"{source_name}: undeclared capability subclass {class_name}")
        if (serial, class_name) in seen_pairs:
            raise ValueError(f"{source_name}: duplicate capability {serial} {class_name}")
        seen_pairs.add((serial, class_name))
        hardware_id = hardware_by_serial[serial]["id"]
        if class_name not in capability_individuals:
            raise ValueError(f"{source_name}: no ontology requirement for {class_name}")
        capability_id = capability_individuals[class_name]
        capabilities.append({
            "id": capability_id,
            "hardware_id": hardware_id,
            "class_iri": class_name,
            "label": class_name,
        })
        capabilities_by_hardware[hardware_id].append(capability_id)
    missing = [item["serial"] for item in hardware if not capabilities_by_hardware[item["id"]]]
    if missing:
        raise ValueError(f"{source_name}: missing hardware capability rows for {missing}")

    holder_pairs = {
        (item["id"], capability_id)
        for item in hardware if item["class_iri"] == "Agent"
        for capability_id in capabilities_by_hardware[item["id"]]
    }
    holder_pairs.update(
        (link["agent_id"], capability_id)
        for link in equipment_links
        for capability_id in capabilities_by_hardware[link["equipment_id"]]
    )
    holders = [
        {"holder_id": holder_id, "capability_id": capability_id}
        for holder_id, capability_id in sorted(holder_pairs)
    ]
    return capabilities, holders


def make_dimensions(
    rows: list[dict[str, str]],
    objects: set[str],
    targets_by_component: dict[str, str],
    hole_ids: set[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    """Attach part dimensions to hosted features and nominal hole sizes to holes."""
    features = []
    geometries = []
    dimension_notes = []
    measures = []
    part_fields = ("diameter_mm", "width_mm", "height_mm", "length_mm", "bolt_length_mm")
    dimensions_by_component = {row["component_id"]: row for row in rows}
    for row in rows:
        component = row["component_id"]
        related = row["related_component_id"]
        if component not in objects or (related and related not in objects):
            raise ValueError(f"dimensions.csv: unknown component for {component}")
        for field in DIMENSION_FIELDS:
            validate_number(row[field], f"dimensions.csv.{component}.{field}")
        if related and row["bolt_length_mm"]:
            related_length = dimensions_by_component[related]["bolt_length_mm"]
            if not related_length or float(row["bolt_length_mm"]) != float(related_length):
                raise ValueError(f"{component}: related bolt length differs from {related}")

        own_values = {
            field: row[field]
            for field in part_fields
            if row[field] and not (field == "bolt_length_mm" and related)
        }
        if own_values:
            feature_id = f"shape_{component}"
            geometry_id = f"geometry_{component}"
            features.append({"id": feature_id, "host_id": component, "label": f"Shape of {component}"})
            details = [f"{field}: {value} millimetre" for field, value in own_values.items()]
            if row["thread_designation"]:
                details.append(f"Thread designation: {row['thread_designation']}")
            if row["notes"] and not row["target_hole_diameter_mm"]:
                details.append(row["notes"])
            geometries.append({
                "id": geometry_id,
                "feature_id": feature_id,
                "description": "; ".join(details),
            })
            for field, value in own_values.items():
                kind = "length" if field == "bolt_length_mm" else field.removesuffix("_mm")
                measures.append(make_measurement(
                    geometry_id, field, value, kind, "NominalThreshold", "milimeter"
                ))
        else:
            details = []
            if row["thread_designation"]:
                details.append(f"Thread designation: {row['thread_designation']}")
            if related:
                details.append(f"Related bolt: {related}")
            if row["notes"]:
                details.append(row["notes"])
            if details:
                dimension_notes.append({"component_id": component, "description": "; ".join(details)})

        hole_diameter = row["target_hole_diameter_mm"]
        clearance = row["nominal_diametral_clearance_mm"]
        if hole_diameter or clearance:
            hole_id = targets_by_component.get(component, "")
            if hole_id not in hole_ids:
                raise ValueError(f"{component}: nominal hole dimensions lack a board Feature")
            geometry_id = f"geometry_{hole_id}"
            details = [f"Nominal fit with {component}; actual clearance requires measurement"]
            if hole_diameter:
                details.append(f"Specified drill-bit diameter: {hole_diameter} millimetre")
                measures.append(make_measurement(
                    geometry_id, "target_hole_diameter_mm", hole_diameter,
                    "diameter", "NominalThreshold", "milimeter"
                ))
            if clearance:
                details.append(f"Nominal diametral clearance: {clearance} millimetre")
                measures.append(make_measurement(
                    geometry_id, "nominal_diametral_clearance_mm", clearance,
                    "nominalDiametralClearance", "NominalThreshold", "milimeter"
                ))
            if row["notes"]:
                details.append(row["notes"])
            geometries.append({
                "id": geometry_id,
                "feature_id": hole_id,
                "description": "; ".join(details),
            })
    if len({row["id"] for row in geometries}) != len(geometries):
        raise ValueError("dimensions.csv: multiple dimension rows describe the same geometry")
    return features, geometries, dimension_notes, measures


def load_named_individuals(class_name: str) -> set[str]:
    """Read the controlled SpecificationKind and Unit individuals from robo-ont."""
    rdf_namespace = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    owl_namespace = "http://www.w3.org/2002/07/owl#"
    names = set()
    for node in ET.parse(ONTOLOGY_PATH).iter(f"{{{owl_namespace}}}NamedIndividual"):
        iri = node.get(f"{{{rdf_namespace}}}about", "")
        if not iri.startswith(ONTOLOGY_NAMESPACE):
            continue
        if any(
            item.get(f"{{{rdf_namespace}}}resource") == ONTOLOGY_NAMESPACE + class_name
            for item in node.findall(f"{{{rdf_namespace}}}type")
        ):
            names.add(iri.removeprefix(ONTOLOGY_NAMESPACE))
    return names


def make_specifications(
    measurements: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    """Group measurements into Specification, Threshold, kind, and unit nodes."""
    ontology_kinds = load_named_individuals("SpecificationKind")
    ontology_units = load_named_individuals("Unit")
    specifications: dict[str, dict[str, str]] = {}
    thresholds = []
    new_kinds: dict[str, dict[str, str]] = {}
    new_units: dict[str, dict[str, str]] = {}
    seen_measurements = set()
    for measurement in measurements:
        owner = require_id(measurement["owner_id"], "specification owner")
        kind = require_id(measurement["kind_id"], "specification kind")
        unit = require_id(measurement["unit_id"], "specification unit")
        threshold_class = measurement["threshold_class"]
        if threshold_class not in {"LowerThreshold", "NominalThreshold", "UpperThreshold"}:
            raise ValueError(f"{measurement['id']}: unsupported threshold class {threshold_class}")
        measurement_key = (owner, kind, unit, threshold_class)
        if measurement_key in seen_measurements:
            raise ValueError(f"Duplicate measurement for {measurement_key}")
        seen_measurements.add(measurement_key)

        specification_id = f"spec_{owner}_{kind}_{unit}"
        kind_iri = (
            ONTOLOGY_NAMESPACE + kind
            if kind in ontology_kinds else RESOURCE_NAMESPACE + "spec_kind_" + kind
        )
        unit_iri = (
            ONTOLOGY_NAMESPACE + unit
            if unit in ontology_units else RESOURCE_NAMESPACE + "unit_" + unit
        )
        specifications.setdefault(specification_id, {
            "id": specification_id,
            "owner_id": owner,
            "kind_iri": kind_iri,
            "label": f"{kind} specification for {owner}",
        })
        thresholds.append({
            "id": f"threshold_{measurement['id']}",
            "specification_id": specification_id,
            "class_iri": threshold_class,
            "label": measurement["label"],
            "value": measurement["value"],
            "unit_iri": unit_iri,
        })
        if kind not in ontology_kinds:
            new_kinds[kind] = {"id": "spec_kind_" + kind, "label": kind}
        if unit not in ontology_units:
            new_units[unit] = {"id": "unit_" + unit, "label": unit.replace("_", " ")}
    return (
        list(specifications.values()),
        thresholds,
        list(new_kinds.values()),
        list(new_units.values()),
    )


def prepare(output: Path) -> None:
    board = read_csv("nist_task_board_1.csv", {"task_id", "task_uri", "goal_id", "component_id", "target_id", "instruction"})
    steps = read_csv("task_steps.csv", {"step_id", "parent_task_id", "component_id", "target_id", "capability_id"})
    task_archetypes = read_csv("scenario-1/task_archetypes.csv", {"step_id", "archetype_name"})
    plan = read_csv("planner_output.csv", {"plan_step", "action_id", "step_id", "task_id", "component_id", "target_id", "capability_ids_json"})
    bom = read_csv("fabrication_bom.csv", {"component_id", "item_name", "part_number", "notes"})
    dimensions = read_csv("dimensions.csv", {"component_id", "related_component_id", *DIMENSION_FIELDS})
    require_unique(board, "task_id", "nist_task_board_1.csv")
    archetypes_by_step = {
        step_id: row["archetype_name"]
        for step_id, row in require_unique(task_archetypes, "step_id", "task_archetypes.csv").items()
    }
    step_ids = {step["step_id"] for step in steps}
    if step_ids - set(archetypes_by_step) != {"recovery_step_1"} or set(archetypes_by_step) - step_ids:
        raise ValueError("task_archetypes.csv: only recovery_step_1 may lack an archetype")
    capability_individuals = load_capability_individuals()
    missing_capabilities = set(CAPABILITY_CLASSES.values()) - set(capability_individuals)
    if missing_capabilities:
        raise ValueError(
            f"robo-ont.rdf: missing shared capability individuals for {sorted(missing_capabilities)}"
        )
    archetype_requirements = load_archetype_requirements(capability_individuals)
    for step_id, archetype_name in archetypes_by_step.items():
        if archetype_name not in archetype_requirements:
            raise ValueError(f"{step_id}: unknown ontology Archetype {archetype_name}")
    objects_by_id = require_unique(bom, "component_id", "fabrication_bom.csv")
    require_unique(dimensions, "component_id", "dimensions.csv")
    if set(objects_by_id) != {row["component_id"] for row in dimensions}:
        raise ValueError("BOM and dimensions must cover the same components")
    for row in board:
        if row["component_id"] not in objects_by_id:
            raise ValueError(f"{row['task_id']}: component missing from BOM")

    goals = make_goals(board)
    goal_links = make_goal_links(goals)
    goal_ids = {row["id"] for row in goals}
    board_targets = {row["target_id"] for row in board if row["target_id"]}
    step_targets = {row["target_id"] for row in steps if row["target_id"]}
    targets = board_targets | step_targets
    tasks, actions, action_caps, roles, states = make_tasks_and_actions(
        steps,
        plan,
        goal_ids,
        set(objects_by_id),
        targets,
        archetypes_by_step,
        archetype_requirements,
        capability_individuals,
    )
    hardware, hardware_measures = make_hardware()
    features = [
        {
            "id": target,
            "host_id": "board",
            "label": next(row["target_name"] for row in board if row["target_id"] == target),
        }
        for target in sorted(board_targets - set(objects_by_id))
    ]
    targets_by_component = {}
    for row in board:
        component = row["component_id"]
        target = row["target_id"]
        if component in targets_by_component and targets_by_component[component] != target:
            raise ValueError(f"{component}: conflicting targets in nist_task_board_1.csv")
        targets_by_component[component] = target
    part_features, geometries, dimension_notes, dimension_measures = make_dimensions(
        dimensions, set(objects_by_id), targets_by_component,
        {feature["id"] for feature in features},
    )
    features.extend(part_features)
    specifications, thresholds, specification_kinds, units = make_specifications(
        dimension_measures + hardware_measures
    )
    zones = [
        {"id": target, "label": target.replace("_", " ")}
        for target in sorted(step_targets - board_targets - set(objects_by_id))
    ]
    agents = [{"id": agent_id, "label": agent_id} for agent_id in sorted({row["agent_id"] for row in actions})]
    equipment_links = make_equipment_links(agents, hardware)
    hardware_capabilities, capability_holders = make_hardware_capabilities(
        hardware, equipment_links, capability_individuals
    )
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output, "board.csv", list(board[0]), board)
    write_csv(output, "goals.csv", ["id", "parent_id", "label", "instruction", "success_condition"], goals)
    write_csv(
        output,
        "success_states.csv",
        ["goal_id", "condition"],
        [
            {"goal_id": goal["id"], "condition": goal["success_condition"]}
            for goal in goals if goal["success_condition"]
        ],
    )
    write_csv(output, "goal_links.csv", ["ancestor_id", "descendant_id"], goal_links)
    write_csv(output, "tasks.csv", ["id", "goal_id", "component_id", "target_id", "instruction", "predecessor_id", "local_predecessor_id", "next_id", "capability_id", "agent_id"], tasks)
    write_csv(output, "task_archetypes.csv", ["step_id", "archetype_name"], task_archetypes)
    write_csv(output, "actions.csv", list(actions[0]), actions)
    write_csv(output, "action_capabilities.csv", ["action_id", "capability_id"], action_caps)
    write_csv(output, "roles.csv", ["step_id", "agent_id", "role_id"], roles)
    write_csv(output, "states.csv", ["id", "component_id", "label"], states)
    write_csv(output, "objects.csv", ["component_id", "item_name", "part_number", "notes", "nist_item_id"], bom)
    write_csv(output, "features.csv", ["id", "host_id", "label"], features)
    write_csv(output, "zones.csv", ["id", "label"], zones)
    write_csv(output, "agents.csv", ["id", "label"], agents)
    write_csv(output, "equipment_links.csv", ["agent_id", "equipment_id", "parent_equipment_id", "membership_relation_id"], equipment_links)
    write_csv(output, "hardware_capabilities.csv", ["id", "hardware_id", "class_iri", "label"], hardware_capabilities)
    write_csv(output, "capability_holders.csv", ["holder_id", "capability_id"], capability_holders)
    write_csv(output, "hardware.csv", ["id", "serial", "name", "kind", "class_iri", "camera", "description"], hardware)
    measurement_columns = ["id", "owner_id", "kind_id", "threshold_class", "label", "value", "unit_id"]
    write_csv(output, "hardware_measures.csv", measurement_columns, hardware_measures)
    write_csv(output, "geometries.csv", ["id", "feature_id", "description"], geometries)
    write_csv(output, "dimension_notes.csv", ["component_id", "description"], dimension_notes)
    write_csv(output, "dimension_measures.csv", measurement_columns, dimension_measures)
    write_csv(output, "specifications.csv", ["id", "owner_id", "kind_iri", "label"], specifications)
    write_csv(output, "thresholds.csv", ["id", "specification_id", "class_iri", "label", "value", "unit_iri"], thresholds)
    write_csv(output, "specification_kinds.csv", ["id", "label"], specification_kinds)
    write_csv(output, "units.csv", ["id", "label"], units)
    (ROOT / "deliverables" / "materialized").mkdir(parents=True, exist_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Directory for normalized CSVs")
    args = parser.parse_args()
    prepare(args.output)


if __name__ == "__main__":
    main()
