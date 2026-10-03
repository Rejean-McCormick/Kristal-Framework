# UNESCO Thesaurus alignment

## Status

Kristal v7 designates the **UNESCO Thesaurus** as Kristall's first `reference_spine` Knowledge Organization System (KOS) for encyclopedic Category/Subject navigation.

## Pinned baseline

Kristall v7 **pins the model at 7 domains and 88 microthesauri**. This is the normative TOC baseline used by the standard.

Reference observed on **2026-10-02**:

- UNESCO Vocabulary Services: <https://vocabularies.unesco.org/en/>
- UNESCO Thesaurus vocabulary: <https://vocabularies.unesco.org/unesco/en/>
- vocabulary identifier: `http://vocabularies.unesco.org/thesaurus`
- vocabulary metadata reports last modification: **2026-06-29**

The current service describes approximately **4,500 concepts**, **5 languages**, **7 domains** and **88 microthesauri**.

The machine-readable baseline is stored in `reference-kos/unesco-thesaurus-baseline.json`.

## Provenance note

UNESCO presentation metadata is not perfectly uniform across every page. Kristall records this only as source provenance; **the v7 baseline remains fixed at 88 microthesauri**.

## External properties used

- format: SKOS / Linked Open Data
- declared construction standard: ISO 25964
- multilingual labels: Arabic, English, French, Russian, Spanish
- stable/dereferenceable concept URIs
- 7 top-level domains
- 88 microthesauri

Kristall's local profile is a navigation/cache layer. UNESCO remains the external authority for the vocabulary itself.

## Import policy

Kristall SHOULD preserve UNESCO URIs and MUST NOT manufacture replacement UNESCO identifiers.

Full import of the vocabulary is optional. A deployment may lazily materialize only the concepts required by its Subjects.

## Sovereignty

```text
UNESCO URI != KQ
UNESCO classification != Kristall truth
UNESCO hierarchy != mandatory single-parent ontology
```

KQ remains Kristall's native semantic identity. UNESCO relationships are external semantic/classification mappings.

## Domain 7

UNESCO's `Countries and country groupings` is preserved faithfully in the KOS mirror. Kristall's default TOC interprets it as a **facet family** rather than a core knowledge discipline.

## Future KOS alignment

Additional KOSs — research-field, education, industry, biomedical, geographic or others — can be registered alongside UNESCO. No secondary KOS silently replaces the UNESCO reference spine or KQ identity.
