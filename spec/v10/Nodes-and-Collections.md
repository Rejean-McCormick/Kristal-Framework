# Nodes and Collections

A **Kristal node** is a discoverable operational endpoint capable of exposing one or more Kristal states and related services. A node is identified by `node_id` and described by `kristal_node_manifest`.

A node MAY play one or more roles:

- `collection` — hosts one or more related Kristal states;
- `directory` — advertises other nodes and host bindings;
- `publisher` — publishes immutable state representations;
- `gateway` — exposes query/read services without owning the underlying semantic state.

A collection boundary is operational and organizational. It does not force all contained knowledge into one logical artifact or one authority domain.

Large deployments SHOULD use multiple collection nodes when ownership, confidentiality, lifecycle, cost, or domain boundaries differ.
