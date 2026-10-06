# Migration from v8 to v9

Migration is additive. Existing v6/v7/v8 artifacts remain valid unchanged.

Recommended adoption:

1. wrap existing canonical artifacts with v9 Logical Artifact descriptors;
2. calculate v9 logical commitments;
3. compose immutable State Snapshots;
4. declare current build processes as Derivations;
5. move physical indexes/caches into Runtime or Materialization surfaces;
6. add alternative materializations only where they provide measurable value.

A v6 state can remain one opaque logical artifact when deeper decomposition provides no benefit.
