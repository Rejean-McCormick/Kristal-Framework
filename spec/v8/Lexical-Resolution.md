# Lexical resolution

A `kristall_lexicon_stack` declares deterministic lexical precedence.

## Resolution algorithm

For a requested semantic reference and locale:

1. validate the requested locale and stack policy;
2. select lexicons compatible with the requested locale or explicitly permitted fallback chain;
3. discard entries whose `lexical_status` is not `resolved`;
4. choose the matching entry with highest declared precedence;
5. if equal-precedence entries disagree, return a conflict rather than silently choosing;
6. if no entry resolves, return the semantic reference with `lexical_status: missing`.

Locale fallback such as `fr-CA → fr` is allowed only when declared by stack policy. Fallback does not establish semantic equivalence.

## Precedence

Precedence is an explicit rendering rule, not authority. A project lexicon may override a preferred display term without overriding the semantic concept it references.

A recommended stack order is:

```text
base language < general domain < specialist domain < education/region < project delta
```

## Generated lexical delta

A lexical-delta generator may compare semantic references used by a Kristal with an existing stack and emit only unresolved references. Generated deltas MUST preserve semantic IDs and MUST NOT generate canonical translations from a language model without an explicit external curation/admission step.

## Conflict visibility

Lexical disagreement is data. Resolvers MUST expose conflicting candidates and their lexicon provenance rather than collapse them silently.
