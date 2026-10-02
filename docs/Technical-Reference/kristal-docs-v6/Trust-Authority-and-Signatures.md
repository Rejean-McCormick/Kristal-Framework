# Trust, Authority & Signatures

Kristal v6 keeps integrity, validation and authority separate.

## Integrity

Integrity asks:

- do canonical bytes hash to the declared digest?
- does a signature verify?
- is the signature over the correct content boundary?
- is a key trusted for this technical purpose?

## Validation

Validation asks whether an assertion/artifact satisfies a declared evaluation policy.

## Authority recognition

Recognition asks whether an authority channel accepts or recognizes an assertion/artifact for a declared applicability envelope.

## Record role does not manufacture authority

Setting:

```text
record_role = authoritative_constraint
```

does not make a statement official. The evidence/provenance/authority chain must point to the real institution, law, standard or official procedure.

## Actionability does not manufacture authority either

`actionability = automatic` means no human judgment is required under the represented policy. It does not grant a key, process or application permission to execute a cross-system mutation.
