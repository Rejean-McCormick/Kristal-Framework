# Profile: Validation Reporting (SHACL)

## Status

Draft (Kristal v5 optional standardized profile)

## Purpose

Provide an interoperable **SHACL-based conformance report** for Kristal artifacts that:

* is **machine-consumable**,
* maps cleanly to Kristal **Validation Report** issue codes and severity levels,
* can be used in CI/CD as an optional validation output,
* can support review, validation decisions, authority recognition, and reader policy evaluation without becoming a default global gate.

This profile is **optional** and does not change core Kristal identity, content addressing, hashing, or artifact status by itself.

## Profile identifier

* `profile_id`: `validation-shacl`
* `profile_version`: `1.0`
* `spec_version`: `5.0`

## Scope

This profile defines:

* required outputs: SHACL shapes graph and SHACL validation report graph;
* minimum mapping rules from SHACL results to Kristal Validation Report issues;
* deterministic reporting requirements;
* linkage requirements between SHACL reports, Kristal artifacts, build records, validation decisions, and authority recognition records where applicable;
* extension predicates that improve interoperability between SHACL outputs and Kristal issue locations.

Non-scope:

* choosing a specific SHACL engine implementation;
* mandating RDF export integrity hashing, which is handled by the RDF integrity / RDFC profile;
* embedding workflow, review, approval, or authority-recognition processes directly into Exchange or Runtime Pack schemas;
* making SHACL validation a default compilation, publication, recognition, or activation gate.

## Inputs

A SHACL validation profile implementation may consume one or more of:

* a Kristal `working_exchange`;
* a Kristal `reference_exchange`;
* an Exchange shard;
* a Runtime Pack manifest;
* a Structured Epistemic State;
* a derived RDF projection suitable for SHACL checking;
* an existing Kristal Validation Report;
* a validation decision target;
* an authority recognition target.

If Claim-IR or Resolved Claim-IR artifacts are used, they are treated as extractor or resolution profile inputs, not as universal Kristal v5 input requirements.

## Outputs

When enabled, an implementation MUST produce:

1. a SHACL shapes graph, or a stable reference to it;
2. a SHACL validation report graph;
3. a Kristal Validation Report entry or report section linking the SHACL execution to the checked artifact;
4. deterministic metadata sufficient to reproduce the SHACL profile execution.

Recommended serializations:

* Turtle for shapes;
* Turtle, N-Quads, or TriG for reports.

When byte-stable output is required, the implementation MUST declare the serialization profile and deterministic ordering rules used.

## Normative requirements

### R1. Shapes availability (MUST)

Implementations MUST provide one of:

* `shapes_uri`: a stable URI to the SHACL shapes graph; or
* `shapes_inline`: an embedded shapes graph for offline packaging.

The shapes MUST be versioned, and the version MUST be recorded.

The shapes version SHOULD be referenced from the Kristal Validation Report and MAY also be referenced from a validation decision, authority recognition record, or profile execution record.

### R2. Deterministic execution (MUST)

Given identical inputs, the same shapes version, the same profile configuration, and the same data projection:

* the set of reported SHACL results MUST be identical;
* result normalization MUST be deterministic;
* serialization ordering MUST be deterministic when byte-stable reports are required.

SHACL engines may differ in native result ordering. Kristal determinism applies to the normalized result set and to the declared deterministic serialization rules, not to unspecified engine-internal ordering.

### R3. Required linkage to Kristal artifacts (MUST)

The SHACL report MUST be linkable to the Kristal artifact or projection being checked via one or more of:

* `kristal:kristalId`;
* `kristal:artifactId`;
* `kristal:shardId`;
* `kristal:stateId`;
* `kristal:runtimePackId`;
* `kristal:buildId`;
* `kristal:contentHash`.

The related Kristal Validation Report MUST declare `profile_id = validation-shacl` in its enabled profiles list, profile execution list, or equivalent profile metadata section.

### R4. Mapping rules (MUST)

Each SHACL validation result MUST map to a Kristal Validation Report issue.

Severity mapping:

* `sh:Violation` maps to `severity = ERROR`;
* `sh:Warning` maps to `severity = WARNING`;
* `sh:Info` maps to `severity = INFO`.

Each mapped issue MUST include:

* `code`: a stable Kristal issue code;
* `severity`: the mapped Kristal severity;
* `message`: a human-readable explanation;
* `location`: a JSON pointer, RDF focus node IRI, artifact reference, assertion reference, or other stable target locator;
* `source_profile`: `validation-shacl`;
* `source_shape` or `source_constraint_component` when available.

### R5. Minimum SHACL result fields (MUST)

Each SHACL result node SHOULD include, and implementations MUST be able to produce, at minimum:

* `sh:focusNode`;
* `sh:resultSeverity`;
* `sh:sourceShape` or `sh:sourceConstraintComponent`;
* `sh:resultMessage`.

If an engine does not provide one of these fields natively, the implementation MUST either derive it during normalization or record a profile execution issue explaining the missing field.

### R6. No default effect on compilation, recognition, or activation (MUST)

Enabling SHACL output MUST NOT change core compilation behavior by itself.

A SHACL profile result MAY inform:

* a validation decision;
* a review process;
* an authority recognition decision;
* a reader policy;
* CI/CD reporting;
* publication checks;
* Runtime Pack activation policy.

However, this effect MUST be explicitly configured. The default behavior is reporting only.

SHACL conformance MUST NOT be treated as universal truth, universal validation, or authority recognition. It only reports conformance to the selected shapes graph under the declared profile configuration.

### R7. Scoped validation semantics (MUST)

A SHACL report MUST NOT imply that an artifact or assertion is globally valid.

If SHACL results are used to support validation, the resulting Kristal validation decision MUST remain scoped by:

* authority channel;
* validation policy;
* domain or subdomain;
* target level;
* certainty level where applicable;
* `validated_as` where applicable.

A SHACL-conformant artifact may still contain uncertain, disputed, fictional, mythological, speculative, or low-certainty assertions. SHACL conformance only means that the checked graph satisfies the declared shapes.

### R8. Target level declaration (MUST)

A SHACL profile execution MUST declare the target level being checked.

Allowed target levels:

* `artifact`;
* `shard`;
* `assertion`;
* `structured_epistemic_state`;
* `exchange`;
* `runtime_pack`;
* `rdf_projection`;
* `authority_registry`;
* `validation_report`;
* `reader_policy`.

The target level MUST be reflected in the Kristal Validation Report issue locations or profile execution metadata.

### R9. Projection declaration (MUST)

If SHACL is applied to a derived RDF projection rather than the native Kristal artifact, the report MUST declare:

* projection profile;
* projection version;
* source artifact ID;
* source content hash;
* projection content hash when available;
* projection generation configuration.

A SHACL report over a projection MUST NOT be silently presented as a direct report over the native artifact unless the projection profile explicitly guarantees equivalence for the checked constraints.

## Recommended conventions

### C1. Shape naming and versioning (SHOULD)

Shapes SHOULD use stable IRIs containing:

* `spec_version`;
* artifact type or target level;
* `shape_version`.

Example:

```text
urn:kristal:shapes:v5:exchange:1.0
```

Additional examples:

```text
urn:kristal:shapes:v5:structured-epistemic-state:1.0
urn:kristal:shapes:v5:runtime-pack:1.0
urn:kristal:shapes:v5:authority-registry:1.0
urn:kristal:shapes:v5:reader-policy:1.0
```

### C2. Code system (SHOULD)

Define a code namespace for SHACL-mapped issues:

```text
KRS_V5_<CATEGORY>_<NAME>
```

Examples:

```text
KRS_V5_SCHEMA_MISSING_REQUIRED_FIELD
KRS_V5_EVIDENCE_MISSING
KRS_V5_VALUE_NORMALIZATION_FAILED
KRS_V5_SCOPE_MISMATCH
KRS_V5_AUTHORITY_CHANNEL_MISSING
KRS_V5_CERTAINTY_LEVEL_INVALID
KRS_V5_VALIDATED_AS_MISSING
KRS_V5_READER_POLICY_UNSUPPORTED
KRS_V5_PROJECTION_MISMATCH
```

### C3. Include both JSON and RDF pointers where possible (SHOULD)

If the validator can derive a JSON pointer for the corresponding location in a Kristal artifact, include it in:

* Kristal Validation Report `location.json_pointer`;
* SHACL result message; or
* a Kristal extension triple.

If the validator can identify RDF locations, include:

* `sh:focusNode`;
* `sh:resultPath`;
* `kristal:rdfNode`;
* `kristal:rdfGraph`;
* `kristal:rdfTriple` where applicable.

### C4. Preserve authority and certainty labels (SHOULD)

When SHACL validation touches assertion-level data, mapped issues SHOULD preserve or reference:

* `assertion_id`;
* `assertion_status`;
* `certainty_level`;
* `validated_as`;
* `authority_channel`;
* `scope`.

This prevents SHACL reporting from flattening scoped validation into an unqualified pass/fail result.

### C5. Reader policy integration (SHOULD)

If a SHACL report is used by a reader, browser, AI agent, or Runtime Pack, the consuming system SHOULD expose whether the report affects:

* `reference_only` mode;
* `validated_only` mode;
* `high_certainty_only` mode;
* `research` mode;
* `creative` mode;
* `all_with_labels` mode;
* a custom reader policy.

SHACL results SHOULD NOT hide labels, uncertainty, disagreement, fictionality, mythology, or disputed status.

## Report structure requirements

### Shapes graph

The shapes graph:

* MUST contain SHACL shapes such as `sh:NodeShape` and/or `sh:PropertyShape`;
* MUST declare an explicit version identifier via `owl:versionInfo`, a Kristal predicate, or both;
* SHOULD declare the target artifact type or target level;
* SHOULD declare the Kristal spec version;
* SHOULD identify whether it applies to native Kristal JSON, RDF projection output, or both.

### Report graph

The report graph MUST follow SHACL Validation Report structure, including:

* `sh:conforms` boolean;
* `sh:result` entries for validation result nodes.

Each result node SHOULD include Kristal extension metadata when available.

## Required extension predicates

To improve interoperability between SHACL outputs and Kristal issue locations, implementations SHOULD emit the following predicates on each `sh:ValidationResult` when applicable:

* `kristal:issueCode`;
* `kristal:jsonPointer`;
* `kristal:artifactId`;
* `kristal:kristalId`;
* `kristal:shardId`;
* `kristal:stateId`;
* `kristal:runtimePackId`;
* `kristal:assertionId`;
* `kristal:evidenceId`;
* `kristal:authorityChannel`;
* `kristal:validationPolicy`;
* `kristal:certaintyLevel`;
* `kristal:validatedAs`;
* `kristal:scopeDomain`;
* `kristal:profileId`;
* `kristal:profileVersion`;
* `kristal:buildId`.

These extensions MUST NOT be required by generic SHACL tools, but they SHOULD be emitted by Kristal-aware implementations to make downstream automation reliable.

## Failure modes and required behaviors

### Shapes unavailable

If shapes are unavailable, the SHACL profile execution MUST fail and record an `ERROR` in the Kristal Validation Report.

Core compilation may still proceed unless the active deployment policy explicitly makes this SHACL profile a gate.

### Shapes invalid

If the shapes graph is invalid, the SHACL profile execution MUST fail and record an `ERROR` with:

* shape reference;
* shape version;
* validation engine;
* error message;
* profile configuration.

### Execution limits exceeded

If SHACL execution exceeds configured limits such as timeout, memory, graph size, or result count, the profile MUST fail and record an `ERROR` with explicit limit information.

### Projection unavailable

If SHACL requires an RDF projection and that projection cannot be produced, the profile MUST fail and record an `ERROR`.

If the profile is configured as report-only, this failure MUST NOT block compilation or artifact materialization.

### Mapping failure

If a SHACL result cannot be mapped to a Kristal Validation Report issue, the implementation MUST record an `ERROR` or `WARNING` describing the mapping failure.

The original SHACL result SHOULD be preserved or referenced for inspection.

### Partial execution

If partial execution is allowed by deployment policy, the report MUST declare:

* `execution_status = partial`;
* which shapes were executed;
* which shapes were skipped;
* why execution was incomplete;
* whether the partial result is allowed to inform validation, recognition, or reader policy.

## Conformance tests

A conforming implementation MUST provide fixtures demonstrating:

* stable shapes versioning;
* reproducible report production;
* correct severity mapping for `sh:Violation`, `sh:Warning`, and `sh:Info`;
* stable mapping to Kristal issue codes;
* linkability via `kristal_id`, artifact ID, or `build_id`;
* deterministic serialization rules for the chosen format or formats;
* projection declaration when SHACL is run against RDF derived from a native Kristal artifact;
* preservation of target level;
* preservation of scoped validation metadata when applicable;
* behavior when shapes are unavailable;
* behavior when shapes are invalid;
* behavior when execution limits are exceeded;
* behavior when a result cannot be mapped cleanly.

## Example profile execution metadata

```json
{
  "profile_id": "validation-shacl",
  "profile_version": "1.0",
  "spec_version": "5.0",
  "target_level": "exchange",
  "target_ref": {
    "id": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "artifact_type": "working_exchange"
  },
  "shapes_uri": "urn:kristal:shapes:v5:exchange:1.0",
  "shapes_version": "1.0",
  "projection_profile": "rdf-wdqs-export",
  "projection_version": "1.0",
  "execution_status": "completed",
  "engine": {
    "name": "example-shacl-engine",
    "version": "1.0.0"
  },
  "result_summary": {
    "conforms": false,
    "error_count": 1,
    "warning_count": 2,
    "info_count": 0
  }
}
```

## Example severity mapping

```text
sh:Violation -> ERROR
sh:Warning   -> WARNING
sh:Info      -> INFO
```

## Example Kristal issue mapping

```json
{
  "code": "KRS_V5_AUTHORITY_CHANNEL_MISSING",
  "severity": "ERROR",
  "message": "The assertion is marked as validated but does not declare an authority channel.",
  "location": {
    "json_pointer": "/assertions/12/authority_channel",
    "rdf_focus_node": "urn:kristal:assertion:12"
  },
  "source_profile": "validation-shacl",
  "source_shape": "urn:kristal:shapes:v5:exchange:authority-channel-required"
}
```

## Open questions

* Do we standardize a single shapes vocabulary per artifact type, or allow multiple named shape sets per target level?
* Do we require engines to output `sh:sourceConstraintComponent` consistently, or treat it as best effort?
* Should Kristal define a compact canonical SHACL report profile for byte-stable report hashing?
* Should reader policy evaluation have its own SHACL shape set, or remain outside this profile?
* Should authority recognition checks be expressed as SHACL constraints, or only referenced from validation policies?
