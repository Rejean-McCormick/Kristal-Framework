# Kristal v9 Compatibility Contract

V9 MUST accept inherited v6, v7, and v8 artifacts according to their frozen contracts. V9 MUST NOT redefine `kristal_state/6.0`, KQ/KP/KA/KS semantic identity, or v8 language/query semantics.

`contracts/v9-compatibility-lock.json` freezes inherited machine and TCK surfaces.

V9 is additive: domain-native v9 artifacts MAY project to v6 for portable interoperability. Such projections MUST be declared and MUST NOT silently replace a richer domain-native canon.

Downgrade MAY lose v9 materialization/lifecycle capabilities but MUST NOT rewrite inherited semantics to simulate support.
