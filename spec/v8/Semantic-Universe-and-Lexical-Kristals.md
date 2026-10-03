# Semantic universe and lexical Kristals

## Language-neutral semantic universe

v8 does not create a second semantic identity system. The semantic universe is built from the existing v7 identity model (`KQ`, `KP`, `KA`, `KS`), v6-compatible referent mappings and declared external KOS crosswalks.

A large deployment MAY federate and shard the universe by subject without changing semantic identity:

```text
semantic universe
├── core
├── mathematics
├── physics
├── chemistry
├── biology
│   ├── botany
│   └── zoology
├── medicine
├── law
└── engineering
```

External systems such as Wikidata, UNESCO vocabularies, MeSH, GBIF or GeoNames MAY supply mappings, labels and evidence. Their identifiers remain external mappings unless explicitly represented as Kristall semantic identities under the v7 rules.

## Domain ownership with global contracts

A federated deployment MAY assign stewardship of specialist shards to domain communities. Local stewardship does not weaken global invariants. Identity syntax, provenance, compatibility, fingerprint profiles and query semantics remain governed by the shared Kristal contracts.

## Orthogonal lexical universe

Lexical Kristals form an independent composable layer:

```text
fr
├── core
├── science
├── chemistry
├── science-college
├── botany
└── botany-north-america

en
├── core
└── ...
```

Semantic and lexical partitioning are orthogonal. A chemistry semantic shard can be rendered through French, English or another lexical stack without altering the chemistry Kristal.

## Companion pattern

A project MAY publish a lexical companion next to a semantic Kristal, but the companion remains a separate artifact:

```text
chemistry-course.kristal
chemistry-course.fr.lexicon.kristal
chemistry-course.es.lexicon.kristal
```

A project-specific lexical companion SHOULD contain only the delta not already covered by the user's base/domain stacks.

## Coverage generation

A lexical-delta generator:

1. enumerates semantic references used by a target Kristal;
2. resolves them through the selected lexicon stack;
3. emits unresolved references as `lexical_status: missing`;
4. never invents a lexical value.
