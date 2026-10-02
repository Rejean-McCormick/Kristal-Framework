# Quickstart

A minimal conceptual v6 assertion might look like:

```json
{
  "statement": {
    "subject": {"kind": "item", "id": "urn:asset:pump-17"},
    "predicate": "maintenance.indicates_inspection",
    "object": {"kind": "item", "id": "urn:inspection:bearing"}
  },
  "assertion_status": "sourced",
  "record_role": "derived_state",
  "coordinates": [
    {"axis": "operating_condition", "value": "high_vibration"}
  ],
  "applicability": {
    "domain": "operations",
    "subdomain": "maintenance"
  },
  "valuations": [
    {
      "dimension": "intervention_necessity",
      "value_semantics": "ordinal",
      "value_state": "known",
      "value": "high"
    }
  ],
  "actionability": {
    "mode": "human_review",
    "requires_human_validation": true
  },
  "evidence_refs": ["urn:sensor:vibration:event-834"]
}
```

The important point is the separation:

- the observation/evidence is not the decision;
- `high` is high **intervention necessity**, not universal truth;
- `human_review` is a routing boundary, not a measurement;
- the artifact does not itself execute the inspection.

## Next steps

- [Valuations-and-Value-Semantics](Valuations-and-Value-Semantics.md)
- [Coordinates-and-Applicability](Coordinates-and-Applicability.md)
- [Record-Roles](Record-Roles.md)
- [Actionability-and-Human-Boundaries](Actionability-and-Human-Boundaries.md)
- [Identity-and-Determinism](Identity-and-Determinism.md)
