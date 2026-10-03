# Profile: RDF WDQS Export (Kristal v5)

## Status

Draft

## Purpose

Define a deterministic RDF export profile for Kristal v5 that is compatible with common Wikidata Query Service (WDQS) expectations and downstream RDF tooling, while keeping Kristal’s core identity, scoped validation, authority recognition, certainty metadata, and offline runtime constraints intact.

This profile specifies:

* what graphs are exported,
* how statements are represented, including qualifiers and references,
* rank and WDQS-style `truthy` projection behavior,
* how Kristal validation, certainty, and authority metadata MAY be exposed in RDF,
* required determinism rules,
* and conformance expectations.

This profile does not make exported RDF globally true by default. It exports structured assertions and their metadata in a deterministic RDF shape. Reader policy, authority recognition, validation scope, and certainty level remain explicit Kristal concerns.

## Scope

In scope:

* RDF dataset shape and serialization requirements
* item, property, statement, qualifier, reference, and value modeling
* rank and WDQS-style `truthy` projection rules
* deterministic output requirements
* optional RDF exposure of Kristal validation, certainty, authority, and reader-policy metadata

Out of scope:

* RDF dataset hashing / canonicalization, handled by the optional **RDF Integrity (RDFC)** profile
* live SPARQL service behavior
* full WDQS feature parity
* validation decisions themselves
* authority recognition decisions themselves
* reader-policy enforcement beyond export selection and manifest declaration

Kristal Runtime Packs remain offline-capable and constrained. This profile defines an export compatibility format, not a hosted WDQS clone.

## Terminology

* **Item**: Wikibase-style entity with a QID, such as `Q123`.
* **Property**: Wikibase-style property with a PID, such as `P123`.
* **Statement**: an assertion about an item using a property and a value, with optional qualifiers, references, rank, validation metadata, certainty metadata, and authority metadata.
* **Qualifier**: additional information attached to a statement.
* **Reference**: provenance or evidence attached to a statement.
* **Rank**: Wikibase-style rank value used for projection behavior: `preferred`, `normal`, or `deprecated`.
* **Truthy projection**: a WDQS-compatible technical projection selecting best-ranked statements for a given `(subject, property)`. In this profile, `truthy` is a compatibility term and does not mean universal truth.
* **Validation status**: Kristal status describing whether a statement or artifact is not evaluated, in review, validated, conditionally validated, disputed, rejected, or revoked.
* **Certainty level**: Kristal metadata describing how strong a statement is within its declared scope.
* **Authority channel**: a scoped authority that may recognize, validate, reject, or classify artifacts or assertions.
* **Reader policy**: a policy selecting which validation statuses, certainty levels, authority channels, and scopes are visible to a reader or consuming system.

Normative keywords: MUST, SHOULD, MAY.

## Inputs

The input to this profile is a Kristal v5 artifact or selected subset of artifacts.

Supported inputs:

* `working_exchange`
* `reference_exchange`
* exchange shards referenced by an `exchange_federation_manifest`
* selected assertions from a Structured Epistemic State, if the export pipeline supports direct state export

The export configuration MUST select:

```json
{
  "export_profile": "rdf-wdqs",
  "export_profile_version": "5.0",
  "projection": "full",
  "reader_policy_ref": null
}
```

Allowed projection values:

```text
full
truthy
```

Optional export configuration MAY include:

* language preferences for labels
* namespace mode
* statement node identity mode
* authority channels to include
* validation statuses to include
* certainty levels to include
* whether to include disputed statements
* whether to include fictional or mythological corpora
* whether to emit Kristal metadata graphs

Labels are optional in RDF export unless explicitly enabled.

## Outputs

The output is a deterministic RDF dataset serialized as N-Quads or Turtle.

Recommended primary serialization:

```text
export.rdf.nq
```

Required output artifacts:

```text
export.rdf.nq
export.manifest.json
```

Allowed alternative serialization:

```text
export.rdf.ttl
```

Turtle is allowed only when the exporter defines additional determinism constraints for prefix ordering, subject ordering, predicate ordering, object ordering, blank node handling, and serializer configuration.

The export manifest MUST record:

* profile id
* profile version
* projection
* source artifact refs
* reader policy refs, if any
* authority registry ref, if any
* namespace choices
* statement node identity scheme
* rank representation mode
* validation / certainty metadata export mode
* sorting and serialization parameters
* deterministic export normalization parameters

## Dataset Structure

### Required graphs

The export MUST be an RDF dataset with at least the following named graphs.

#### 1. Assertion graph

Required.

Contains:

* item-to-value triples
* item-to-statement-node triples
* statement node triples
* qualifiers
* rank representation
* statement-level metadata required by the selected export mode

#### 2. Reference graph

Required if references exist.

Contains:

* reference nodes
* reference details
* deterministic links from statement nodes to reference nodes

If references are present in the source data, a reference graph MUST be emitted.

#### 3. Metadata graph

Optional.

Contains:

* export metadata
* build id
* source artifact refs
* profile selection
* projection mode
* reader policy refs
* authority registry refs
* timestamps

The metadata graph MUST NOT affect the Kristal core content hash unless an integrity profile explicitly declares that it is part of the RDF hash target.

### Optional graphs

#### 4. Validation graph

Optional but RECOMMENDED when validation metadata exists.

Contains:

* validation status
* validated-as classification
* validation decision refs
* validation policy refs
* authority channel refs
* validation scope

#### 5. Certainty graph

Optional but RECOMMENDED when certainty metadata exists.

Contains:

* certainty level
* confidence summaries, if present
* scope-specific certainty metadata

#### 6. Authority graph

Optional but RECOMMENDED when authority recognition metadata exists.

Contains:

* authority channel refs
* authority recognition refs
* recognition status
* recognized-as classification
* authority scope

#### 7. Reader policy graph

Optional.

Contains:

* reader policy refs
* active reader mode
* allowed validation statuses
* allowed certainty levels
* allowed authority channels
* inclusion flags for disputed, fictional, or mythological material

## URI Policy

The export MUST define deterministic URI construction for:

* items
* properties
* statement nodes
* reference nodes
* value nodes, where needed
* validation decision nodes, if exported
* authority recognition nodes, if exported
* reader policy nodes, if exported

### Recommended URI scheme

Wikibase-aligned prefixes SHOULD be used where compatibility is desired:

```text
wd:   items
wdt:  direct properties
p:    statement properties
ps:   statement value properties
pq:   qualifier properties
pr:   reference properties
prov: provenance linkage
rdf:  RDF core predicates
xsd:  XML Schema datatypes
```

An implementation MAY use standard Wikidata namespace forms, but MUST be consistent and deterministic.

Kristal-specific metadata SHOULD use a declared namespace such as:

```text
kri:  Kristal artifact, validation, certainty, authority, and reader-policy terms
```

The exact namespace bindings MUST be recorded in `export.manifest.json`.

## Statement Node Identity

Each exported statement MUST have a stable identifier across runs given identical inputs.

Requirement:

* If the source provides a stable `assertion_id`, the statement node SHOULD be derived from it.
* If the source provides a stable Wikibase statement id, the statement node MAY be derived from it.
* If neither is available, the statement node MUST be derived from a deterministic hash of:

  * subject QID
  * predicate PID
  * normalized object value
  * normalized qualifiers, sorted deterministically
  * normalized references, sorted deterministically when included in identity mode
  * and an optional disambiguator when multiple identical statements exist.

The exact construction MUST be documented and recorded in the export manifest.

Recommended form:

```text
kri:statement/sha256:<hex>
```

or, for Wikibase-compatible exports:

```text
wds:<stable-statement-id>
```

Blank nodes SHOULD be avoided. If blank nodes are used, they MUST be deterministically skolemized.

## Statement Modeling

### Full projection

When:

```json
{
  "projection": "full"
}
```

the export MUST emit all selected statements according to the active export configuration and reader policy.

The full projection MUST emit:

* direct-value triples using `wdt:Pxx`, when compatible with the value type
* statement-node triples using `p:Pxx`
* statement-value triples using `ps:Pxx`
* qualifier triples using `pq:Pxx`
* reference linkage using `prov:wasDerivedFrom` or Wikibase-style reference linkage
* rank representation
* all selected references
* all selected qualifiers

If validation, certainty, authority, or reader-policy metadata is included, the export SHOULD emit it in separate metadata graphs rather than mixing it into the assertion graph.

### Truthy projection

When:

```json
{
  "projection": "truthy"
}
```

the export MUST emit only best-ranked statements per `(subject, property)` according to the rank rules below.

Rules:

* If preferred-rank statements exist for a given `(subject, property)`, only preferred statements are emitted.
* Else, normal-rank statements are emitted.
* Deprecated statements MUST NOT be emitted in truthy projection.
* If multiple statements share the best rank, all best-ranked statements MUST be emitted.
* The truthy projection MUST be deterministic given identical inputs.

The `truthy` projection is a WDQS compatibility projection. It MUST NOT be described as universal truth. It is only a rank-based selection of statements under the selected input, reader policy, and export configuration.

## Rank Rules

Kristal v5 WDQS export MUST support at least the following ranks:

```text
preferred
normal
deprecated
```

Rank MUST be represented deterministically.

Acceptable methods include:

* Wikibase-style rank predicates
* explicit rank triples using a dedicated Kristal or export-profile predicate

The method MUST be stated in the export manifest.

Recommended representation:

```text
wikibase:rank wikibase:PreferredRank
wikibase:rank wikibase:NormalRank
wikibase:rank wikibase:DeprecatedRank
```

## Value Modeling

Object values MUST be serialized in a way compatible with WDQS expectations.

### Item values

Item values SHOULD be serialized as item IRIs:

```text
wd:Q123
```

### String values

Plain strings MUST be RDF literals.

Language tags MUST only be used where the value is explicitly monolingual or language-scoped.

### Monolingual text

Monolingual text MUST be serialized as an RDF literal with a language tag.

### Time values

Time values SHOULD use:

```text
xsd:date
xsd:dateTime
```

Precision handling MUST be documented.

If the source provides lower precision than the RDF datatype can express directly, the exporter MUST either:

* preserve precision metadata using an additional predicate, or
* document the precision normalization in the export manifest.

### Quantity values

Quantities SHOULD be serialized as numeric literals.

Unit modeling MUST be documented.

If the unit is known, the exporter SHOULD emit a unit IRI or unit predicate.

### Coordinates

Coordinates MAY be serialized using:

* WKT literals, or
* dedicated latitude / longitude predicates.

The selected method MUST be documented.

### URLs

URLs SHOULD be serialized as IRIs.

### External identifiers

External identifiers SHOULD be serialized as literals unless a profile declares a deterministic IRI expansion rule.

## Value Normalization

Values MUST use Kristal-normalized forms from the source artifact where available.

If the export performs additional normalization, that normalization:

* MUST be deterministic,
* MUST be documented,
* MUST be recorded in the export manifest.

Normalization MUST NOT silently erase validation status, certainty level, authority scope, or reference metadata.

## Qualifiers

Qualifiers MUST be emitted as triples attached to the statement node.

Qualifier ordering in serialized output MUST be deterministic.

If a statement has multiple qualifiers for the same property, all MUST be emitted unless the selected reader policy or export configuration excludes them.

## References

References MUST be emitted as reference nodes.

Statement nodes MUST link to reference nodes deterministically.

If a statement has multiple references, all selected references MUST be emitted.

Reference node identity MUST be stable across runs given identical inputs.

Recommended reference node identity:

```text
kri:reference/sha256:<hex>
```

The hash target SHOULD include:

* normalized reference claims
* normalized source identifiers
* normalized evidence refs
* deterministic ordering of reference components

The exact construction MUST be documented and recorded in the export manifest.

## Validation, Certainty, and Authority Metadata

Kristal v5 separates:

* artifact identity,
* statement identity,
* assertion status,
* certainty level,
* validation status,
* authority recognition,
* and reader visibility.

This profile MAY expose that metadata in RDF.

If exported, the metadata MUST remain scoped. An assertion MUST NOT be represented as generally validated without also exposing the authority channel, validation policy, and scope that support that status.

### Assertion status

Allowed assertion status values:

```text
hypothesis
claimed
sourced
disputed
reviewed
validated
rejected
retracted
superseded
```

### Validation status

Allowed validation status values:

```text
not_evaluated
in_review
validated
conditionally_validated
disputed
rejected
revoked
```

### Certainty level

Allowed certainty level values:

```text
unknown
speculative
low
medium
high
established
not_applicable
```

### Validated-as values

Allowed validated-as values:

```text
hypothesis
claim
sourced_claim
reviewed_claim
high_confidence_fact
institutional_reference
publisher_declaration
technical_specification
legal_or_policy_position
mythological_corpus
fictional_corpus
symbolic_model
disputed_position
rejected_claim
```

### Authority metadata

If authority metadata is exported, it SHOULD include:

* authority channel id,
* recognition status,
* recognized-as value,
* validation policy ref,
* recognition scope,
* evidence refs where available.

Recognition by one authority channel MUST NOT imply recognition by another authority channel.

## Reader Policy Interaction

The exporter MAY accept a reader policy that filters which statements are exported.

Reader policy may select:

* authority channels,
* validation statuses,
* certainty levels,
* validated-as values,
* domains,
* subdomains,
* whether disputed statements are included,
* whether fictional corpora are included,
* whether mythological corpora are included.

If a reader policy is used, the export manifest MUST record:

* reader policy id,
* reader mode,
* included authority channels,
* included validation statuses,
* included certainty levels,
* included validated-as values,
* inclusion flags for disputed, fictional, and mythological material.

Allowed reader modes:

```text
reference_only
validated_only
high_certainty_only
research
creative
all_with_labels
custom
```

“Validated-only” means all visible statements satisfy the active reader policy. It does not mean all statements have maximum certainty or universal agreement.

## Determinism Requirements

The export MUST be byte-stable given identical inputs and the same profile settings.

Minimum requirements:

1. Use deterministic serializer configuration.
2. Prefer N-Quads for primary export.
3. Sort output N-Quads lexicographically by:

   1. graph IRI
   2. subject
   3. predicate
   4. object
4. Avoid blank nodes where possible.
5. If blank nodes are used, deterministically skolemize them.
6. Ensure deterministic namespace selection.
7. Ensure deterministic statement node identity.
8. Ensure deterministic reference node identity.
9. Ensure deterministic ordering of repeated qualifiers.
10. Ensure deterministic ordering of repeated references.
11. Ensure deterministic handling of language labels.
12. Ensure deterministic handling of rank projection.

The export manifest MUST record:

* profile id and version,
* projection,
* namespace choices,
* statement node identity scheme,
* reference node identity scheme,
* sorting parameters,
* serialization parameters,
* reader policy, if any,
* validation metadata export mode,
* authority metadata export mode,
* certainty metadata export mode.

## Export Manifest

The export manifest MUST be JSON.

Minimum shape:

```json
{
  "schema_version": "5.0",
  "artifact_type": "rdf_wdqs_export_manifest",
  "export_profile": "rdf-wdqs",
  "export_profile_version": "5.0",
  "created_at": "2026-01-01T00:00:00Z",
  "source_artifacts": [],
  "projection": "full",
  "serialization": {
    "format": "application/n-quads",
    "file": "export.rdf.nq",
    "sort_order": [
      "graph",
      "subject",
      "predicate",
      "object"
    ],
    "blank_node_policy": "avoid"
  },
  "namespaces": {},
  "statement_node_identity": {
    "mode": "assertion_id",
    "fallback": "deterministic_hash"
  },
  "reference_node_identity": {
    "mode": "deterministic_hash"
  },
  "rank_representation": {
    "mode": "wikibase_rank_predicates"
  },
  "reader_policy_ref": null,
  "authority_registry_ref": null,
  "metadata_graphs": {
    "validation": false,
    "certainty": false,
    "authority": false,
    "reader_policy": false
  }
}
```

Implementations MAY extend this manifest, but extensions MUST NOT change core export semantics without declaring a distinct profile or profile version.

## Conformance

An export is conformant to this profile if:

* it emits the required graphs for the selected projection,
* it follows deterministic URI and statement identity rules,
* it models statements, qualifiers, references, and ranks according to this profile,
* it preserves selected references and qualifiers,
* it is byte-stable under repeated builds,
* it records all required export parameters in the manifest,
* it does not represent scoped validation as universal validation,
* and it does not erase authority, certainty, or reader-policy distinctions when those distinctions are part of the selected export.

## Recommended Tests

Implementations SHOULD provide tests for:

### Fixture output

A fixture dataset with known expected N-Quads output.

### Determinism

Same inputs and same settings MUST produce identical bytes across runs.

### Rank / truthy projection

Tests SHOULD verify:

* preferred overrides normal,
* normal is used when preferred is absent,
* deprecated is excluded from truthy projection,
* multiple best-ranked statements are retained.

### Multi-reference stability

Tests SHOULD verify stable ordering and stable identity for multiple references.

### Qualifier stability

Tests SHOULD verify stable ordering and stable identity behavior when qualifiers repeat or overlap.

### Metadata graph separation

Tests SHOULD verify that metadata graph inclusion does not affect Kristal core content hash unless an integrity profile explicitly declares it.

### Reader policy filtering

Tests SHOULD verify that selected reader policies include and exclude statements deterministically.

### Authority-scoped validation

Tests SHOULD verify that validation metadata remains attached to its authority channel, validation policy, and scope.

## Interactions with Other Profiles

### RDF Integrity (RDFC)

The **RDF Integrity (RDFC)** profile may consume the deterministic RDF dataset emitted by this profile and compute RDF hashes or integrity proofs.

This WDQS export profile defines export shape and determinism. RDFC defines RDF canonicalization and integrity.

### Provenance Nanopub + PROV-O

The **Provenance Nanopub + PROV-O** profile may reuse the same statement and reference nodes.

Packaging remains separate from this WDQS export profile unless an implementation declares a combined profile.

### Query TPF Pagination

The **Query TPF Pagination** profile may expose exported RDF through constrained offline or local query surfaces.

This profile does not require a live SPARQL endpoint.

### Reader Policy Profile

The **Reader Policy** profile may define which authority channels, certainty levels, validation statuses, and validated-as values are included in the export.

When a reader policy is applied, it MUST be recorded in the export manifest.

### Authority Recognition Profile

The **Authority Recognition** profile may define the authority recognition records referenced or exported by this profile.

Recognition metadata MUST remain scoped.

## Notes

This profile preserves WDQS compatibility where useful, but Kristal v5 does not collapse knowledge into a single global truth layer.

The RDF export is a deterministic projection of selected Kristal artifacts under explicit profile settings. The meaning of “validated,” “recognized,” “reference,” or “truthy” depends on declared authority channels, validation policies, scopes, certainty levels, and reader policy.
