"""Apply the generated axiom report to the RDF ontology.

Requires rdflib. Run without --apply to preview changes; --apply updates the
ontology in place after parsing the result to ensure it remains valid RDF/XML.
"""

import argparse
import hashlib
import os
from pathlib import Path
import re
import stat
import tempfile
import xml.etree.ElementTree as ET

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AXIOMS = (
    PROJECT_ROOT
    / "deliverables/ontology/Autonomous-Robotic-Orchestration-Modular-Ontology_axioms.md"
)
DEFAULT_ONTOLOGY = PROJECT_ROOT / "deliverables/ontology/robo-ont.rdf"
IMPORTED_PROPERTIES = {
    "partOf": "http://daselab.org/ContextualizedWinstonPartWhole#part-of",
    "spatiallyLocatedIn": (
        "http://daselab.org/ContextualizedWinstonPartWhole#spatially-located-in"
    ),
}
AXIOM_LINE = re.compile(r"^([^:]+): `([^`]+)`$")


def render_axiom(category: str, subject: str, relation: str, target: str) -> str:
    """Recreate the report expression to catch mismatched headings and lines."""
    renderings = {
        "subclass": f"{subject} SubClassOf {target}",
        "disjoint": f"{subject} DisjointWith {target}",
        "global domain": f"{relation} some owl:Thing SubClassOf {subject}",
        "scoped domain": f"{relation} some {target} SubClassOf {subject}",
        "global range": f"owl:Thing SubClassOf {relation} only {target}",
        "scoped range": f"{subject} SubClassOf {relation} only {target}",
        "existential": f"{subject} SubClassOf {relation} some {target}",
        "inverse existential": (
            f"{target} SubClassOf inverse {relation} some {subject}"
        ),
        "qualified functionality": (
            f"owl:Thing SubClassOf {relation} max 1 {target}"
        ),
        "scoped functionality": (
            f"{subject} SubClassOf {relation} max 1 owl:Thing"
        ),
        "qualified scoped functionality": (
            f"{subject} SubClassOf {relation} max 1 {target}"
        ),
    }
    if category not in renderings:
        raise ValueError(f"Unsupported axiom category: {category}")
    return renderings[category]


def read_axioms(path: Path) -> list[tuple[str, str, str, str]]:
    """Read every report entry and verify its expression matches its heading."""
    entries = []
    heading = None
    for line_number, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            parts = line[2:].split()
            if len(parts) != 3:
                raise ValueError(f"{path}:{line_number}: expected a three-part heading")
            heading = parts
            continue
        match = AXIOM_LINE.fullmatch(line)
        if match is None or heading is None:
            raise ValueError(f"{path}:{line_number}: unexpected report line: {line}")
        category, expression = match.groups()
        subject, relation, target = heading
        expected = render_axiom(category, subject, relation, target)
        if expression != expected:
            raise ValueError(
                f"{path}:{line_number}: expected `{expected}`, got `{expression}`"
            )
        entries.append((category, subject, relation, target))
    if not entries:
        raise ValueError(f"No axiom entries found in {path}")
    return entries


def ontology_base(graph: Graph) -> str:
    ontology_iris = list(graph.subjects(RDF.type, OWL.Ontology))
    if len(ontology_iris) != 1 or not isinstance(ontology_iris[0], URIRef):
        raise ValueError("Expected exactly one named owl:Ontology in the RDF file")
    ontology_iri = str(ontology_iris[0])
    namespace = ontology_iri if ontology_iri.endswith("#") else ontology_iri + "#"
    if not any(
        str(entity).startswith(namespace)
        for entity in graph.subjects(RDF.type, OWL.Class)
    ):
        raise ValueError(f"No declared classes use the ontology namespace {namespace}")
    return namespace


def class_or_datatype(name: str, base: str) -> URIRef:
    if name.startswith("xsd:"):
        return XSD[name.removeprefix("xsd:")]
    return URIRef(base + name)


def declared_names(graph: Graph, kind: URIRef, base: str) -> set[str]:
    return {
        str(entity).removeprefix(base)
        for entity in graph.subjects(RDF.type, kind)
        if str(entity).startswith(base)
    }


def resolve_property(
    name: str,
    base: str,
    graph: Graph,
    imported_graph: Graph,
    imported_mode: str,
) -> tuple[URIRef, bool] | None:
    """Resolve a property IRI and whether it is a datatype property."""
    if name in IMPORTED_PROPERTIES:
        if imported_mode == "skip":
            return None
        if imported_mode == "map":
            property_iri = URIRef(IMPORTED_PROPERTIES[name])
            if (property_iri, RDF.type, OWL.ObjectProperty) not in imported_graph:
                raise ValueError(f"Imported property not found: {property_iri}")
            return property_iri, False
        raise ValueError(f"Unsupported imported-property mode: {imported_mode}")

    property_iri = URIRef(base + name)
    if (property_iri, RDF.type, OWL.ObjectProperty) in graph:
        return property_iri, False
    if (property_iri, RDF.type, OWL.DatatypeProperty) in graph:
        return property_iri, True
    raise ValueError(f"Property {name} is not declared in the ontology")


def restriction_key(
    position: str,
    owner: URIRef,
    property_iri: URIRef,
    kind: str,
    filler: URIRef | None = None,
    inverse: bool = False,
) -> tuple[str, ...]:
    return (
        position,
        str(owner),
        str(property_iri),
        kind,
        str(filler) if filler is not None else "",
        "inverse" if inverse else "direct",
    )


def axiom_key(
    entry: tuple[str, str, str, str],
    base: str,
    property_iri: URIRef | None,
) -> tuple[str, ...]:
    category, subject, _, target = entry
    owner = URIRef(base + subject)
    filler = class_or_datatype(target, base)
    if category == "subclass":
        return ("subclass", str(owner), str(filler))
    if category == "disjoint":
        return ("disjoint", *sorted((str(owner), str(filler))))
    if property_iri is None:
        raise ValueError(f"Property missing for {entry}")
    if category == "global domain":
        return ("domain", str(property_iri), str(owner))
    if category == "global range":
        return ("range", str(property_iri), str(filler))
    if category == "scoped domain":
        return restriction_key("left", owner, property_iri, "some", filler)
    if category == "scoped range":
        return restriction_key("right", owner, property_iri, "only", filler)
    if category == "existential":
        return restriction_key("right", owner, property_iri, "some", filler)
    if category == "inverse existential":
        return restriction_key("right", filler, property_iri, "some", owner, True)
    if category == "qualified functionality":
        return restriction_key("right", OWL.Thing, property_iri, "max_qualified", filler)
    if category == "scoped functionality":
        # The report's owl:Thing filler is invalid for hasSerial, a data property.
        # An unqualified max 1 restriction preserves the intended cardinality.
        return restriction_key("right", owner, property_iri, "max")
    if category == "qualified scoped functionality":
        return restriction_key("right", owner, property_iri, "max_qualified", filler)
    raise ValueError(f"Unsupported axiom category: {category}")


def parse_restriction(
    graph: Graph, node: BNode
) -> tuple[URIRef, str, URIRef | None, bool] | None:
    if (node, RDF.type, OWL.Restriction) not in graph:
        return None
    property_node = graph.value(node, OWL.onProperty)
    inverse = isinstance(property_node, BNode)
    if inverse:
        property_node = graph.value(property_node, OWL.inverseOf)
    if not isinstance(property_node, URIRef):
        return None
    for predicate, kind in (
        (OWL.someValuesFrom, "some"),
        (OWL.allValuesFrom, "only"),
        (OWL.maxQualifiedCardinality, "max_qualified"),
        (OWL.maxCardinality, "max"),
    ):
        value = graph.value(node, predicate)
        if value is None:
            continue
        if kind.startswith("max"):
            if not isinstance(value, Literal) or str(value) != "1":
                return None
            filler = graph.value(node, OWL.onClass) or graph.value(node, OWL.onDataRange)
        else:
            filler = value
        if filler is not None and not isinstance(filler, URIRef):
            return None
        return property_node, kind, filler, inverse
    return None


def existing_axiom_keys(graph: Graph) -> set[tuple[str, ...]]:
    keys = set()
    for subject, target in graph.subject_objects(RDFS.subClassOf):
        if isinstance(subject, URIRef) and isinstance(target, URIRef):
            keys.add(("subclass", str(subject), str(target)))
        for position, owner, restriction in (
            ("left", target, subject),
            ("right", subject, target),
        ):
            if not isinstance(owner, URIRef) or not isinstance(restriction, BNode):
                continue
            details = parse_restriction(graph, restriction)
            if details is not None:
                property_iri, kind, filler, inverse = details
                keys.add(
                    restriction_key(position, owner, property_iri, kind, filler, inverse)
                )
    for subject, target in graph.subject_objects(OWL.disjointWith):
        if isinstance(subject, URIRef) and isinstance(target, URIRef):
            keys.add(("disjoint", *sorted((str(subject), str(target)))))
    for property_iri, owner in graph.subject_objects(RDFS.domain):
        keys.add(("domain", str(property_iri), str(owner)))
    for property_iri, target in graph.subject_objects(RDFS.range):
        keys.add(("range", str(property_iri), str(target)))
    return keys


def add_axiom(
    graph: Graph,
    key: tuple[str, ...],
    data_property: bool,
) -> None:
    """Add one axiom using the OWL 2 RDF mapping for class restrictions."""
    if key[0] == "subclass":
        graph.add((URIRef(key[1]), RDFS.subClassOf, URIRef(key[2])))
        return
    if key[0] == "disjoint":
        graph.add((URIRef(key[1]), OWL.disjointWith, URIRef(key[2])))
        return
    if key[0] in {"domain", "range"}:
        predicate = RDFS.domain if key[0] == "domain" else RDFS.range
        graph.add((URIRef(key[1]), predicate, URIRef(key[2])))
        return

    position, owner, property_name, kind, filler, direction = key
    digest = hashlib.sha256(repr(key).encode()).hexdigest()[:24]
    restriction = BNode(f"axiom_{digest}")
    property_node = URIRef(property_name)
    if direction == "inverse":
        inverse_node = BNode(f"inverse_{digest}")
        graph.add((inverse_node, OWL.inverseOf, property_node))
        property_node = inverse_node
    graph.add((restriction, RDF.type, OWL.Restriction))
    graph.add((restriction, OWL.onProperty, property_node))
    if kind in {"some", "only"}:
        predicate = OWL.someValuesFrom if kind == "some" else OWL.allValuesFrom
        graph.add((restriction, predicate, URIRef(filler)))
    elif kind == "max_qualified":
        graph.add(
            (restriction, OWL.maxQualifiedCardinality, Literal(1, datatype=XSD.nonNegativeInteger))
        )
        qualifier = OWL.onDataRange if data_property else OWL.onClass
        graph.add((restriction, qualifier, URIRef(filler)))
    elif kind == "max":
        graph.add(
            (restriction, OWL.maxCardinality, Literal(1, datatype=XSD.nonNegativeInteger))
        )
    else:
        raise ValueError(f"Unsupported restriction kind: {kind}")

    if position == "left":
        subclass = (restriction, RDFS.subClassOf, URIRef(owner))
    else:
        subclass = (URIRef(owner), RDFS.subClassOf, restriction)
    graph.add(subclass)


def serialize_additions(graph: Graph) -> str:
    ET.register_namespace("rdf", str(RDF))
    ET.register_namespace("rdfs", str(RDFS))
    ET.register_namespace("owl", str(OWL))
    root = ET.fromstring(graph.serialize(format="xml"))
    fragments = []
    for child in root:
        ET.indent(child, space="    ")
        fragment = ET.tostring(child, encoding="unicode")
        indented_lines = [
            "    " + line if line.strip() else "" for line in fragment.splitlines()
        ]
        fragments.append("\n".join(indented_lines))
    return "\n".join(fragments)


def apply_axioms(
    report_path: Path,
    ontology_path: Path,
    imported_mode: str,
    write_changes: bool,
) -> None:
    entries = read_axioms(report_path)
    source_bytes = ontology_path.read_bytes()
    source_text = source_bytes.decode("utf-8")
    ontology = Graph().parse(data=source_text, format="xml")
    base = ontology_base(ontology)
    imported_graph = Graph()
    imported_path = ontology_path.with_name("contextualized-winston-part-whole.rdf")
    if imported_mode == "map":
        imported_graph.parse(imported_path)
        spatial_property = URIRef(IMPORTED_PROPERTIES["spatiallyLocatedIn"])
        has_global_domain = any(
            category == "global domain" and relation == "spatiallyLocatedIn"
            for category, _, relation, _ in entries
        )
        if has_global_domain and (
            spatial_property, RDF.type, OWL.ReflexiveProperty
        ) in imported_graph:
            raise ValueError(
                "Mapping the global domain of imported reflexive "
                "spatially-located-in to SpatialThing would imply that every "
                "individual is a SpatialThing; use --imported-properties skip"
            )

    new_class_names = {
        name
        for category, subject, _, target in entries
        if category == "subclass"
        for name in (subject, target)
    }
    known_classes = declared_names(ontology, OWL.Class, base) | new_class_names
    known_classes |= declared_names(imported_graph, OWL.Class, base)
    additions = Graph()
    for class_name in sorted(new_class_names - declared_names(ontology, OWL.Class, base)):
        additions.add((URIRef(base + class_name), RDF.type, OWL.Class))

    existing = existing_axiom_keys(ontology) | existing_axiom_keys(imported_graph)
    added = 0
    skipped_existing = 0
    skipped_imported = 0
    for entry in entries:
        category, subject, relation, target = entry
        resolved = None
        if category not in {"subclass", "disjoint"}:
            resolved = resolve_property(relation, base, ontology, imported_graph, imported_mode)
            if resolved is None:
                skipped_imported += 1
                continue
        property_iri, data_property = resolved if resolved is not None else (None, False)
        if category == "subclass" and relation != "SubClassOf":
            raise ValueError(f"Expected SubClassOf in subclass heading: {entry}")
        if category != "subclass":
            class_names = [subject]
            if category not in {"global domain", "scoped functionality"}:
                class_names.append(target)
            for name in class_names:
                if not name.startswith("xsd:") and name not in known_classes:
                    raise ValueError(
                        f"Class {name} is not declared or introduced by a subclass axiom"
                    )
        if property_iri is not None:
            if data_property != target.startswith("xsd:"):
                raise ValueError(f"Property type and target disagree: {entry}")
            if category in {"scoped domain", "inverse existential"} and data_property:
                raise ValueError(f"Inverse or scoped domain requires an object property: {entry}")
        key = axiom_key(entry, base, property_iri)
        if key in existing:
            skipped_existing += 1
            continue
        add_axiom(additions, key, data_property)
        existing.add(key)
        added += 1

    print(f"Report entries: {len(entries)}")
    print(f"New axioms: {added}; already present or repeated: {skipped_existing}")
    print(f"Imported-property axioms skipped: {skipped_imported}")
    new_class_count = len(new_class_names - declared_names(ontology, OWL.Class, base))
    print(f"New class declarations: {new_class_count}")
    if not write_changes or not additions:
        return

    closing_tag = "</rdf:RDF>"
    if source_text.count(closing_tag) != 1:
        raise ValueError("Expected exactly one RDF/XML closing tag")
    fragment = serialize_additions(additions)
    generated_block = (
        "    <!-- Axioms generated from the ontology axiom report. -->\n"
        f"{fragment}\n\n"
    )
    output_text = source_text.replace(closing_tag, generated_block + closing_tag, 1)
    reparsed = Graph().parse(data=output_text, format="xml")
    if len(reparsed) != len(ontology) + len(additions):
        raise ValueError("Round-trip verification found missing or duplicate RDF triples")
    if ontology_path.read_bytes() != source_bytes:
        raise RuntimeError("Ontology changed during import; no file was written")

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=ontology_path.parent, delete=False
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(output_text)
        os.chmod(temporary_path, stat.S_IMODE(ontology_path.stat().st_mode))
        os.replace(temporary_path, ontology_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    print(f"Updated {ontology_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--axioms", type=Path, default=DEFAULT_AXIOMS)
    parser.add_argument("--ontology", type=Path, default=DEFAULT_ONTOLOGY)
    parser.add_argument(
        "--imported-properties",
        choices=("map", "skip"),
        required=True,
        help="Map report aliases to imported property IRIs, or skip their four axioms",
    )
    parser.add_argument("--apply", action="store_true", help="Update the RDF file in place")
    args = parser.parse_args()
    apply_axioms(args.axioms, args.ontology, args.imported_properties, args.apply)


if __name__ == "__main__":
    main()
