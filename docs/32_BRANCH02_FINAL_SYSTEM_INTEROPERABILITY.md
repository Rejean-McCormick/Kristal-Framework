# Branch 02 — final-system semantic interoperability

**State:** local-source compatibility evidence, **not** ratification of a final Framework v11 standard or a deployed integration.

## Authority

Kristal Framework 11.0.0-draft.4 owns namespace-scoped KQ/KP/KA/KS semantic identity, graph structure, conformance and lexical separation. It does not approve crosswalks by word similarity, mutate consumer workspaces, operate diK dictionaries or authorize publication. Historical compatibility locks and v11 schemas/TCK remain unchanged in this work package.

## Verified local source interfaces

- The supplied Kit 4.0.0-draft.4 declares `kristal-integration-framework-pin/v11.0-draft.4` and hashes 13 Framework source files. Run `python tools/v11/check_consumer_pin.py --consumer-pin <kit>/contracts/v11-framework-pin.json` for a **read-only** independent check against this Framework checkout. A changed hash, unsupported version or missing file is rejected.
- diK alpha.7 includes vendored copies of **11 v11 JSON schemas** originating in the Framework draft.3 contract. The supplied draft.4 schemas are byte-identical to these 11 copies. **Schema parity does not prove runtime or version-wide interchangeability**. diK's own read-only checker can compare the selected sources.
- Authoring Kit's optional `scripts/check_branch02_interop.py` exercises a real pinned Kit/Framework *fixture* and records that the Framework reference and Kit coverage reports match, with no canonical changes.
- Arketype design metadata is not a namespace or identity authority. Its new external Kit option is explicitly selected, and leaves the 19 historical templates in place.
- Kristalizer's explicit Kit dependency can be inspected with `kit-status --framework PATH`, refusing unapproved versions and mismatched pin bytes.
- SenTient produces **unreviewed external Q/P candidates**, not Framework semantic identities or an `accepted exactMatch` decision.

## Implementation and acceptance requirements

1. Pin an exact Framework version *and* the 13 corresponding source file digests before authoring/reading v11 graph data.
2. Require independent producer/consumer fixtures for graph, registry, crosswalk, dictionary catalog and literal handling; include invalid namespace, unapproved Q/P match, missing/fallback lexical coverage and changed digest cases.
3. Treat every import plan, candidate lexical catalog and structure template as noncanonical until the authorized Kit workspace accepts it by a distinct reviewed transaction.
4. Do not promote the draft.3-to-draft.4 byte parity result to full v11 TCK, actual dictionary import verification or permission to publish a Kristal.
5. Future Framework revisions require a separately approved compatibility decision; do not edit frozen v11 schemas/TCK to satisfy application tests.

**Proof command for this snapshot:**

```bash
python tools/v11/check_consumer_pin.py --consumer-pin ../Authoring-Kit/contracts/v11-framework-pin.json
python tools/validate_all.py
```

A local source-tree path must be adapted to the actual user's checkouts; the commands do not contact GitHub. See the accompanying Branch02 `HANDOFF.md` for consumed schemas, proof limits and open owner decisions.
