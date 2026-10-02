# Goal hasDeadline TemporalExtent
disjoint: `Goal DisjointWith TemporalExtent`

existential: `Goal SubClassOf hasDeadline some TemporalExtent`

global domain: `hasDeadline some owl:Thing SubClassOf Goal`

global range: `owl:Thing SubClassOf hasDeadline only TemporalExtent`

qualified scoped functionality: `Goal SubClassOf hasDeadline max 1 TemporalExtent`

# Goal isWithinBounds SpatialExtent
disjoint: `Goal DisjointWith SpatialExtent`

global domain: `isWithinBounds some owl:Thing SubClassOf Goal`

global range: `owl:Thing SubClassOf isWithinBounds only SpatialExtent`

# Goal hasOperationalExtent SpatialExtent
disjoint: `Goal DisjointWith SpatialExtent`

global domain: `hasOperationalExtent some owl:Thing SubClassOf Goal`

global range: `owl:Thing SubClassOf hasOperationalExtent only SpatialExtent`

# Goal hasSuccessState State
disjoint: `Goal DisjointWith State`

existential: `Goal SubClassOf hasSuccessState some State`

global range: `owl:Thing SubClassOf hasSuccessState only State`

# Goal hasTask Task
disjoint: `Goal DisjointWith Task`

inverse existential: `Task SubClassOf inverse hasTask some Goal`

scoped domain: `hasTask some Task SubClassOf Goal`

scoped range: `Goal SubClassOf hasTask only Task`

# Task providesRole Role
disjoint: `Task DisjointWith Role`

inverse existential: `Role SubClassOf inverse providesRole some Task`

scoped range: `Task SubClassOf providesRole only Role`

# Task requiresSpatialThing SpatialThing
disjoint: `Task DisjointWith SpatialThing`

existential: `Task SubClassOf requiresSpatialThing some SpatialThing`

global domain: `requiresSpatialThing some owl:Thing SubClassOf Task`

global range: `owl:Thing SubClassOf requiresSpatialThing only SpatialThing`

# Task requiresArchetype Archetype
disjoint: `Task DisjointWith Archetype`

existential: `Task SubClassOf requiresArchetype some Archetype`

global domain: `requiresArchetype some owl:Thing SubClassOf Task`

global range: `owl:Thing SubClassOf requiresArchetype only Archetype`

qualified scoped functionality: `Task SubClassOf requiresArchetype max 1 Archetype`

# SpatialThing hasMetadata Metadata
disjoint: `SpatialThing DisjointWith Metadata`

global range: `owl:Thing SubClassOf hasMetadata only Metadata`

qualified functionality: `owl:Thing SubClassOf hasMetadata max 1 Metadata`

# SpatialThing hasSpatiotemporalExtent SpatiotemporalExtent
disjoint: `SpatialThing DisjointWith SpatiotemporalExtent`

global range: `owl:Thing SubClassOf hasSpatiotemporalExtent only SpatiotemporalExtent`

# SpatialThing currentState State
disjoint: `SpatialThing DisjointWith State`

existential: `SpatialThing SubClassOf currentState some State`

global range: `owl:Thing SubClassOf currentState only State`

qualified scoped functionality: `SpatialThing SubClassOf currentState max 1 State`

# SpatialThing enablesCapability Capability
disjoint: `SpatialThing DisjointWith Capability`

global domain: `enablesCapability some owl:Thing SubClassOf SpatialThing`

global range: `owl:Thing SubClassOf enablesCapability only Capability`

inverse existential: `Capability SubClassOf inverse enablesCapability some SpatialThing`

# SpatialThing assumesRole Role
disjoint: `SpatialThing DisjointWith Role`

global domain: `assumesRole some owl:Thing SubClassOf SpatialThing`

global range: `owl:Thing SubClassOf assumesRole only Role`

inverse existential: `Role SubClassOf inverse assumesRole some SpatialThing`

# Agent fulfillsArchetype Archetype
disjoint: `Agent DisjointWith Archetype`

global range: `owl:Thing SubClassOf fulfillsArchetype only Archetype`

# Agent hasCapability Capability
disjoint: `Agent DisjointWith Capability`

global domain: `hasCapability some owl:Thing SubClassOf Agent`

global range: `owl:Thing SubClassOf hasCapability only Capability`

# SpatialThing hasSpec Specification
disjoint: `SpatialThing DisjointWith Specification`

global range: `owl:Thing SubClassOf hasSpec only Specification`

# Archetype requiresCapability Capability
disjoint: `Archetype DisjointWith Capability`

global domain: `requiresCapability some owl:Thing SubClassOf Archetype`

global range: `owl:Thing SubClassOf requiresCapability only Capability`

# Capability enablesAction Action
disjoint: `Capability DisjointWith Action`

global domain: `enablesAction some owl:Thing SubClassOf Capability`

global range: `owl:Thing SubClassOf enablesAction only Action`

inverse existential: `Action SubClassOf inverse enablesAction some Capability`

scoped range: `Capability SubClassOf enablesAction only Action`

# Capability enabledBySpatialThing SpatialThing
disjoint: `Capability DisjointWith SpatialThing`

existential: `Capability SubClassOf enabledBySpatialThing some SpatialThing`

global range: `owl:Thing SubClassOf enabledBySpatialThing only SpatialThing`

# Capability hasSpec Specification
disjoint: `Capability DisjointWith Specification`

existential: `Capability SubClassOf hasSpec some Specification`

global range: `owl:Thing SubClassOf hasSpec only Specification`

# Specification hasThreshold Threshold
disjoint: `Specification DisjointWith Threshold`

existential: `Specification SubClassOf hasThreshold some Threshold`

global domain: `hasThreshold some owl:Thing SubClassOf Specification`

global range: `owl:Thing SubClassOf hasThreshold only Threshold`

# Specification isSpecificationOf SpecificationKind
disjoint: `Specification DisjointWith SpecificationKind`

global domain: `isSpecificationOf some owl:Thing SubClassOf Specification`

global range: `owl:Thing SubClassOf isSpecificationOf only SpecificationKind`

# Threshold isUnitOf Unit
disjoint: `Threshold DisjointWith Unit`

global domain: `isUnitOf some owl:Thing SubClassOf Threshold`

global range: `owl:Thing SubClassOf isUnitOf only Unit`

# Metadata isOfFormat Format
disjoint: `Metadata DisjointWith Format`

existential: `Metadata SubClassOf isOfFormat some Format`

global domain: `isOfFormat some owl:Thing SubClassOf Metadata`

global range: `owl:Thing SubClassOf isOfFormat only Format`

qualified scoped functionality: `Metadata SubClassOf isOfFormat max 1 Format`

# Metadata hasLocation Location
disjoint: `Metadata DisjointWith Location`

global domain: `hasLocation some owl:Thing SubClassOf Metadata`

global range: `owl:Thing SubClassOf hasLocation only Location`

inverse existential: `Location SubClassOf inverse hasLocation some Metadata`

qualified scoped functionality: `Metadata SubClassOf hasLocation max 1 Location`

# Role hasTemporalExtent TemporalExtent
existential: `Role SubClassOf hasTemporalExtent some TemporalExtent`

qualified scoped functionality: `Role SubClassOf hasTemporalExtent max 1 TemporalExtent`

# Threshold hasValue xsd:double
existential: `Threshold SubClassOf hasValue some xsd:double`

qualified scoped functionality: `Threshold SubClassOf hasValue max 1 xsd:double`

# Metadata hasName xsd:string
existential: `Metadata SubClassOf hasName some xsd:string`

global domain: `hasName some owl:Thing SubClassOf Metadata`

global range: `owl:Thing SubClassOf hasName only xsd:string`

qualified scoped functionality: `Metadata SubClassOf hasName max 1 xsd:string`

# SpatialThing hasPhysicalSpecification Specification
global domain: `hasPhysicalSpecification some owl:Thing SubClassOf SpatialThing`

global range: `owl:Thing SubClassOf hasPhysicalSpecification only Specification`

# SpatialThing partOf SpatialThing
global domain: `partOf some owl:Thing SubClassOf SpatialThing`

global range: `owl:Thing SubClassOf partOf only SpatialThing`

# SpatialThing spatiallyLocatedIn SpatialThing
global domain: `spatiallyLocatedIn some owl:Thing SubClassOf SpatialThing`

global range: `owl:Thing SubClassOf spatiallyLocatedIn only SpatialThing`

# Metadata hasDescription xsd:string
global domain: `hasDescription some owl:Thing SubClassOf Metadata`

global range: `owl:Thing SubClassOf hasDescription only xsd:string`

qualified scoped functionality: `Metadata SubClassOf hasDescription max 1 xsd:string`

# Metadata hasTag xsd:string
global domain: `hasTag some owl:Thing SubClassOf Metadata`

global range: `owl:Thing SubClassOf hasTag only xsd:string`

# Metadata hasSerial xsd:string
global domain: `hasSerial some owl:Thing SubClassOf Metadata`

global range: `owl:Thing SubClassOf hasSerial only xsd:string`

scoped functionality: `Metadata SubClassOf hasSerial max 1 owl:Thing`

# Goal hasInstructionText xsd:string
global range: `owl:Thing SubClassOf hasInstructionText only xsd:string`

qualified scoped functionality: `Goal SubClassOf hasInstructionText max 1 xsd:string`

# Feature hasGeometry Geometry
global range: `owl:Thing SubClassOf hasGeometry only Geometry`

inverse existential: `Geometry SubClassOf inverse hasGeometry some Feature`

scoped domain: `hasGeometry some Geometry SubClassOf Feature`

# SpatialThing hasFeature Feature
global range: `owl:Thing SubClassOf hasFeature only Feature`

inverse existential: `Feature SubClassOf inverse hasFeature some SpatialThing`

scoped domain: `hasFeature some Feature SubClassOf SpatialThing`

# Location asString xsd:string
global range: `owl:Thing SubClassOf asString only xsd:string`

# Location hasURI xsd:anyURI
global range: `owl:Thing SubClassOf hasURI only xsd:anyURI`

qualified scoped functionality: `Location SubClassOf hasURI max 1 xsd:anyURI`

# Location hasIP xsd:integer
global range: `owl:Thing SubClassOf hasIP only xsd:integer`

qualified scoped functionality: `Location SubClassOf hasIP max 1 xsd:integer`

# Location hasFilePath xsd:string
global range: `owl:Thing SubClassOf hasFilePath only xsd:string`

qualified scoped functionality: `Location SubClassOf hasFilePath max 1 xsd:string`

# Goal hasSubGoal Goal
scoped domain: `hasSubGoal some Goal SubClassOf Goal`

scoped range: `Goal SubClassOf hasSubGoal only Goal`

# Task dependsOnTask Task
scoped domain: `dependsOnTask some Task SubClassOf Task`

scoped range: `Task SubClassOf dependsOnTask only Task`

# Task hasNextTask Task
scoped domain: `hasNextTask some Task SubClassOf Task`

scoped range: `Task SubClassOf hasNextTask only Task`

# Environment SubClassOf SpatialThing
subclass: `Environment SubClassOf SpatialThing`

# Object SubClassOf SpatialThing
subclass: `Object SubClassOf SpatialThing`

# Feature SubClassOf SpatialThing
subclass: `Feature SubClassOf SpatialThing`

# Geometry SubClassOf SpatialThing
subclass: `Geometry SubClassOf SpatialThing`

# Agent SubClassOf SpatialThing
subclass: `Agent SubClassOf SpatialThing`

# Target SubClassOf Role
subclass: `Target SubClassOf Role`

# Bystander SubClassOf Role
subclass: `Bystander SubClassOf Role`

# Worker SubClassOf Role
subclass: `Worker SubClassOf Role`

# Obstacle SubClassOf Role
subclass: `Obstacle SubClassOf Role`

# Zone SubClassOf Role
subclass: `Zone SubClassOf Role`

# Staging SubClassOf Zone
subclass: `Staging SubClassOf Zone`

# Storage SubClassOf Zone
subclass: `Storage SubClassOf Zone`

# Workspace SubClassOf Zone
subclass: `Workspace SubClassOf Zone`

# GripperBased SubClassOf Capability
subclass: `GripperBased SubClassOf Capability`

# Open SubClassOf GripperBased
subclass: `Open SubClassOf GripperBased`

# Close SubClassOf GripperBased
subclass: `Close SubClassOf GripperBased`

# Place SubClassOf GripperBased
subclass: `Place SubClassOf GripperBased`

# Pick SubClassOf GripperBased
subclass: `Pick SubClassOf GripperBased`

# SensorBased SubClassOf Capability
subclass: `SensorBased SubClassOf Capability`

# Distance SubClassOf SensorBased
subclass: `Distance SubClassOf SensorBased`

# Audition SubClassOf SensorBased
subclass: `Audition SubClassOf SensorBased`

# Touch SubClassOf SensorBased
subclass: `Touch SubClassOf SensorBased`

# Vision SubClassOf SensorBased
subclass: `Vision SubClassOf SensorBased`

# MotionBased SubClassOf Capability
subclass: `MotionBased SubClassOf Capability`

# Navigate SubClassOf MotionBased
subclass: `Navigate SubClassOf MotionBased`

# Rotate SubClassOf MotionBased
subclass: `Rotate SubClassOf MotionBased`

# Press SubClassOf MotionBased
subclass: `Press SubClassOf MotionBased`

# Push SubClassOf MotionBased
subclass: `Push SubClassOf MotionBased`

# Reach SubClassOf MotionBased
subclass: `Reach SubClassOf MotionBased`

# Pull SubClassOf MotionBased
subclass: `Pull SubClassOf MotionBased`

# PowerBased SubClassOf Capability
subclass: `PowerBased SubClassOf Capability`

# CargoBased SubClassOf Capability
subclass: `CargoBased SubClassOf Capability`

# UpperThreshold SubClassOf Threshold
subclass: `UpperThreshold SubClassOf Threshold`

# LowerThreshold SubClassOf Threshold
subclass: `LowerThreshold SubClassOf Threshold`

# NominalThreshold SubClassOf Threshold
subclass: `NominalThreshold SubClassOf Threshold`

