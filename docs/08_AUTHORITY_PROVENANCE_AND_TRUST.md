# Authority, provenance and trust

## 1. Purpose

V9 increases the number of derived artifacts and physical representations in a deployment. That makes existing Kristal trust boundaries more important, not less.

No physical optimization may blur the distinction between:

```text
integrity
authenticity
authority
validation
factual correctness
```

## 2. Integrity

A blob digest can establish that retrieved bytes match referenced bytes.

A logical commitment can establish that reconstructed logical content matches a named commitment profile.

Neither statement proves the truth of a claim.

```text
HASH IDENTITY != FACTUAL AUTHORITY
```

## 3. Authenticity

A signature can prove that a holder of a cryptographic key signed a defined payload.

Authenticity does not automatically establish domain authority.

Key governance and authority recognition remain separate policies.

## 4. Epistemic provenance

Epistemic provenance supports interpretation of knowledge.

It can answer questions such as:

- where did a claim originate?
- which evidence supports it?
- which authority recognized it?
- under what applicability and valuation does it hold?
- which conflicts or supersession relationships apply?

This provenance can be part of the logical artifact when it changes the knowledge state.

## 5. Build provenance

Build provenance describes the computational production path.

Examples:

```text
source snapshot digest
transform identifier/version
configuration
schema versions
toolchain
parameters
```

A builder can transform a medical or mathematical artifact without becoming an authority over medicine or mathematics.

```text
EPISTEMIC PROVENANCE != BUILD PROVENANCE
```

## 6. Publication provenance

A deployment may separately record:

- who published a snapshot;
- which release process qualified it;
- what signatures attest the release;
- what activation decision selected it.

Those records are operational governance and should not be silently folded into the knowledge itself.

## 7. Authority preservation during composition

A state may reference artifacts governed by separate authorities.

For example, a hospital deployment may combine:

```text
Clinical Commons
Clinical Practice
Clinician Identity Vault
Patient Identity Vault
Security Audit
source clinical systems
```

The composition must preserve those boundaries.

```text
STATE COMPOSITION != AUTHORITY MERGE
REFERENCE != OWNERSHIP TRANSFER
```

## 8. External KOS and external systems

Existing v8 principles remain unchanged:

```text
EXTERNAL KOS != KRISTALL IDENTITY
RETRIEVED CONTENT != INSTRUCTION AUTHORITY
```

V9 physical resolvers must therefore treat retrieved blobs as data. A downloaded manifest cannot grant itself mutation or activation privileges.

## 9. Derived models

Derived artifacts such as:

```text
query index
Action Graph
posterior diagnostic ranking
AI context bundle
search/vector index
```

must not become epistemic authority merely because they are efficient or heavily used.

Their lineage must point back to the logical states they represent.
