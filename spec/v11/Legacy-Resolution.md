# Non-destructive legacy resolution

Use the input request contract `kristal_legacy_resolution_requests` to list **specific source paths whose values serve as semantic identifiers**. Do not blindly scan and rewrite all strings in a committed Kristal. The v11 proof-of-concept tool:

```sh
python tools/v11/resolve_legacy.py \
  --requests examples/v11/legacy-resolution-requests.example.json \
  --lexicon examples/v11/lexicon-fr.example.json \
  --lexicon examples/v11/lexicon-en.example.json \
  --crosswalk examples/v11/external-crosswalk.example.json
```

It emits a report: `resolved` means a **unique deterministic dictionary/exact accepted crosswalk candidate**, not independently proven semantic equivalence to the original text; `ambiguous` lists all candidates, and `unresolved` creates no identity. Proposals require a separate admitted migration decision before modifying source files. Unreviewed lexical resolution MUST NOT be taken as a canonical rewrite approval.

A migration pipeline SHALL:

1. inventory identities and predicates in legacy graphs while excluding natural-language values, citations and source text;
2. reconcile known registry IDs, then external IDs via **accepted exact** crosswalk records, then search the lexical candidates;
3. review ambiguities, version decisions and provenance, and mint any justified missing KQ/KP in a namespace registry;
4. emit a new v11 graph revision and a report of unresolved references;
5. preserve original bytes, v9 commitments, source paths and reversal/audit history.

A missing Wikidata dump changes candidate coverage, not the validity of an existing local identity. This version does not implement automatic Wikidata dump ingestion or cross-repository migration. Those belong in the Authoring Kit's producer tooling and require integration tests.

## Addendum draft.3 — revue par diK

A specialized dictionary application MAY emit `kristal_dik_conversion_plan`, a non-executable manifest of exact JSON Pointer source paths, original values, target KQ/KP IDs and per-operation review decisions. The Framework supplies a read-only plan/schema/digest validator, **not** an automatic rewriting command. Only a producer implementing explicit identity-role checks, all-approved decisions, new logical revision creation and source-commitment preservation can apply a reviewed plan. See [diK interoperability](diK-Interoperability.md).
