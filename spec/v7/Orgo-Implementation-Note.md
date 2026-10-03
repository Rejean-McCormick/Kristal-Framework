# Orgo implementation note — resonance alignment

This note is informative for the Orgo repository. It does not claim runtime implementation.

Recommended Orgo-side addition:

```text
docs/Technical-Reference/SEMANTIC_RESONANCE.md
```

The document should state:

1. Orgo keeps Q/P/R/S semantic charters unchanged.
2. A shared `semantic_resonance_set/1.0` contract may be used for candidate recognition, retrieval and routing.
3. Resonance does not bypass RBAC, workflow evaluation, Case/Task ownership or command validation.
4. When exported to Kristall, Orgo Q/P/R/S IDs may map to KQ/KP through explicit external mappings.
5. Orgo remains standalone-first; Kristall is an optional semantic/encyclopedic consumer/provider.

No current Orgo database migration is required merely to support the mapping contract.
