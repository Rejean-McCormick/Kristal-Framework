# Kristall TOC, categories and subjects

Kristall v7 uses an explicit encyclopedic navigation model so the Mesh does not become an undifferentiated graph.

## 1. Reference spine

The **UNESCO Thesaurus** is the default external Knowledge Organization System (KOS) for broad Category/Subject navigation. It is imported as an external reference spine, not as Kristall's sovereign identity system.

Kristall keeps native `KQ` identities and maps them to UNESCO's permanent URIs.

```text
Kristall KQ category/subject
        ↕ mapping
UNESCO SKOS concept / concept group URI
```

## 2. Category

A **Category** is a relatively stable navigational region used to partition and browse the encyclopedia.

Category is not a claim that every Subject has one unique parent. Subjects are polyhierarchical.

The v7 TOC baseline is pinned to UNESCO's **7 domains and 88 microthesauri** model (observed 2026-10-02). Domains 1–6 default to `knowledge_category`. Domain 7 (Countries and country groupings) defaults to `facet_category`, because geography/jurisdiction commonly cuts across many subjects rather than behaving as one discipline.

## 3. Subject

A **Subject** is a semantic territory that can be explored under multiple orientations.

Examples: Biology, Law, Energy, Music, Finance, Time.

A Subject:

- has one stable KQ identity;
- may belong to multiple Categories;
- may map to zero, one or many UNESCO concepts;
- has no mandatory single discipline parent;
- may have one or more natural/default Axis Types;
- can generate many Kristal projections.

```text
SUBJECT != CATEGORY
SUBJECT != AXIS
SUBJECT != KRISTAL FILE
```

## 4. External concept mapping

Classification into an UNESCO microthesaurus is distinct from mapping to one exact UNESCO concept.

A Subject can therefore be placed in `2.70 Biology` before an exact concept URI has been resolved.

Exact concept mappings use SKOS-like semantics:

- `exactMatch`
- `closeMatch`
- `broadMatch`
- `narrowMatch`
- `relatedMatch`

Mappings MUST NOT be promoted merely from label equality or resonance.

## 5. Why the 100 seed Kristals matter

The 100 seed Kristals are treated as Subject samples. Their names define territories; their recorded natural angles provide evidence for Axis Types. The UNESCO Thesaurus organizes **what area** the Subject belongs to; Kristall Axis Types organize **how that Subject is examined**.
