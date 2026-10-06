# Logical Artifacts

A `kristal_logical_artifact` is the polymorphic knowledge boundary of Kristal v9.

It carries:

- stable `artifact_id` semantic identity;
- `logical_contract {id, version}`;
- domain-native `payload`;
- `logical_commitment`;
- optional logical `scope`;
- optional pinned logical `dependencies`;
- optional domain-semantic `extensions`;
- optional authority/identity metadata outside content commitment.

## No universal payload shape

The v9 core does not define universal `nodes`, `edges`, `rows`, `events`, `claims` or `cells` members. Those belong to the named logical contract.

A graph remains a graph. A procedure DAG remains a DAG. An AST remains an AST. A relation may remain a relation. A small document may remain inline.

## Contract responsibility

The logical contract defines payload validity and any domain-specific normalization required before commitment. It MUST define whether every collection that can affect logical equality behaves as an ordered sequence, set, multiset, map, or another deterministic structure.

The generic v9 baseline does not guess those semantics from JSON syntax.

## Extensions

`extensions` are part of the baseline logical artifact commitment because domain extensions may carry actual knowledge. Physical hints, indexes, cache metadata and materialization settings therefore MUST NOT be stored in `extensions` if they are intended to be representation-only; they belong to materialization/runtime surfaces.
