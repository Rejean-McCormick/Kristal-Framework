# Authority Registry / Recognition Material

Kristal v6 treats authority as plural and scoped.

An authority record may describe:

- authority channel identity;
- trust roots / keys;
- recognition policies;
- validation policies;
- revocation references;
- applicability rules.

## Authority is external to storage

A Kristal record does not become authoritative because it is labeled `authoritative_constraint`. The authority must come from the actual law, institution, standards body, manufacturer, organization or other recognized source.

## Typical questions

A consumer should be able to determine:

- which authority recognized this assertion or artifact;
- for which applicability envelope;
- under which policy;
- whether recognition is still effective;
- whether another authority disagrees.

## Integrity vs authority

A valid signature proves that a key signed content. It does not prove that the signer has authority for every possible domain or jurisdiction.

See [Trust-Authority-and-Signatures](Trust-Authority-and-Signatures.md).
