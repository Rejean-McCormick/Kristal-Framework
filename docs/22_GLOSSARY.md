# Glossary

## Activation

Selection of a published immutable snapshot for an operational channel such as `production` or `current`.

## Artifact Descriptor

A v9 record that identifies a logical artifact contract/commitment and, where applicable, links to representations or metadata needed to locate them.

## Blob

A sequence of stored bytes. A blob is identified physically by a blob digest.

## Blob Digest

Digest over exact physical bytes.

## Build

Computation that produces candidate logical artifacts and/or materializations. A successful build does not imply publication or activation.

## Build Provenance

Information describing how an artifact was computationally produced: inputs, transform, parameters, toolchain and related build evidence.

## Canon

The authoritative logical content within a declared authority boundary. A runtime/index is not canon merely because it is convenient.

## Commitment Profile

Versioned rules defining normalization, field inclusion/exclusion, ordering, domain separation and digest generation for a Logical Commitment.

## Coverage

Metadata declaring which part of a logical state or capability a local/portable materialization contains.

## Derivation

Machine-readable relationship describing how declared inputs and a transformation produce outputs.

## Derived Artifact

An artifact that can be rebuilt from declared source artifacts/inputs and is not the authoritative source for the underlying knowledge.

## Epistemic Overlay

Epistemic metadata or assertions attached to domain-native identities without requiring the native payload to be flattened into a universal shape.

## Epistemic Provenance

Evidence/source/authority lineage relevant to why and how knowledge should be interpreted or trusted.

## Exchange

Portable/verifiable packaging of a state, descriptors, manifests and physical blobs for distribution.

## Factorization

Non-destructive sharing of repeated structure or metadata while preserving reconstructability, provenance, exceptions and disagreement.

## HEAD

A mutable pointer selecting an immutable snapshot. `HEAD` is operational state, not the snapshot itself.

## Identity Migration

Explicit change in the rules defining semantic identity, including split/merge/remapping of previous semantic identities.

## Logical Artifact

A typed, independently identifiable unit of logical knowledge whose internal structure is defined by a Logical Contract.

## Logical Commitment

Digest/commitment over normalized logical content under a named profile. It is independent from physical packing when the logical content is unchanged.

## Logical Contract

Versioned domain contract defining the structure, semantics, normalization and validation rules of a Logical Artifact.

## Materialization

Physical representation of logical content under an explicit materialization profile.

## Materialization Manifest

Record mapping a logical artifact commitment to the physical blobs/segments required by a materialization profile.

## Materialization Profile

Versioned rules defining how logical content is encoded, segmented, factorized and reconstructed physically.

## Owned Member

Artifact that participates directly in the publishing state/authority's logical composition.

## Pinned Reference

Reference to a precise immutable external artifact/state revision or logical commitment.

## Projection

Explicit transformation from one logical contract/view into another, potentially with declared information loss or scope reduction.

## Publish

Creation/admission of an immutable State Snapshot according to release policy.

## Repack

Change of physical representation, segment boundaries, compression or related storage form that preserves logical content.

## Runtime Pack

Derived physical package optimized for lookup/query/execution. It must identify its source logical state and must not silently become canonical authority.

## Segment

Immutable physical unit within a materialization. Segment boundaries are not semantic boundaries by default.

## Semantic ID

Stable logical identity answering which object/concept/assertion/artifact is being referenced.

## Shard

Semantic, governance or lifecycle partition that may be independently curated/versioned. A shard is not a physical segment.

## State Snapshot

Immutable logical composition of owned logical artifacts and pinned external references.

## V6 Portable Projection

A `kristal_state/6.0` representation/projection used for portable interoperability. In v9 a domain-native canon does not have to be replaced by that projection.
