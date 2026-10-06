# FAQ

## Does v9 replace `kristal_state/6.0`?

No. V6 remains a valid portable epistemic contract. V9 can reference unchanged v6 states and can produce v6 projections where needed.

## Is a v9 State Snapshot just another big JSON state?

No. The snapshot is a logical composition descriptor. Its artifacts may be inline, segmented, domain-native, remote or referenced through pinned child states.

## Are assertions obsolete?

No. Atomic assertions remain essential when claim-level identity, provenance, valuation or conflict must be independently represented. V9 only rejects the assumption that every domain-native structure must use assertion objects as its canonical physical shape.

## Why not just use gzip/Zstandard on the large JSON?

Compression solves transport/storage bytes surprisingly well, but it does not solve monolithic parsing, partial reads, localized updates, rebuild amplification, partial verification or representation-independent identity.

## Why not standardize Parquet?

Parquet is excellent for some homogeneous relation workloads and poor as a universal semantic shape. V9 keeps the core independent so a Parquet profile can exist without making every Kristal tabular.

## Does factorization lose metadata?

It must not. Shared/defaulted metadata remains logically present. A conforming materialization must reconstruct the effective logical values.

## Can two different files have the same logical commitment?

Yes, when their declared materialization profiles reconstruct the same logical artifact under the same logical commitment profile.

## Can the same semantic object have multiple logical commitments over time?

Yes. Stable semantic identity and revision content are different concepts.

## Is the logical commitment always public?

Not necessarily. Sensitive deployments may need restricted or protected commitment profiles. V9 should not assume public deterministic digests for all knowledge.

## Is a shard the same as a segment?

No. A shard is semantic/governance/lifecycle partitioning. A segment is physical storage partitioning.

## Does a parent state own referenced child states?

No. References do not transfer ownership or authority.

## Can an index become canon?

Only if the domain deliberately changes its authority model and contract. A rebuildable convenience index is derived and should remain so.

## Does v9 require a content-addressed store?

No. Filesystems, object stores, databases or content-addressed stores may implement physical storage. Blob digests and descriptors provide portable integrity without forcing a storage backend.

## Does v9 require distributed consensus?

No. The core requires immutable snapshots and safe publication semantics. A deployment may implement activation with a local atomic rename, database transaction, compare-and-swap API or stronger distributed mechanism.

## What changes first in the Framework?

The recommended order is:

1. commitment semantics and vectors;
2. state/artifact contracts;
3. derivation contract;
4. materialization contract;
5. lifecycle/publish semantics;
6. reference implementation;
7. optimized profiles.

## What is the key success criterion?

A physical optimization must be replaceable without silently changing the knowledge it represents.
