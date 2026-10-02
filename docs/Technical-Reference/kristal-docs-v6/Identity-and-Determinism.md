# Identity & Determinism

Kristal v6 remains deterministic and content-addressable.

The semantic upgrade does not change the basic integrity rule: equivalent canonical content must produce stable bytes under the declared canonicalization profile and therefore stable hashes/identifiers.

## Canonicalization

The active v6 profile is:

```text
kristal.v6:jcs-rfc8785
```

Canonicalization is a technical hashing/signature process. It is **not** the act of declaring an assertion canonical, authoritative or true.

## Hash target

Identity calculations must follow the active contract's explicit content boundary. Identity fields, computed content hashes and signatures are normally excluded from the content they themselves identify.

Do not invent a local exclusion list in each consumer.

## Deterministic projections

A derived projection should declare its source state(s), transform/configuration and relevant policy inputs. If those inputs are identical, the derived output should be reproducible where the projection contract promises determinism.

## Mutation

When canonical content changes, recompute affected identifiers and signatures. Do not preserve old hashes across semantic mutation.

## Identity is not authority

A perfectly reproducible hash proves content identity. It does not prove factual correctness, validation or authority recognition.
