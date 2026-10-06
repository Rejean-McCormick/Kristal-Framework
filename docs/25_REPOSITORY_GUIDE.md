# Repository guide for v9 work

## 1. Principle

The existing repository boundaries should remain intact. V9 should extend them rather than create a parallel tree with different ownership rules.

Current major responsibilities remain:

```text
spec/       normative prose
schemas/    canonical active JSON Schemas
tck/        normative conformance vectors
examples/   non-normative examples
reference/  reference implementation(s)
tools/      repository/release/helper tooling
contracts/  contract manifests and compatibility locks
history/    release/status history
compat/     legacy compatibility material
```

This `/docs` directory is design and implementation documentation. Normative v9 text should move into `spec/v9/` as it stabilizes.

## 2. Proposed v9 repository additions

A mature v9 repository may contain:

```text
spec/v9/
  00-overview/
  01-core-spec/
  Logical-Artifacts.md
  State-Snapshots.md
  Identity-and-Commitments.md
  Derivations.md
  Materialization.md
  Exchange-and-Runtime.md
  Build-Publish-Activate.md
  Compatibility.md
  Security.md
  Conformance.md
  Glossary.md

schemas/v9/
  state.schema.json
  artifact-descriptor.schema.json
  derivation.schema.json
  materialization.schema.json
  exchange.schema.json

examples/v9/
  inline-state.example.json
  segmented-state.example.json
  federation.example.json
  derivation.example.json

reference/js/src/v9/
  state.mjs
  commitment.mjs
  derivation.mjs
  materialization.mjs
  publisher.mjs

tck/v9/vectors/
  commitments/
  identity/
  materialization/
  lifecycle/
  compatibility/
```

Exact filenames can change, but ownership should remain clear.

## 3. Do not put normative rules in tooling only

If a behavior affects interoperability, identity, logical equality or security, it must be described in the specification and covered by TCK vectors.

Reference code cannot be the only definition of a commitment boundary.

## 4. Do not duplicate schemas

KristalDiag may mirror active schemas for independent qualification, but the Framework remains the normative source.

Mirror verification should continue to ensure exact byte equality or pinned contract digest equality.

## 5. Compatibility locks

The v9 release contract should extend the existing compatibility-lock pattern to pin inherited v6/v7/v8 machine surfaces.

V9 schemas themselves should also enter the release/contract manifest once stable.

## 6. Reference implementation boundary

Reference code should demonstrate:

- commitment calculation;
- state composition;
- materialization reconstruction;
- deterministic derivation handling;
- local publish/activation;
- inherited v6/v7/v8 compatibility.

It should not become the hidden normative definition of domain-native logical contracts.

## 7. Example repository workflow

```text
edit spec/docs
    ↓
update schema if contract changed
    ↓
add/modify TCK vectors
    ↓
update reference implementation
    ↓
run Framework validation
    ↓
run KristalDiag qualification
    ↓
build reproducible release
```

A contract change without updated vectors should be treated as incomplete work.
