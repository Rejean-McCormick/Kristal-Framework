# v8 design rationale (informative)

This document is informative, not normative.

The final v8 architecture intentionally applies several established senior architecture/security patterns where they align with Kristal's existing model:

- **Anti-Corruption Layer** → v6/v7/external-KOS adapters isolate foreign/legacy models.
- **CQRS/read-model separation** → canonical state remains authoritative while query indexes and AI projections are derived.
- **Sharding/Data Mesh** → semantic and lexical universes can be federated with domain stewardship under shared contracts.
- **Claim Check** → large source/evidence payloads are referenced and expanded on demand.
- **Graceful Degradation** → missing lexicons, shards or indexes are explicit states, not fabricated answers.
- **Timeout/agentic budgets** → deterministic limits live outside the model and propagate to child queries.
- **Canonical Semantic Fingerprints** → versioned semantic digests are distinct from byte hashes.
- **Schema valid is not authorized/semantically valid** → validation is layered.
- **Model is an Untrusted Planner** → model proposals pass deterministic gates.
- **Prompt/Context Taint** → retrieved context keeps provenance/trust classification.
- **Independent Tamper Anchor** → high-assurance deployments may externally anchor snapshot/release roots.

Patterns concerned mainly with deployment infrastructure (for example blue/green rollout, Kubernetes service mesh, DLQ, CDN) are deliberately not part of the Kristal semantic standard. They remain implementation/operations choices.
