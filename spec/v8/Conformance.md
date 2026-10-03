# v8 conformance

v8 defines additive profiles. A deployment claims only the profiles it actually implements.

## V8-Reader

MUST read valid v6, v7 and v8 companion artifacts without redefining v6/v7 semantics. MUST preserve unresolved identities and compatibility boundaries.

## V8-Language

MUST validate lexical Kristals/stacks, interpret BCP 47 locale tags, perform deterministic precedence, expose missing/conflicting lexicalization and never fabricate a lexical value as canonical output.

## V8-Query

MUST distinguish read models/results from canonical state, support exact identity-based query for declared modes, validate typed traversal, expose normalized execution plan, preserve unresolved/conflict states and report `complete|partial|error` plus continuation/truncation metadata.

## V8-Federation

MUST preserve shard/source provenance, enforce parent budgets across subqueries and expose unavailable/unknown shard outcomes. Pagination/continuation MUST bind to a stable normalized query and compatible source state.

## V8-AI-Context

MUST emit bounded context bundles with source fingerprints, provenance/trust metadata, completeness, omissions, unresolved items and declared byte/token budget semantics. If token limits are used, the tokenizer/profile MUST be declared or the value marked heuristic.

## V8-Integrity

MUST preserve inherited byte/content identity. If semantic fingerprints are supported, the implementation MUST declare a versioned fingerprint profile and domain separation and MUST NOT present the semantic fingerprint as inherited byte identity.

## V8-Full

MUST satisfy V8-Reader, V8-Language, V8-Query, V8-Federation, V8-AI-Context and V8-Integrity.

Conformance to a v8 profile does not remove any v6/v7 conformance obligation claimed by the implementation.
