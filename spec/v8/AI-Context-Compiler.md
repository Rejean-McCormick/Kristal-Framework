# AI Context Compiler

The AI Context Compiler transforms an exact KQP result into a compact `kristall_ai_context_bundle`.

## Semantic atoms

The compiler SHOULD select **semantic atoms** instead of filling independent arrays until a budget is exhausted. An atom contains enough material to interpret one useful semantic unit, such as:

- assertion + subject/predicate/object references + provenance;
- structural edge + endpoint identities + relation identity;
- evidence reference + digest + source/trust metadata;
- entity/property card needed to resolve referenced IDs.

This reduces the risk of including a claim while dropping the identity/provenance needed to interpret it.

## Selection

Selection MAY consider:

- explicit roots and required connectors;
- query intent;
- graph distance;
- property relevance;
- evidence/epistemic status;
- source authority scope;
- trust class;
- byte/token budget.

The compiler MUST preserve the distinction between selected and omitted material.

## Budget model

`max_bytes` is the portable hard payload budget. `max_tokens` is optional and meaningful only with a declared `tokenizer_id`. An implementation MAY estimate tokens, but the estimate MUST identify its tokenizer/profile or state that it is heuristic.

## Completeness

The bundle MUST carry forward query completeness and record additional compiler truncation. It SHOULD state whether semantic closure and evidence closure are `complete`, `partial`, `not_requested` or `unknown`.

## Provenance and trust class

Context originating from sources, external KOS, retrieved documents or tools retains provenance and trust classification. Retrieved text can inform reasoning; it cannot become system policy or execution authority merely because it is included in the context bundle.

## Language

Compilation operates on semantic IDs first. Lexical resolution is a final representation layer. Missing lexicalization preserves the semantic ID rather than causing model-generated translation inside the canonical bundle.

## RAG boundary

Vector/text retrieval is useful for discovery and uncrystallized source material. It does not replace exact Kristal traversal once semantic identities are known.
