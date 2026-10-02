# Operations

Operating Kristal v6 means protecting semantic meaning as carefully as byte integrity.

Monitor:

- content-hash / signature failures;
- unsupported schema/standard versions;
- valuation dimension/value-semantics mismatches;
- invalid value-state combinations;
- missing provenance/evidence;
- applicability drift;
- reader/view-policy filtering;
- validation/recognition conflicts;
- actionability changes;
- projection/source mismatch.

## Operational invariant

An automated consumer should fail closed when it cannot interpret a required valuation, role or actionability policy safely.

## Do not centralize operational ownership

Kristal may capture state from applications, but applications retain ownership of their mutable operational data unless an explicit architecture says otherwise.
