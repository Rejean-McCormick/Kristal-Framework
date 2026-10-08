# Kristal v10 Compatibility Contract

V10 is additive above v9.

1. Valid frozen v6, v7 and v8 artifacts remain valid unchanged.
2. Valid v9 logical artifacts, state snapshots, derivations, materialization manifests, exchanges, activations and commitments remain valid unchanged.
3. The v9 commitment profiles `kristal.logical/jcs-sha256-v1` and `kristal.state-commitment/jcs-sha256-v1` are not redefined by v10.
4. A v10 implementation MUST NOT require conversion of v9 semantic state into host-specific identifiers.
5. Host bindings, publication records and directories are outside the v9 logical/state commitment projections.
6. A v10 host profile MAY add stricter operational requirements, but MUST NOT reinterpret logical state.

```text
V10 ADOPTION != V9 REWRITE
HOST MIGRATION != LOGICAL REVISION
```
