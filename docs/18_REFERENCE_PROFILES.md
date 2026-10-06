# Reference profiles

## 1. Purpose

The v9 core should remain small. Concrete behavior that can evolve independently belongs in named profiles.

Profiles are contracts, not hidden optimizer choices.

## 2. Logical commitment profile

Proposed initial profile:

```text
kristal.logical/jcs-sha256-v1
```

Expected properties:

- contract-specific normalization precedes canonicalization;
- set-like collections are deterministically normalized;
- ordered collections preserve order;
- JCS provides canonical JSON bytes;
- SHA-256 provides the digest;
- a domain separator binds the contract/profile context.

This profile is appropriate only for logical contracts whose normalized representation is JSON-compatible.

## 3. Inline JSON materialization

```text
kristal.materialization/inline-json/1
```

Use when:

- artifact is small;
- direct readability is valuable;
- partial physical retrieval is unnecessary;
- one-file replacement cost is acceptable.

This should be the default shape for many small Kristals.

## 4. Native blob materialization

```text
kristal.materialization/native-blob/1
```

Use when a logical contract defines or references a domain-native encoding whose structure should remain intact.

The materialization descriptor still records media type, byte digest and size.

## 5. Segmented JSONL materialization

```text
kristal.materialization/segmented-jsonl/1
```

Intended for large homogeneous or stream-friendly artifacts.

Properties may include:

- immutable segments;
- deterministic assignment rule;
- optional compression;
- optional local dictionaries;
- reconstruction order independent from logical ordering unless the contract requires order.

## 6. Expanded v6 materialization/projection

```text
kristal.materialization/kristal-state-v6/1
```

Provides an expanded `kristal_state/6.0` representation when a consumer requires the portable v6 contract.

For domain-native v9 artifacts, this may actually be a projection plus materialization rather than a representation of the exact same logical contract. The descriptor must make that distinction explicit.

## 7. Columnar profile

A future profile may define a compact columnar representation for homogeneous relation families.

It should be developed only after the base reconstruction and commitment semantics are stable.

The profile should not require Parquet specifically unless the community intentionally standardizes a Parquet interoperability profile.

## 8. Runtime profiles

Runtime profiles may define environments such as:

```text
kristal.runtime/sqlite/1
kristal.runtime/arrow/1
kristal.runtime/search/1
```

These are optional ecosystem contracts, not semantic core requirements.

## 9. Profile versioning

Changing behavior under an existing profile identifier is forbidden when it affects reconstruction, logical equality or byte determinism promised by that profile.

```text
PROFILE RULE CHANGE
    =>
NEW PROFILE ID
```
