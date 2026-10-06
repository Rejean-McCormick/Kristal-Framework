# Logical artifacts

## 1. Purpose

The **Logical Artifact** is the primary polymorphic boundary in v9.

It exists so that Kristal can apply common identity, lifecycle, integrity and derivation rules without forcing every domain to use the same internal data structure.

## 2. Minimum conceptual descriptor

A logical artifact should be describable with information equivalent to:

```json
{
  "artifact_id": "urn:recipe:variant:carbonara:42",
  "logical_contract": {
    "id": "recipes.procedure-graph",
    "version": "3.0"
  },
  "logical_commitment": {
    "profile": "kristal.logical/jcs-sha256-v1",
    "digest": "sha256:..."
  },
  "scope": {
    "domain": "culinary"
  },
  "authority_ref": "authority:recipes",
  "dependencies": []
}
```

The baseline draft field names are now defined by `schemas/v9/kristal-logical-artifact.schema.json`; domain payload shape remains polymorphic.

## 3. Logical contract

The `logical_contract` defines how the artifact must be interpreted.

It is responsible for domain-specific rules such as:

- schema and validation;
- semantics of collections;
- ordered versus set-like structures;
- internal stable identities;
- logical normalization;
- commitment profiles;
- dependency rules;
- projection contracts.

The Kristal core must not duplicate those rules generically.

## 4. Native shapes

Examples of valid logical artifact shapes include:

### Relational

A massive relation such as Pokémon learnsets can remain conceptually a relation while individual claims retain logical identity.

### Procedural DAG

A recipe procedure can retain operation nodes, intermediate states, inputs, outputs, end conditions and partial ordering.

### Multiplex graph

Vehicle diagnostics can retain components, ports, typed transfers, operating-state conditions, functional paths and failure models.

### Formal AST

Mathematical expressions can retain binding, order and typed operator structure that would be unsafe to flatten naively.

### Federation node

An educational or organizational artifact can consist mainly of pinned child-state references and ordered topology.

### Document/research corpus

A small layered epistemic corpus can remain a compact structured document rather than being segmented for its own sake.

## 5. Logical artifact versus assertion

V6 assertions remain important and fully supported. V9 simply does not require every domain-native object to be expressed as a v6 assertion as its canonical business form.

Assertions remain appropriate when independent claim addressability is the natural logical unit.

A domain-native artifact may also expose an epistemic overlay or v6 projection when cross-domain interoperability requires it.

## 6. Capability discovery

A logical artifact may advertise optional capabilities such as:

```text
projectable-to-v6
addressable-members
partial-fetch
queryable
streamable
encrypted
```

Capabilities must not be inferred from filenames or media types alone when correctness depends on them.

## 7. Small-artifact rule

A small logical artifact may be represented inline.

V9 must not impose manifests, dictionaries, partition trees or remote stores when a single readable file is the most appropriate representation.

```text
SMALL KRISTAL MUST STAY SMALL
```
