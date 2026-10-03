# Migration

Kristal v8.0.0 is additive. There is no mandatory migration of v6 or v7 canonical artifacts.

For v7 → v8 adoption, see `spec/v8/Migration-v7-to-v8.md`. The recommended path is to keep existing registries unchanged, add capability metadata, external lexical Kristals, derived query indexes and KQP/AI-context services.

Downgrade from v8 can omit v8-only capabilities, but it must not rewrite semantic assertions to compensate for the loss.
