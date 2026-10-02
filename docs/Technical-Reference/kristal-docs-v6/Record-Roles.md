# Record Roles

`record_role` identifies the functional role of an assertion or record in a Kristal State.

This is essential when one artifact contains different kinds of information that must not be confused.

## Common roles

### authoritative_constraint

External rule or constraint whose authority comes from a source outside Kristal: law, regulation, official procedure, standard, manufacturer requirement.

The role does **not** make it authoritative by itself. Provenance and authority recognition must point to the actual authority.

### observed_state

Neutral observation or captured state: a document arrived, a value was measured, a symptom occurred, a status changed.

### organizational_rule

Rule, threshold or policy chosen by the organization: escalation condition, preferred diagnostic sequence, internal definition of “ready”.

### reference_knowledge

Reusable descriptive/domain knowledge.

### derived_state

Machine- or rule-derived conclusion built from other assertions.

### decision

Recorded choice or adjudication, ideally with actor/policy/provenance.

### action

Action candidate, instruction or completed action representation.

### structural_record

Identity/navigation/structural material for which domain valuations may be `not_applicable`.

## Role is not ownership

An application can export an `observed_state` into Kristal without giving Kristal ownership of its operational database. Likewise, a law represented as `authoritative_constraint` remains authoritative because of its legal source, not because Kristal stored it.
