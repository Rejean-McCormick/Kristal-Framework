# Artifacts

Kristal v6 centers on **Kristal State** as the canonical structured artifact. Other files are supporting records, policies, manifests or derived materializations.

## Canonical artifact

### Kristal State

A `kristal_state` contains atomic assertions plus the labels required to interpret them safely: typed valuations, coordinates, applicability, roles, actionability, provenance/evidence, validation/recognition references, conflict/succession/lineage and integrity metadata.

See [Kristal-State](Kristal-State.md).

## Supporting artifacts

### Validation / recognition records

These record policy evaluation and scoped authority recognition. They do not rewrite the assertion into universal truth.

### Reader Policy

Controls which labeled assertions or projections a consumer may expose.

### Referent Registry

Carries stable domain-neutral referent identities where a profile uses a separate registry.

### Authority / trust material

Trust roots, channels, signature metadata and related policy may be maintained separately from the state.

## Derived artifacts

Indexes, query stores, runtime materializations, timelines, navigation graphs and consumer projections can be derived from canonical states.

They should remain tied to source state identifiers and rebuildable inputs.

## Legacy artifacts

The v5 Exchange / Runtime Pack / shard / federation surfaces are retained in this wiki as compatibility documentation. New v6 models should not treat them as a second canonical truth layer.
