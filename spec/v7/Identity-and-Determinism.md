# Identity and determinism

v7 preserves the v6 source identity boundary and adds a separate opaque semantic identity space for Kristall.

## Source Kristal identity

A source v6 `kristal_state` keeps its v6 canonicalization and state hash exactly as defined by v6. Kristall stores that identity as an input reference.

## Kristall semantic IDs

Within a declared `namespace_id`, Kristall allocates:

```text
KQ… entity/item
KP… property/relation
KA… assertion
KS… source
```

The numbers are opaque. They MUST NOT encode taxonomy or domain meaning and MUST NOT be recycled.

A bare ID is namespace-scoped. Federation uses `(namespace_id, semantic_id)` or an equivalent URI.

See [Semantic Identity](Semantic-Identity.md).

## Meta-artifact canonicalization

The initial v7 meta profile is:

```text
kristal.v7:jcs-rfc8785
```

For v7 meta-artifacts, implementations SHOULD canonicalize the artifact after excluding `content_hash` and `signatures` when those fields identify/sign the artifact itself. A future final v7 contract may freeze artifact-specific hash boundaries more narrowly; implementations MUST version any deviation.

## Logical ID vs content identity

A stable logical semantic ID is not a content hash. Changing labels, descriptions or accepted classifications does not change the identity. Structural changes SHOULD produce version/supersession records when semantically relevant.

## Deterministic projections

A projection is reproducible only when its declared inputs are stable: source snapshot identities, Kristall namespace/snapshot, subject selector, axes, context, policies and transform version.
