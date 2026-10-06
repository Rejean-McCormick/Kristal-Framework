# Conformance

Conformance is capability-based. An implementation MUST NOT claim a profile it does not fully implement.

## V9-State-Reader

A `V9-State-Reader` MUST:

- validate `kristal_logical_artifact` and `kristal_state_snapshot` machine contracts;
- reproduce the normative artifact and state logical-commitment vectors;
- reject a declared commitment that does not match normalized logical content;
- preserve the distinction between semantic identifiers and logical commitments;
- preserve pinned external references without treating them as owned content.

## V9-Builder

A `V9-Builder` includes `V9-State-Reader` and MUST additionally:

- validate `kristal_derivation` records;
- declare exact logical inputs, transform identity/version, parameters and outputs;
- avoid claiming deterministic output when undeclared mutable inputs can affect results;
- emit artifacts whose declared logical commitments verify.

## V9-Materializer

A `V9-Materializer` includes `V9-State-Reader` and MUST additionally:

- validate `kristal_materialization_manifest`;
- bind every materialization to an exact source logical commitment;
- preserve reconstructability according to the declared profile;
- demonstrate that repack/resegmentation does not change the source logical commitment when logical content is unchanged;
- treat dictionaries, indexes, compression and physical segment identifiers as non-semantic unless a domain contract explicitly says otherwise.

## V9-Publisher

A `V9-Publisher` includes `V9-State-Reader` and MUST additionally:

- publish immutable snapshots;
- never mutate an already-published snapshot in place;
- keep BUILD, PUBLISH and ACTIVATE distinct;
- provide atomic activation semantics within the transport/profile it claims;
- leave the previous active state intact when publication fails before activation;
- support rollback by selecting a retained prior snapshot rather than rewriting history.

Distributed consensus is not required by the baseline profile; a local filesystem publisher may conform when its activation update is atomic for that filesystem.

## V9-Full

`V9-Full` requires all four profiles above and MUST retain inherited v6/v7/v8 compatibility. It MUST pass:

- v6 portable-state vectors;
- v7 frozen semantic/Kristall vectors;
- v8 language/query vectors;
- v9 schemas and golden commitments;
- v9 polymorphic workload vectors.

## Polymorphism gate

The reference TCK includes multiple domain shapes. A core change MUST NOT require every workload to become a table, assertion list, graph, DAG or document. The baseline workload set includes a factorized relation, procedure DAG, multiplex graph, formal AST, epistemic corpus and federated state composition.

## Authority

Schema or TCK conformance demonstrates contract behavior only. It does not itself confer epistemic authority, operational authorization, recognition or factual truth.
