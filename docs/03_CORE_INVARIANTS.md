# Core invariants

V9 inherits the v6, v7 and v8 invariants. The distinctions below are additional architectural safety boundaries.

## Logical state and materialization

```text
LOGICAL STATE != PHYSICAL MATERIALIZATION
LOGICAL ARTIFACT != BLOB
LOGICAL COMMITMENT != BLOB DIGEST
REPRESENTATION != IDENTITY
REPACK != LOGICAL REVISION
RECOMPRESSION != LOGICAL REVISION
RESEGMENTATION != LOGICAL REVISION
INDEX REBUILD != LOGICAL REVISION
ENCRYPTION CHANGE != LOGICAL REVISION
```

## Polymorphism

```text
KNOWLEDGE != ASSERTION LIST
DOMAIN-NATIVE SHAPE != PORTABLE PROJECTION
LOGICAL GRAPH != PHYSICAL MERKLE DAG
ORDERED COLLECTION != SET
NATIVE MODEL != RUNTIME INDEX
```

## Authority and trust

```text
STATE COMPOSITION != AUTHORITY MERGE
REFERENCE != OWNERSHIP TRANSFER
INTEGRITY != AUTHENTICITY
AUTHENTICITY != AUTHORITY
AUTHORITY != FACTUAL CORRECTNESS
EPISTEMIC PROVENANCE != BUILD PROVENANCE
BUILD != VALIDATION
VALIDATION != RECOGNITION
```

## Lifecycle

```text
BUILD != PUBLISH
PUBLISH != ACTIVATE
STATE SNAPSHOT != HEAD
ROLLBACK != HISTORY REWRITE
SOURCE BYTE CHANGE != LOGICAL CHANGE
```

## Federation and storage

```text
SHARD != SEGMENT
PARTITION STRATEGY != SEMANTIC MODEL
REMOTE ABSENCE != LOGICAL ABSENCE
PARTIAL AVAILABILITY != NEGATION
CACHE != AUTHORITY
INDEX != SOURCE OF TRUTH
```

## Compatibility

```text
V9 EXTENSION != V6/V7/V8 MUTATION
NEW MATERIALIZATION != NEW SEMANTICS
DOWNGRADE LOSS != SEMANTIC REWRITE
IDENTITY MIGRATION != SCHEMA RENAME
```

## Practical interpretation

These are not slogans. They determine implementation behavior.

For example, if a developer can make an index rebuild alter the state-level logical commitment, the design has mixed the read model with canonical state.

If changing compression alters semantic identity, physical identity has leaked into logical identity.

If importing a referenced child state transfers its authority to the parent, federation has become authority collapse.

If a query reports `false` merely because the required shard was not downloaded, partial availability has become epistemic error.
