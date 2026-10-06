# v9 helper tooling

V9's normative behavior is defined by `spec/v9/`, `schemas/v9/`, and `tck/v9/`.

The primary executable reference surface is currently the zero-dependency JavaScript implementation under `reference/js/`:

```text
kristal-ref logical-commitment-v9
kristal-ref state-commitment-v9
kristal-ref verify-logical-artifact-v9
kristal-ref verify-state-v9
kristal-ref verify-materialization-v9
kristal-ref publish-state-v9
kristal-ref activate-state-v9
```

No automatic materialization planner is normative in v9.0-draft.1. Storage heuristics remain tooling concerns and must emit an explicit declared materialization profile.
