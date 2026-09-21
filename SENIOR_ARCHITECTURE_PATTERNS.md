# Senior Architecture Pattern Alignment

Kristal is primarily a **specification and conformance repository for immutable epistemic artifacts**. The senior architecture patterns below apply to the **build, validation, distribution and runtime-pack operational plane**. Unless a profile explicitly says otherwise, they are operational guidance and are **not part of Kristal artifact conformance**.

| Pattern | Kristal alignment |
|---|---|
| Circuit Breaker | **Operational guidance** for fallible SenTient/resolver calls. |
| Dead Letter Queue (DLQ) | **Operational guidance** for poison/repeatedly failing ingestion and build work, with triage/ownership expectations. |
| Exponential Backoff + Jitter | **Operational guidance** for retryable pipeline/distribution failures. |
| Timeout Budgets / Cancellation | **Operational guidance** with hard timeouts and cancellation by pipeline stage. |
| Rate Limiting / Throttling | **Operational guidance** for bounded tenant/resource usage. |
| Graceful Degradation | **Operational guidance** for reader-policy and rendering failure paths without changing epistemic meaning. |
| Blue-Green Deployment | **Operational guidance** for Runtime Pack release/activation. |
| Canary Release | **Operational guidance** for staged Runtime Pack rollout. |
| Distributed Tracing | **Operational guidance** through recommended `trace_id`, `span_id`, correlation propagation and structured operational events. |
| Metrics & Alerting | **Operational guidance** through recommended dashboards, health signals and actionable alerts. |
| CQRS framing | **Non-normative guidance** where read/query materializations are separated from authoritative artifact inputs. |

## Important non-claims

- **Artifact immutability is not the same thing as the “Immutable Infrastructure” deployment pattern.**
- These patterns do not change Kristal's normative separation of artifact integrity, validation, authority recognition, reader visibility and runtime activation.
- A pattern listed here is not automatically implemented by every Kristal deployment; this repository defines guidance/contracts and conformance surfaces.

## Evidence anchors

- `docs/Technical-Reference/kristal-docs-v5/00-overview/vision-and-scope.md`
- `docs/Technical-Reference/kristal-docs-v5/08-ops/failure-paths-and-resilience.md`
- `docs/Technical-Reference/kristal-docs-v5/08-ops/logging-and-correlation-ids.md`
- `docs/Technical-Reference/kristal-docs-v5/08-ops/release-strategies.md`
