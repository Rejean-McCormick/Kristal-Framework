# v8 compatibility contract

## Mandatory backward compatibility

A v8 implementation:

1. **MUST** accept valid v6 `kristal_state` artifacts unchanged.
2. **MUST** accept valid v7 Kristall artifacts unchanged.
3. **MUST NOT** redefine any v6 field.
4. **MUST NOT** redefine v7 `KQ`, `KP`, `KA` or `KS` identity.
5. **MUST NOT** require lexical artifacts, query indexes or semantic fingerprints for semantic validity.
6. **MUST** treat v8 language/query artifacts as additive companions or derived materializations.
7. **MUST NOT** mutate a v6/v7 artifact merely to enable v8 capabilities.

## v7 human labels

Existing v7 `preferred_label`, `label`, `description` and `title` fields remain valid. In a v8 processor they are compatibility/display fallbacks, not semantic identity and not mandatory lexical authority.

A v8 implementation MUST NOT require a v7 artifact to be rewritten merely to externalize these labels.

## v6 adapters

A v8 adapter MAY address v6 namespaced referents directly or map them to v7 semantic identities when such mappings already exist. Adapter-generated mappings preserve provenance and MUST NOT silently mint equivalence.

## Query compatibility

v8 pagination and capability negotiation extend, rather than contradict, v6 query principles. A v8 engine reading v6 material MUST preserve v6 distinctions such as valuation semantics, applicability and record role when they matter to interpretation.

## Capability loss on downgrade

A v8 artifact MAY be projected to v7/v6 where representable. If lexical stacks, query indexes, semantic fingerprints, query plans or AI context metadata are omitted, the downgrade MUST declare capability loss. Semantic assertions MUST NOT be changed to compensate for unavailable v8 capabilities.

## Frozen compatibility surfaces

Files listed in `contracts/v8-compatibility-lock.json` are frozen inherited inputs. v8 conformance tooling verifies their hashes so v8 cannot accidentally mutate its v6/v7 substrate.
