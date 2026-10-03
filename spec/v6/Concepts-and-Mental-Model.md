# Concepts & Mental Model

Kristal v6 separates a stable structural substrate from domain-specific semantics.

## Structural invariants

Across domains, Kristal keeps these concerns stable:

1. stable identities / referents;
2. atomic assertions;
3. explicit applicability;
4. typed valuations;
5. provenance and evidence;
6. validation and authority recognition;
7. conflict, succession and lineage;
8. deterministic identity and reproducibility;
9. reader/projection separation;
10. actionability distinct from execution authority.

## Programmable semantics

What varies by domain is the interpretation of the structure.

The same ordinal valuation vocabulary might mean:

- proof closure in mathematics;
- diagnostic support in automotive troubleshooting;
- constitutive necessity in recipes;
- administrative applicability in an institutional pathway;
- taxonomic acceptance in botany;
- maintenance necessity in building operations.

The important rule is that the **dimension is explicit**. `high` has no universal meaning outside the valuation dimension that defines it.

## Canonical core

```text
referent
   ↓
assertion
(subject → predicate → object)
   │
   ├── valuations[]
   ├── coordinates
   ├── applicability
   ├── record_role
   ├── actionability
   ├── evidence / provenance
   ├── validation / recognition
   ├── conflicts / supersedes
   └── lineage
```

Readers and projections are built from this canonical layer. A timeline, diagnostic tree, admission pathway or cross-scale view does not need to be stored as a second truth source.

## Role of `not_applicable`

One of the strongest safeguards in the model is the ability to say that a measurement dimension simply does not apply to a structural assertion.

`not_applicable` is not “zero” and not “unknown”. It is a semantic firewall.

## Human/machine accumulation

A Kristal can be improved incrementally:

- an AI extracts a relationship;
- evidence is attached;
- a human corrects its applicability;
- a later authority recognizes it;
- a new rule supersedes the old one;
- a derived projection is rebuilt;
- the next agent starts from that accumulated state.

The result is durable intellectual capital rather than disposable generated text.
