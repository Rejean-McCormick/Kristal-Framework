# FAQ

## Is Kristall one giant JSON document?
No. `kristall_manifest` is a root descriptor. Registries and Mesh data can be sharded.

## Does v7 invalidate v6?
No. v6 `kristal_state` remains the portable contract.

## Why not put `schema_version: 7.0` on generated Kristals?
Because the design goal is additive compatibility. v7-specific lineage lives in `extensions.kristal_v7` while the portable state remains valid v6.

## Is a Surface stored?
Usually no. It is a query-time view. Persist it only when a portable Projection is useful.

## Are two similar assertions automatically merged?
No. They become candidates for an assertion family. Scope, evidence, applicability and conflict must be preserved.

## Can an AI discover axes automatically?
It can propose them. Activation follows a declared promotion policy.

## Why only two axes per projection?
The internal Kristall may be highly multidimensional. The two-axis limit is a human-facing orientation contract that keeps portable Kristals coherent and interpretable.
