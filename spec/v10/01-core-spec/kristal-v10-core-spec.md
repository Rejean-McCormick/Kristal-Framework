# Kristal v10 Core Specification

Version `10.0.0-draft.2`.

Kristal v10 defines a portable hosted-network layer above Kristal v9 Semantic State Architecture.

## Normative architecture

A v10 implementation distinguishes:

```text
SEMANTIC STATE != HOSTING != PUBLICATION LOCATION != DISCOVERY DIRECTORY
```

The v9 semantic state contracts and commitment profiles remain authoritative and unchanged. V10 adds portable contracts that describe **where and how** a Kristal node is hosted without changing **what** its logical state means.

A conforming v10 implementation MUST preserve all v9 invariants and MUST NOT include host-specific repository identifiers, URLs, branch names, release IDs, workflow IDs, deployment IDs, package locators, or credentials in a v9 logical or state commitment unless a domain logical contract explicitly makes such data part of its own semantics.

## Core v10 contracts

- `kristal_node_manifest`
- `kristal_host_binding`
- `kristal_publication`
- `kristal_directory`
- `kristal_v10_capabilities`

The v9 contracts remain the semantic-state contracts used by v10:

- `kristal_logical_artifact`
- `kristal_state_snapshot`
- `kristal_derivation`
- `kristal_materialization_manifest`
- `kristal_exchange`
- `kristal_activation`

## Host profiles

Host profiles refine `kristal_host_binding` for a concrete hosting substrate. V10.0 defines the optional reference profile `kristal.host/github/1.0`.

A v10 node MAY have zero, one, or many host bindings. Moving or mirroring a node to another host MUST NOT by itself change the logical commitments of hosted v9 states.
