# Deduplication and factorization

v7 replaces destructive deduplication with **factorization**.

## Four cases

### Exact duplicate

Equivalent normalized assertion with equivalent scope. The system may share one canonical representation while preserving every source member.

### Semantic equivalent

Different wording appears to express the same proposition. Preserve a family and require a traceable equivalence decision.

### Variant / specialization

Assertions overlap but differ by scope, precision, applicability or granularity. They MUST NOT be flattened into one statement.

### Conflict

Assertions are incompatible under overlapping applicability. Preserve both and record conflict.

## Duplication as geometric evidence

If two Kristals repeat a large common concept set but systematically organize the concepts with different relation families, the duplication may reveal an orientation axis.

Therefore:

> factorize common structure only after comparing how that structure is used.

## Compression objective

A mature Kristall SHOULD reduce redundant representation while preserving reconstructability, provenance, exceptions and disagreement.

Compression is useful only when information is not lost silently.
