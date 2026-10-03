# Kristal v8 core specification

Version: `8.0.0`

## 1. Scope

Kristal v8 extends the Kristal/Kristall architecture with two optional capabilities:

- **Language Layer** — external lexical Kristals and deterministic lexical resolution;
- **AI Query Layer** — rebuildable read indexes, typed exact query, federation, semantic slices and bounded AI context compilation.

v8 also standardizes integrity and trust rules required by those capabilities. No v8 capability may redefine semantic identity, epistemic state, provenance, source authority or portable v6 fields.

## 2. Stable substrate

A conforming v8 implementation MUST preserve:

```text
v6  portable Kristal state
v7  Kristall semantic identity / orchestration
v8  optional Language + AI Query capabilities
```

Valid v6 and v7 artifacts MUST remain valid without modification. v8 processors MAY construct adapters and derived read models around them, but MUST NOT rewrite canonical input merely to enable v8 functionality.

## 3. Read/write separation

Canonical Kristal state and semantic registries are the authoritative write/source model. Query indexes, lexical projections, caches, search indexes and AI context bundles are read models.

```text
READ MODEL != CANONICAL STATE
```

A read model MUST be rebuildable or traceable to declared source state. Lag, truncation or cache state MUST NOT be interpreted as a semantic assertion.

## 4. Language Layer

Human words are not semantic identity. A lexical Kristal associates stable semantic references with language-specific forms. Lexical artifacts remain external companions and MUST NOT become the source of semantic truth.

A deployment MAY compose language layers such as:

```text
fr-core
+ fr-science
+ fr-chemistry
+ fr-college
+ fr-CA
+ project-specific lexical delta
```

Locale identifiers use BCP 47 syntax. Domain, educational and geographic scope SHOULD use semantic references where stable identities are available.

Resolution MUST be deterministic. Missing lexicalization MUST remain explicitly unresolved; a processor MUST NOT invent a canonical term to satisfy a requested language.

## 5. AI Query Layer

AI-oriented query is derived from canonical semantic material. Query indexes MUST be rebuildable and non-authoritative. Approximate discovery MAY locate candidate semantic identities, but factual traversal MUST operate on resolved identities and canonical relations/assertions.

KQP separates:

```text
discovery → identity resolution → exact semantic query → bounded projection
```

Similarity, ranking and model confidence are discovery signals, not assertions.

## 6. Typed query and federation

KQP requests declare roots, traversal direction, property constraints, filters, evidence policy, pagination and deterministic budgets. Query results declare normalized execution plans, source fingerprints, completeness, continuation state, unresolved items, conflicts and omissions.

Federated queries MUST preserve shard/source provenance. A missing or timed-out shard yields a partial result, not a negative factual conclusion.

## 7. AI context compilation

An AI context bundle is a bounded read projection. The compiler SHOULD select semantically closed atoms, not unrelated buckets of data. A useful atom can contain an assertion or edge plus the minimum identities, provenance and evidence references required to interpret it.

A bundle MUST disclose:

- roots and query intent;
- source fingerprints;
- selection policy;
- completeness and truncation state;
- unresolved/conflicting material;
- omissions caused by budget or policy;
- provenance/trust class for retrieved context;
- lexical resolution metadata when language rendering is requested.

Budget-driven omission MUST NOT be represented as negation or absence in the underlying Kristal.

## 8. Integrity

v8 distinguishes byte identity from semantic fingerprinting. Existing v6/v7 content hashes remain unchanged. A v8 semantic fingerprint is an optional, versioned derived digest over a declared semantic projection. It MUST NOT replace inherited byte/content identity.

## 9. AI trust boundary

A model is an untrusted planner. Model output MAY propose queries, projections or mutations, but deterministic schema validation, semantic validation, authorization and admission remain outside the model. Retrieved content is data with provenance; it cannot grant itself authority by containing instructions.

## 10. Compatibility

The normative v8 compatibility contract is [Compatibility Contract](compatibility-contract.md).
