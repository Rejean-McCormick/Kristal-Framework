# Kristal State

`kristal_state` is the primary canonical structured artifact in Kristal v6.

It is a container for atomic assertions plus the context required to interpret them safely.

## Typical state-level concerns

A state normally carries:

- `schema_version`;
- `artifact_type: kristal_state`;
- deterministic identity/content hash;
- artifact lifecycle status;
- state-level applicability/context;
- source references;
- assertions;
- provenance;
- validation/recognition references;
- reader-policy references where applicable;
- lineage / build metadata / warnings where applicable.

## Assertion-level concerns

An assertion may carry:

- statement: subject → predicate → object;
- `assertion_status`;
- `valuations[]`;
- `coordinates`;
- `applicability`;
- `record_role`;
- `actionability`;
- evidence/provenance references;
- validation/recognition references;
- conflict/succession/lineage relationships.

## Atomicity

The point of atomic assertions is not minimal JSON size. It is independent addressability.

If two claims have different evidence, applicability, valuation or authority, they should be independently representable even when they appear together in prose.

## Rich payloads

An assertion object can still carry domain-specific structured payloads. Kristal does not forbid rich JSON; it wraps it in a stable envelope so the payload can be identified, contextualized, sourced, validated and superseded.

## State is not a mutable application database

A Kristal State may record a snapshot of operational state, but source applications retain ownership of their mutable records. New observations or decisions produce new traceable state rather than silently rewriting history.
