# AI compact encoding

## Purpose

Expanded JSON is readable and interoperable but can waste AI context by repeating long semantic IDs and field names. v8 defines an optional compact projection profile for AI transport while keeping expanded JSON as the canonical exchange form.

Profile: `kristal-ai-compact/1.0`

## Symbol table

A compact bundle MAY assign local symbols:

```text
0 → KQ847291
1 → KP31
2 → KS9021
```

Payload atoms can then reference `0`, `1`, `2`. Local symbols have meaning only inside the bundle and MUST NOT become persistent semantic identities.

## Determinism

For deterministic compact output, symbol assignment SHOULD follow first canonical occurrence after stable ordering of selected atoms. A compact bundle MUST include enough metadata to expand losslessly to the semantic IDs used by the source result.

## No semantic compression

Compact encoding may remove syntactic repetition. It MUST NOT merge distinct assertions, erase provenance, convert uncertainty to certainty or replace unresolved identities with guessed labels.

## Interoperability

Processors that do not support compact encoding may request `expanded_json`. Capability negotiation declares supported output encodings.
