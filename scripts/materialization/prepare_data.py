"""Normalize the source CSVs into small, mapping-ready materialization tables."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "scripts" / "data"
PREPARED = SOURCE / "prepared"


def read_rows(path: Path) -> list[dict[str, str]]:
    """Read CSV rows while normalizing BOMs, whitespace, and blank cells."""
    with path.open(encoding="utf-8-sig", newline="") as source_file:
        return [
            {
                key.strip(): (value or "").replace("\u00a0", " ").strip()
                for key, value in row.items()
                if key is not None
            }
            for row in csv.DictReader(source_file)
        ]


def write_rows(path: Path, fieldnames: list[str], rows: Iterable[dict[str, str]]) -> None:
    """Write a deterministic UTF-8 CSV with a stable column order."""
    with path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def add_specification(
    rows: list[dict[str, str]],
    entity_id: str,
    kind: str,
    threshold_role: str,
    raw_value: str,
    unit: str = "",
) -> None:
    """Append a populated threshold and its deterministic specification IDs."""
    value = raw_value.strip()
    if not value:
        return
    rows.append(
        {
            "entity_id": entity_id,
            "kind": kind,
            "threshold_role": threshold_role,
            "value": value,
            "unit": unit,
        }
    )


def collect_hardware_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Collect robot records and attachable objects without asserting roles."""
    robots: list[dict[str, str]] = []
    components: list[dict[str, str]] = []
    for filename in ("robot-arm-specs.csv", "robot-mobile-specs.csv"):
        for row in read_rows(SOURCE / filename):
            robots.append(
                {
                    "serial": row["Serial"],
                    "name": row["Name"],
                    "type": row["Type"],
                }
            )
    for filename, name_column in (
        ("robot-attachment-specs.csv", "Attachment"),
        ("robot-vision-accessory-specs.csv", "Attachment"),
    ):
        for row in read_rows(SOURCE / filename):
            components.append(
                {
                    "serial": row["Serial"],
                    "name": row[name_column],
                    "type": row["Type"],
                }
            )
    return robots, components


def create_capability_tables(agent_ids: set[str], component_ids: set[str]) -> None:
    """Split hardware capabilities by whether the serial identifies an agent."""
    agent_capabilities: list[dict[str, str]] = []
    component_capabilities: list[dict[str, str]] = []
    for row in read_rows(SOURCE / "robot-hardware-capabilities.csv"):
        normalized = {"serial": row["Serial"], "capability_class": row["Capability Class"]}
        if normalized["serial"] in agent_ids:
            agent_capabilities.append(normalized)
        elif normalized["serial"] in component_ids:
            component_capabilities.append(normalized)
    columns = ["serial", "capability_class"]
    write_rows(PREPARED / "agent-capabilities.csv", columns, agent_capabilities)
    write_rows(PREPARED / "component-capabilities.csv", columns, component_capabilities)


def collect_specifications() -> None:
    """Flatten approved numeric source fields to populated ontology thresholds."""
    rows: list[dict[str, str]] = []
    specs: tuple[tuple[str, str, str, str], ...] = (
        ("Repeated Positioning Accuracy (±mm)", "repeatedPositioningAccuracy", "nominal", "millimeter"),
        ("Min Power Output (Volts)", "voltage", "lower", "volt"),
        ("Max Power Output (Volts)", "voltage", "upper", "volt"),
        ("Max Payload (Grams)", "payload", "nominal", "gram"),
        ("Weight (Grams)", "weight", "nominal", "gram"),
        ("Weight (g)", "weight", "nominal", "gram"),
        ("Min Operating Temperature (Celsius)", "temperature", "lower", "celsius"),
        ("Max Operating Temperature (Celsius)", "temperature", "upper", "celsius"),
        ("Operating Range (mm)", "workingRadius", "nominal", "millimeter"),
        ("Min Stroke (mm)", "stroke", "lower", "millimeter"),
        ("Max Stroke (mm)", "stroke", "upper", "millimeter"),
        ("Min Grip Force (N)", "gripForce", "lower", "newton"),
        ("Max Grip Force (N)", "gripForce", "upper", "newton"),
        ("Form-fit grip payload (Grams)", "formFitGrip", "nominal", "gram"),
        ("Friction-grip-payload (Grams)", "frictionGrip", "nominal", "gram"),
        ("Ideal Depth Min (cm)", "depth", "lower", "centimeter"),
        ("Ideal Depth Max (cm)", "depth", "upper", "centimeter"),
        ("Depth Max Frame Rate (fps)", "frequency", "nominal", "hertz"),
    )

    for filename in (
        "robot-arm-specs.csv",
        "robot-mobile-specs.csv",
        "robot-attachment-specs.csv",
        "robot-vision-accessory-specs.csv",
    ):
        for row in read_rows(SOURCE / filename):
            for column, kind, role, unit in specs:
                add_specification(rows, row["Serial"], kind, role, row.get(column, ""), unit)

    for row in read_rows(SOURCE / "nist-task-board-1-parts.csv"):
        entity_id = row["part_id"]
        for column, kind in (
            ("length (mm)", "length"),
            ("width (mm)", "width"),
            ("height (mm)", "height"),
            ("depth (mm)", "depth"),
            ("diameter (mm)", "diameter"),
            ("radius (mm)", "radius"),
            ("pitch (mm)", "pitch"),
        ):
            add_specification(rows, entity_id, kind, "nominal", row.get(column, ""), "millimeter")
        add_specification(rows, entity_id, "weight", "nominal", row.get("weight (kg)", ""), "kilogram")

    write_rows(
        PREPARED / "specifications.csv",
        ["entity_id", "kind", "threshold_role", "value", "unit"],
        rows,
    )


def collect_capability_specifications() -> None:
    """Link capabilities only to source specifications that describe them."""
    kinds_by_capability = {
        "Reach": {"workingRadius", "repeatedPositioningAccuracy"},
        "Open": {"stroke"},
        "Close": {"stroke", "gripForce"},
        "Pick": {"payload", "formFitGrip", "frictionGrip"},
        "Place": {"payload", "formFitGrip", "frictionGrip"},
        "Distance": {"depth"},
        "Vision": {"frequency"},
    }
    specification_kinds_by_serial: dict[str, set[str]] = {}
    for row in read_rows(PREPARED / "specifications.csv"):
        specification_kinds_by_serial.setdefault(row["entity_id"], set()).add(row["kind"])

    rows: list[dict[str, str]] = []
    for capability in read_rows(SOURCE / "robot-hardware-capabilities.csv"):
        serial = capability["Serial"]
        capability_class = capability["Capability Class"]
        for kind in sorted(kinds_by_capability.get(capability_class, set())):
            if kind in specification_kinds_by_serial.get(serial, set()):
                rows.append(
                    {
                        "serial": serial,
                        "capability_class": capability_class,
                        "kind": kind,
                    }
                )

    write_rows(
        PREPARED / "capability-specifications.csv",
        ["serial", "capability_class", "kind"],
        rows,
    )


def prepare_data() -> None:
    """Create only the derived tables used by the itemized YARRRML mappings."""
    PREPARED.mkdir(parents=True, exist_ok=True)
    robots, components = collect_hardware_rows()
    agents = read_rows(PREPARED / "agents.csv")
    agent_ids = {row["id"] for row in agents}
    component_ids = {row["serial"] for row in components}

    write_rows(PREPARED / "robot-hardware.csv", ["serial", "name", "type"], robots)
    write_rows(PREPARED / "component-objects.csv", ["serial", "name", "type"], components)
    create_capability_tables(agent_ids, component_ids)

    component_links = [
        {"part_id": row["attachment_id"], "whole_id": row["id"]}
        for row in agents
        if row.get("attachment_id") and row["attachment_id"] in component_ids | agent_ids
    ]
    write_rows(PREPARED / "component-links.csv", ["part_id", "whole_id"], component_links)
    collect_specifications()
    collect_capability_specifications()


if __name__ == "__main__":
    prepare_data()
