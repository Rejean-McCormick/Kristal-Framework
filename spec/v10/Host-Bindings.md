# Host Bindings

A `kristal_host_binding` maps one Kristal node to a concrete hosting substrate.

The generic binding records:

- stable `binding_id`;
- `node_id`;
- host profile identifier/version;
- account scope;
- the primary host resource;
- optional surfaces for source, publication, materialization, activation, automation, attestation and discovery.

Bindings MUST NOT contain passwords, access tokens, private keys or other reusable credentials.

Bindings are replaceable. A node can have multiple bindings at once, for example a GitHub primary, an OCI mirror and an offline archive.

```text
HOST BINDING != LOGICAL STATE
MIRROR != LOGICAL REVISION
```
