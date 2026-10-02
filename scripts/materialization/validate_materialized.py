"""Check materialized feature geometry and physical specifications against CSVs."""

from __future__ import annotations

import csv
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD

from prepare_data import make_specifications


ROOT = Path(__file__).resolve().parents[2]
PREPARED = ROOT / "scripts" / "data" / "prepared"
ONTOLOGY = ROOT / "deliverables" / "ontology" / "robo-ont.rdf"
MATERIALIZED = ROOT / "deliverables" / "materialized" / "scenario.nt"
ROBO_ONT = Namespace(
    "https://github.com/kastle-lab/Autonomous-Robotic-Orchestration-Modular-Ontology/lod/ontology#"
)
ROBO_R = Namespace(
    "https://github.com/kastle-lab/Autonomous-Robotic-Orchestration-Modular-Ontology/lod/resource#"
)


def read_rows(name: str) -> list[dict[str, str]]:
    with (PREPARED / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def require_triple(graph: Graph, subject: URIRef, predicate: URIRef, value: object) -> None:
    if (subject, predicate, value) not in graph:
        raise ValueError(f"Missing triple: {subject} {predicate} {value}")


def require_exact_links(
    graph: Graph, predicate: URIRef, expected: set[tuple[URIRef, URIRef]]
) -> None:
    actual = {(subject, value) for subject, _, value in graph.triples((None, predicate, None))}
    if actual != expected:
        raise ValueError(
            f"{predicate}: {len(expected - actual)} missing and {len(actual - expected)} extra links"
        )


def validate() -> None:
    ontology = Graph().parse(ONTOLOGY)
    graph = Graph().parse(MATERIALIZED, format="nt")
    combined = graph + ontology
    require_triple(ontology, ROBO_ONT.hasGeometry, RDFS.domain, ROBO_ONT.Feature)
    require_triple(
        ontology, ROBO_ONT.hasPhysicalSpecification, RDFS.domain, ROBO_ONT.SpatialThing
    )

    features = read_rows("features.csv")
    geometries = read_rows("geometries.csv")
    specifications = read_rows("specifications.csv")
    thresholds = read_rows("thresholds.csv")
    measures = read_rows("dimension_measures.csv") + read_rows("hardware_measures.csv")
    expected_tables = make_specifications(measures)
    for name, expected in zip(
        ("specifications.csv", "thresholds.csv", "specification_kinds.csv", "units.csv"),
        expected_tables,
    ):
        if read_rows(name) != expected:
            raise ValueError(f"{name}: prepared rows differ from source measurements")

    expected_hosts = set()
    for row in features:
        feature = ROBO_R[row["id"]]
        require_triple(graph, feature, RDF.type, ROBO_ONT.Feature)
        host = ROBO_R[row["host_id"]]
        require_triple(graph, host, RDF.type, ROBO_ONT.Object)
        expected_hosts.add((host, feature))
    require_exact_links(graph, ROBO_ONT.hasFeature, expected_hosts)
    if set(graph.subjects(RDF.type, ROBO_ONT.Feature)) != {feature for _, feature in expected_hosts}:
        raise ValueError("Feature individuals differ from the prepared feature table")

    expected_geometries = set()
    for row in geometries:
        geometry = ROBO_R[row["id"]]
        feature = ROBO_R[row["feature_id"]]
        metadata = ROBO_R["metadata_" + row["id"]]
        require_triple(graph, geometry, RDF.type, ROBO_ONT.Geometry)
        require_triple(graph, geometry, ROBO_ONT.hasMetadata, metadata)
        require_triple(graph, metadata, ROBO_ONT.hasDescription, Literal(row["description"]))
        expected_geometries.add((feature, geometry))
    require_exact_links(graph, ROBO_ONT.hasGeometry, expected_geometries)
    if set(graph.subjects(RDF.type, ROBO_ONT.Geometry)) != {geometry for _, geometry in expected_geometries}:
        raise ValueError("Geometry individuals differ from the prepared geometry table")
    if any((subject, RDF.type, ROBO_ONT.Object) in graph for subject, _ in expected_geometries):
        raise ValueError("An Object is directly linked to Geometry")

    expected_owners = set()
    for row in specifications:
        specification = ROBO_R[row["id"]]
        require_triple(graph, specification, RDF.type, ROBO_ONT.Specification)
        require_triple(
            graph, specification, ROBO_ONT.isSpecificationOf, URIRef(row["kind_iri"])
        )
        kind = URIRef(row["kind_iri"])
        if (kind, RDF.type, ROBO_ONT.SpecificationKind) not in combined:
            raise ValueError(f"{kind}: missing SpecificationKind type")
        expected_owners.add((ROBO_R[row["owner_id"]], specification))
    require_exact_links(graph, ROBO_ONT.hasPhysicalSpecification, expected_owners)
    if set(graph.subjects(RDF.type, ROBO_ONT.Specification)) != {spec for _, spec in expected_owners}:
        raise ValueError("Specification individuals differ from the prepared table")

    expected_thresholds = set()
    for row in thresholds:
        threshold = ROBO_R[row["id"]]
        specification = ROBO_R[row["specification_id"]]
        require_triple(graph, threshold, RDF.type, ROBO_ONT.Threshold)
        require_triple(graph, threshold, RDF.type, ROBO_ONT[row["class_iri"]])
        unit = URIRef(row["unit_iri"])
        require_triple(graph, threshold, ROBO_ONT.isUnitOf, unit)
        if (unit, RDF.type, ROBO_ONT.Unit) not in combined:
            raise ValueError(f"{unit}: missing Unit type")
        values = list(graph.objects(threshold, ROBO_ONT.hasValue))
        if len(values) != 1 or values[0].datatype != XSD.double:
            raise ValueError(f"{threshold}: expected one xsd:double value")
        if float(values[0]) != float(row["value"]):
            raise ValueError(f"{threshold}: value differs from prepared CSV")
        expected_thresholds.add((specification, threshold))
    require_exact_links(graph, ROBO_ONT.hasThreshold, expected_thresholds)
    if set(graph.subjects(RDF.type, ROBO_ONT.Threshold)) != {item for _, item in expected_thresholds}:
        raise ValueError("Threshold individuals differ from the prepared table")

    for row in read_rows("dimension_notes.csv"):
        metadata = ROBO_R["metadata_" + row["component_id"]]
        require_triple(graph, metadata, ROBO_ONT.hasDescription, Literal(row["description"]))

    print(
        f"Validated {len(graph)} triples: {len(features)} hosted features, "
        f"{len(geometries)} geometries, {len(specifications)} specifications, "
        f"and {len(thresholds)} numeric thresholds."
    )


if __name__ == "__main__":
    validate()
