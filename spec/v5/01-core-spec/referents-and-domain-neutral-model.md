# Referents and the domain-neutral knowledge model

## Status

Normative profile — Kristal v5, Referent Registry `1.0.0`.

## Decision

Kristal does **not** impose a universal people-first, concept-first, organization-first, or process-first ontology. It represents epistemic assertions over stable **referents**. A consumer domain MAY choose a dominant navigation view without changing Kristal semantics.

A referent is identified by a stable internal `ref` and a deliberately shallow `kind`. The normative kinds are `person`, `collective`, `work`, `edition`, `manifestation`, `document`, `concept`, `place`, `installation`, `activity`, `process`, `event`, `physical_object`, `system`, and `other`.

`person` and `collective` are the only actor-oriented distinctions fixed by this profile. Kristal does not require a universal subdivision of collectives into groups, organizations, institutions, companies, councils, or movements. Such classifications belong in `classifications` or domain extensions.

## Assertions remain authoritative knowledge structure

The Referent Registry does not contain the domain's truth claims. Relations such as `author_of`, `operates`, `located_in`, `concerns`, or `uses` remain assertions in a Structured Epistemic State with evidence, provenance, certainty, status, validation and authority metadata.

```text
Referent Registry                  Structured Epistemic State
stable identities                 assertions
shallow kinds          +          predicates / relations
external identifiers              evidence / provenance
labels                            certainty / validation
```

## Concepts and glossaries

A `concept` is a valid referent, but this does not make concepts a required primary axis. A glossary is normally a consumer projection/index over concepts linked by assertions to actors, works, processes, documents or other referents. Kristal does not require one canonical dictionary definition.

## External identifiers

Wikidata QIDs, VIAF IDs, Project Gutenberg IDs and similar identifiers are external anchors. They MUST NOT replace the Kristal `ref` as the internal identity and MUST NOT by themselves confer epistemic validity.

## Works, editions and manifestations

Consumers that model cultural/documentary material SHOULD distinguish:

```text
work != edition != manifestation
```

A work is the intellectual/creative work; an edition is a particular editorial realization; a manifestation is a concrete digital or physical carrier/file/provider representation.

## Consumer views

A Christian intellectual corpus may be people-first. An industrial corpus may be installation/process-first. An art corpus may be artist/work-first. These are projection choices, not changes to Kristal core semantics.

## Contract

Machine-readable contract: `../02-schemas/referent-registry.schema.json`.
