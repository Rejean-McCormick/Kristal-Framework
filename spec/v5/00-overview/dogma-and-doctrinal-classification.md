# Dogma and doctrinal classifications

## Status and scope

Informative modeling guidance, 2026-09-24. Uses existing Kristal v5 schemas;
introduces no new core field, enum, artifact, or required profile.

En français : « dogme » est une classification du contenu, attribuée à une
proposition dans une tradition et justifiée par des sources. Ce n'est pas un
nouveau niveau de certitude. Les assertions, qualificatifs, sources et mécanismes
de reconnaissance existants suffisent.

## Represent the classification as an assertion

Keep the religious proposition and the assertion about its doctrinal status
separate. Use `statement.subject` to identify the proposition,
`statement.predicate` for a corpus-defined doctrinal-status relation, and
`statement.object` for the corpus-defined concept of dogma. Entity and predicate
identifiers use the existing `external_id` or `iri` fields; object entities use
`kind: item` with an entity reference in `value`.

Use existing `statement.qualifiers` to identify the tradition or institution
in which the classification applies and, when sourced, the relevant date or
period. Connect the precise defining passage through existing provenance and
evidence references. Preserve original wording, edition and attribution rather
than treating an editorial paraphrase as an institutional definition.

The example uses `doctrine:has_doctrinal_status`, `doctrine:dogma`,
`doctrine:within_tradition`, and `doctrine:classification_source` as illustrative
local identifiers. They are not new Kristal-reserved terms. A corpus may also
represent theological opinion, non-definitive teaching or an open question as
content concepts using exactly the same structure. Their definitions and mapping
criteria belong to corpus curation, not the core schema.

## Keep the existing dimensions independent

| Existing field | Interpretation |
| --- | --- |
| `assertion_status` | State of the assertion about doctrinal classification: claimed, sourced, reviewed, etc. |
| `certainty_level` | Strength of that assertion in its declared scope; dogma does not automatically imply `established`. |
| `validated_as` | Existing epistemic classification, such as `sourced_claim` or, when justified, `institutional_reference`. |
| `authority_recognition_refs` | Actual scoped recognition records, when available. Describing a church's teaching does not create a church-issued recognition record. |
| `scope` | Existing domain plus subdomain, jurisdiction and time window as appropriate. `culture` with a religious subdomain is one valid choice; `religion` is not a core domain enum. |
| `provenance_refs` / `evidence_refs` | Sources and review evidence for the classification. |

The schema enums for `validated_as` and `recognized_as` do not include `dogma`.
Neither `dogma` nor `religion` should be inserted into a core enum to encode this
use case. `institutional_reference` alone is insufficient to identify a dogma:
it also covers other institutional reference material.

`established` remains relative to authority, scope and policy, not universal
truth. `not_applicable` is available when factual certainty is not the appropriate
measure, but is not mandatory merely because content is religious. Likewise,
`mythological_corpus` is available for a chosen narrative/cultural reading; it is
not a mandatory label for every religious proposition or doctrinal classification.

## Recognition, disagreement and history

Distinguish the institution described in a qualifier from the issuer of a Kristal
recognition. A curator can document what an institution teaches without being
that institution or signing on its behalf. Start extracted classifications as
sourced or claimed as warranted; only assign validation and recognition after
the relevant process and supporting records exist.

Store an author's interpretation as a separate assertion with its own source.
Do not infer that every statement by a saint, doctor, theologian or pope is a
dogma. Do not infer contradiction merely from different wording. Record genuine
conflicts, later corrections and lineage through the existing mechanisms;
preserve dates and authority scopes instead of overwriting historical positions.

## Reading and querying

To identify dogmas, select classification assertions whose predicate and object
match the corpus vocabulary, then restrict by tradition, time and applicable
reader policy. Resolve their subjects to the propositions and source passages.
A `high` certainty filter or `institutional_reference` filter alone is not a
dogma filter. Qualifier-aware filtering depends on the reader's declared query
capabilities; this guidance does not add a new required query operator.

Present separately: the teaching, its documented doctrinal status, the sources,
and associated interpretations. A personal reader position does not rewrite the
institutional classification. Neither ingestion nor compilation grants official
endorsement.

## Executable example and checks

[Dogma classification example](../10-examples/dogma-classification.example.json)
is a deliberately synthetic Working State with one classification assertion.
It is not an actual Catholic dogma, an endorsement, or a production content-addressed
artifact. Repeated-digit IDs are fixture placeholders, as in other examples.
Its local human-submission source and provenance are fully embedded. Replace them
with verified sources, exact passages and computed identifiers for production.

The existing release validator checks the example against the unchanged Structured
Epistemic State schema. Additional negative checks ensure `dogma` cannot be used
as a certainty level or validated-as enum, and that an unrecognized core field is
rejected. These checks establish structural compatibility, not doctrinal accuracy.

See [Structured Epistemic State](../01-core-spec/structured-epistemic-state.md),
[Assertion status and certainty](../01-core-spec/assertion-status-and-certainty.md),
and [Authority recognition](../01-core-spec/authority-recognition.md).
