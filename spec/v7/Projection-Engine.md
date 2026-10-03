# Projection engine

The projection engine turns a Kristall region into a portable Kristal.

## Required inputs

For a deterministic materialized projection, declare at least:

- Kristall snapshot/manifest identity;
- stable subject selector;
- primary orientation axis;
- optional secondary orientation axis;
- contextual filters/applicability window;
- source inclusion policy;
- conflict policy;
- transform/projection version.

## Selection outline

1. resolve subject region;
2. rank/filter assertions by axis affinity and structural role;
3. include required connective concepts;
4. preserve conflicting material under policy;
5. include evidence/provenance references;
6. generate v6 assertions without changing their meaning;
7. attach `extensions.kristal_v7` lineage metadata;
8. validate output against the v6 schema.

## Maximum axes

A portable projection has exactly one primary orientation axis and zero or one secondary orientation axis.
