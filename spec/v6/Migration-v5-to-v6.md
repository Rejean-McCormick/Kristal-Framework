# Migration: v5 → v6

Kristal v6 is a breaking semantic upgrade. The active vocabulary changes from epistemic-specific field names to domain-neutral abstractions.

## Main mapping

| v5 | v6 |
|---|---|
| Structured Epistemic State | `kristal_state` |
| `certainty_level` | `valuations[]` |
| `uncertainty` | valuation value state / method / typed value |
| `qualifiers` | `coordinates` |
| `scope` | `applicability` |
| certainty summary | valuation summary |
| implicit data type | `record_role` where useful |
| implicit automation assumptions | explicit `actionability` |

## Important semantic change

Do not migrate by replacing:

```text
high → 0.8
```

or:

```text
unknown → 0
```

Instead define the dimension and value semantics explicitly.

## Working / Reference

The old Working/Reference distinction should be understood through artifact lifecycle/status, validation and authority recognition rather than as two universal artifact classes that duplicate the canonical state.

## Exchange / Runtime Pack

Existing Exchange and Runtime Pack consumers can remain as legacy adapters or derived materializations, but new domain models should not make them the canonical truth layer.

## Migration strategy

1. identify the v5 meaning of `certainty_level` per assertion family;
2. define explicit valuation dimensions;
3. migrate qualifiers to domain coordinates;
4. migrate scope to applicability;
5. add record roles only where the role is actually known;
6. add actionability only where policy explicitly defines human/automation boundaries;
7. recompute canonical identities/hashes;
8. rerun validation and reader/projection tests.
