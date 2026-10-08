# Migration from v9 to v10

Migration is additive.

1. Keep existing v9 logical artifacts and state snapshots unchanged.
2. Add a `.kristal/node.json` node manifest.
3. Add one or more host binding descriptors under `.kristal/bindings/`.
4. Add `.kristal/capabilities.json` describing v10 hosted-network capabilities.
5. Optionally add a directory for multi-node deployments.
6. Continue using v9 logical/state commitment verification.

No v9 state rehash is required solely to adopt v10.

```text
V10 ADOPTION != V9 REWRITE
```
