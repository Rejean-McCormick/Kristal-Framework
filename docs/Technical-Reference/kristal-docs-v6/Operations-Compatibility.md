# Operations: Compatibility

Kristal v6 is a breaking semantic generation relative to v5. Within v6, compatibility should preserve both structural and semantic meaning.

## Stable expectations

Consumers should version-gate changes to:

- canonicalization/hash boundaries;
- `kristal_state` required structure;
- valuation value semantics;
- value-state meaning;
- record-role vocabulary/semantics;
- actionability semantics;
- validation/recognition meaning;
- reader/view-policy semantics.

## Additive evolution

Profiles may add optional valuation dimensions, coordinates, projections or role-specific conventions when consumers can safely ignore what they do not understand.

## Breaking evolution

Treat these as breaking unless explicitly versioned:

- changing the meaning of an existing valuation dimension;
- coercing `unknown`/`not_applicable` into numeric values;
- changing what `automatic` authorizes;
- changing content-hash boundaries;
- changing validation/recognition semantics;
- silently promoting a derived projection to canonical truth.

## Upgrade principle

Prefer machine-readable version gates and validation over heuristic compatibility.
