# Kristal v10 Architecture

```text
                    Semantic plane (v9, unchanged)

 Logical Artifacts ─────► immutable State Snapshot
                               │
                               ├──── pinned external state/artifact refs
                               │
                               ▼
                    materializations / exchange

────────────────────────────────────────────────────────────────
                    Hosted-network plane (v10)

                       Kristal Node Manifest
                          │             │
                    Host Binding(s)   Directory link(s)
                          │
              ┌───────────┼───────────────┐
              ▼           ▼               ▼
          Publication   Activation      Automation
          locations     surfaces        surfaces
              │
              ▼
        attestations / mirrors
```

The semantic plane defines content, identity, authority and exact state composition. The hosted-network plane makes that state discoverable, distributable and operable on concrete infrastructure.

A repository can host a Kristal node, but a repository is not itself the node. One node may be mirrored across multiple hosts, and one host account may contain many nodes.
