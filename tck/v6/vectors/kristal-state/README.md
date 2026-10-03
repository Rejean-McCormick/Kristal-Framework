# Kristal State v6 conformance fixture

`kristal-state.example.json` is the canonical positive fixture shared with the v6 reference adapter.

A conformant verifier must at minimum enforce:

- `schema_version = 6.0`;
- `artifact_type = kristal_state`;
- typed `valuations[]`;
- separation of `value_state` from `value`;
- supported `record_role` and `actionability.mode` vocabularies;
- `kristal.v6:jcs-rfc8785` identity semantics;
- exclusion of `state_id`, `content_hash` and `signatures` from the state hash target.

Legacy v5 Exchange and Runtime Pack vectors remain under `kristal-docs-v5/09-test-vectors/` for compatibility adapters only.
