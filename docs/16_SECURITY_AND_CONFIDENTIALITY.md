# Security and confidentiality

## 1. Security posture

V9 increases composability and remote/partial materialization possibilities. It must therefore preserve strict boundaries between data retrieval, integrity checking, authorization and authority.

## 2. Threat categories

The architecture should distinguish at least:

- accidental corruption;
- incomplete writes/crashes;
- concurrent publishers;
- malicious or compromised remote storage;
- unauthorized readers;
- unauthorized publishers/activators;
- epistemically untrusted sources.

Different controls address different threats.

## 3. Digest limits

A blob digest can detect byte changes.

A logical commitment can detect logical reconstruction changes under a profile.

Neither grants read permission or proves factual correctness.

## 4. Confidential logical artifacts

Not every logical commitment should automatically be globally public.

For sensitive data, deterministic public hashes can reveal equality and, for low-entropy inputs, may aid dictionary attacks.

Therefore v9 should allow security profiles where commitment visibility is restricted or where a protected commitment mechanism is used.

V9.0 should not invent new cryptography. It should make the commitment mechanism profile-driven so qualified schemes can be introduced safely.

## 5. Encryption boundary

A physical representation may be encrypted independently from logical content.

Changing:

```text
key
nonce
ciphertext envelope
storage system
```

can change the blob digest without changing logical content.

This enables key rotation and secure repack without semantic mutation.

## 6. Hospital-style compartmentalization

Sensitive operational domains may require separate artifacts/states and key domains for:

```text
shareable knowledge
practice facts
clinician identity
patient identity
security audit
```

V9 state composition must not require co-location or shared decryption authority.

## 7. Access control

A reader's ability to discover that an artifact exists does not necessarily imply permission to retrieve or decrypt it.

Resolvers and runtime systems may return states such as:

```text
available
authorization-required
intentionally-redacted
not-local
unknown
```

without fabricating semantic conclusions.

## 8. Activation authority

The right to upload a blob is not the right to publish a State Snapshot.

The right to publish a snapshot is not automatically the right to activate it in production.

```text
STORE WRITE != PUBLISH AUTHORITY != ACTIVATE AUTHORITY
```

Deployments should separate these privileges when risk warrants it.

## 9. Signatures

Signatures should bind clearly defined objects, for example:

- state snapshot bytes;
- release manifest;
- activation record;
- build receipt.

The signed boundary must be explicit. A signature over one representation must not be interpreted as a signature over every logically equivalent representation unless the signature scheme explicitly signs the logical commitment instead.

## 10. Remote content

Retrieved manifests and blobs are untrusted input until validated.

Parsers must apply normal resource limits and schema/profile validation before content is admitted into a runtime or publication pipeline.

```text
RETRIEVED CONTENT != INSTRUCTION AUTHORITY
```
