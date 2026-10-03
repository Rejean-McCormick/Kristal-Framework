# DaaT integration boundary

**Status:** informative ecosystem integration profile for Kristal/Kristall `7.0.0-draft.3.2`.

**DaaT** is an optional external anti-corruption/admission boundary used by Interaction Kernel integrations in front of Kristal/Kristall. Its stable machine identifier is `daat`. Kristal/Kristall does not require DaaT in order to exist or conform to this standard.

## Boundary

DaaT may:

- admit an Interaction Kernel request under an explicit versioned Profile;
- verify the pinned Kristal/Kristall compatibility baseline;
- map admitted source-owned exports or artifact references into a declared Kristal-native input contract;
- invoke Kristal-native build/validation interfaces;
- validate returned portable artifacts and pass immutable artifact references, receipts or events back through Interaction Kernel.

DaaT does **not**:

- crawl or acquire source material;
- own source bytes, snapshots or long-lived media storage;
- become a general corpus cleaning, deduplication or semantic-normalization engine;
- own another application's mutable operational state;
- mint or reinterpret Kristall `KQ` / `KP` / `KA` / `KS` semantic identities;
- author Kristall Mesh, axes, KOS/TOC registries, source registries or crystallization decisions on behalf of Kristal/Kristall.

These semantic authorities remain inside Kristal/Kristall. Acquisition and persistent source storage remain outside DaaT.

## Portable compatibility

The active portable interchange remains the unchanged v6 contract:

```text
artifact_type  = kristal_state
schema_version = 6.0
```

Kristall v7 may ingest such Kristals, preserve their source identity, perform semantic alignment and crystallization, and emit new v6-compatible projections carrying v7 lineage under `extensions.kristal_v7`. DaaT may transport or explicitly map across the external boundary, but it does not perform Kristall's semantic identity resolution or crystallization authority.

## Ownership model

```text
source owner / source store
          │ immutable snapshot or ArtifactRef
          ▼
Interaction Kernel
          │ admitted versioned Profile
          ▼
        DaaT (`daat`)
          │ explicit contract mapping
          ▼
Kristal portable interface (`kristal_state/6.0`)
          │
          ▼
Kristal / Kristall v7
```

Cross-boundary transport does not transfer ownership. A source system keeps authority over its mutable operational state and source storage; Kristal/Kristall owns the semantic artifacts it creates.
