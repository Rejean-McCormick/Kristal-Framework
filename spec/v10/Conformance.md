# Kristal v10 Conformance

V10 conformance is profile-based.

## `V10-Node-Reader`

MUST read and validate `kristal_node_manifest`, `kristal_host_binding`, `kristal_publication` and `kristal_directory` core structures.

## `V10-Publisher`

MUST preserve v9 publication semantics, publish exact state commitments, and emit or retain a `kristal_publication` record.

## `V10-Directory`

MUST distinguish discovery from semantic federation and MUST NOT treat directory omission as semantic negation.

## `V10-GitHub-Host`

MUST satisfy `V10-Node-Reader` and the `kristal.host/github/1.0` binding profile. Plan-dependent GitHub features MAY be reported as unavailable capabilities.

## `V10-Full`

MUST satisfy `V9-Full`, `V10-Node-Reader`, `V10-Publisher`, and `V10-Directory`. Support for the GitHub host profile is optional for generic `V10-Full` conformance.


## Validation result requirements (draft.2)

Reference validators distinguish structural/type failures from unsupported profiles, digest mismatches and relation mismatches with stable issue codes. Malformed input MUST return a failed validation result rather than an uncaught exception for ordinary document errors. An unsupported commitment/profile MAY be transported opaquely, but MUST NOT be reported as verified.

`V10-Publisher` additionally requires byte size and blob digest for each resource in the verifiable baseline and MUST detect a mismatched remote bundle before treating a retry as idempotent.
