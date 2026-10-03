# v8 helper tools

These scripts are **non-normative** demonstrations of the v8 capability layer.

- `build_lexicon_delta.py` emits unresolved semantic references without inventing terms.
- `resolve_lexicon.py` demonstrates deterministic lexical precedence and explicit missing/conflict behavior.
- `semantic_slice.py` builds an exact bounded, direction-aware subgraph from existing v7 registries/Mesh without modifying canonical inputs.
- `compile_ai_context.py` compiles a KQP result into whole semantic atoms under a hard byte budget and optional declared token estimate.

Normative behavior is defined by `spec/v8/` and `schemas/v8/`.
