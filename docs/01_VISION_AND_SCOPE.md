# Vision and scope

## 1. Vision

Kristal v9 makes the knowledge model independent from the storage strategy used to carry it.

Earlier Kristal generations already established strong boundaries:

- v6 made epistemic assertions independently addressable and portable;
- v7 separated stable semantic identity from content identity and introduced factorization;
- v8 separated canonical state from language, query indexes and AI-facing read models.

At large scale, one remaining coupling becomes costly: a logical assertion or native domain object is still too often represented by a directly corresponding physical JSON object. That coupling is convenient for small states but causes unnecessary repetition, monolithic rebuilds and expensive partial access for large ones.

V9 removes that coupling without weakening addressability, provenance or determinism.

## 2. Scope

V9 standardizes the architecture around five questions:

1. **What logical knowledge exists?**
2. **What stable identity does it have?**
3. **How was a revision produced?**
4. **How is the logical content materialized physically?**
5. **Which immutable snapshot is published or active?**

V9 does not attempt to define a universal ontology or universal database model.

## 3. Polymorphism requirement

A conforming architecture must support knowledge whose native form is naturally:

```text
relation
property graph
DAG
cyclic graph
AST
hierarchy
federation
event log
matrix
document corpus
proof structure
state machine
opaque domain object
```

The list is open.

The Standard must not require a domain to flatten such structures into triples, rows or assertion objects merely to participate in v9.

## 4. Epistemic continuity

Representation independence must not weaken Kristal's epistemic model.

If two claims differ in evidence, applicability, valuation or authority, they must remain independently representable even when a compact materialization stores shared metadata once.

```text
PHYSICAL FACTORIZATION != EPISTEMIC COLLAPSE
```

## 5. Operational continuity

V9 must continue the existing principles of deterministic builds, immutable released artifacts, traceable rollback, explicit authority and derived runtime packs.

The architecture should make those principles easier to implement at scale rather than create a parallel operational model.

## 6. Non-goals

V9 is not:

- a graph database specification;
- a replacement for JSON Schema;
- a new query language;
- a distributed consensus protocol;
- an object-store protocol;
- an RDF profile;
- a Parquet profile;
- a cryptographic key-management system;
- a mandate that every artifact be content-addressed publicly.

Those capabilities may be attached through profiles or implementations when appropriate.

## 7. Design success

V9 succeeds when all of the following can be true simultaneously:

- Pokémon exposes hundreds of thousands of independently meaningful claims without requiring a giant expanded JSON state internally;
- a recipe remains a procedural DAG rather than a simulated table;
- an automotive diagnostic model keeps its conditional multiplex graph;
- a math system keeps formula ASTs and proof/theory/representation graphs separate;
- a hospital system composes artifacts without merging confidentiality or authority domains;
- a university hierarchy references child Kristals without copying them;
- a 50 KiB Kristal remains a small, readable artifact with no large-scale machinery.
