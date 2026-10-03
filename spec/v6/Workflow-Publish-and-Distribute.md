# Workflow: Publish & Distribute

Publishing a Kristal v6 artifact means making a content-addressed state or projection available to consumers with enough metadata to verify and interpret it.

## Publish the canonical source

Prefer publishing the `kristal_state` identity/hash plus any validation/recognition/reader-policy references required by the consumer contract.

## Derived materializations

If distributing an index, runtime/query store or consumer projection, include:

- source state identifier/hash;
- transform/profile/version;
- relevant reader/applicability policy;
- integrity metadata;
- enough labels to preserve valuation/role/actionability meaning.

## Do not flatten

Distribution should not turn:

- unknown into false;
- `not_applicable` into low;
- a vector into an unexplained single score;
- validation into authority;
- `automatic` into execution permission.

## Reference use

If an artifact is recommended for reference use, that recommendation should be backed by explicit artifact status and/or authority recognition for a declared applicability envelope.
