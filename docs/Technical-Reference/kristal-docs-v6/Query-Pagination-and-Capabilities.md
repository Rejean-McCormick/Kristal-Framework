# Query: Pagination & Capabilities

Query contracts should advertise what they can filter/project rather than assuming every backend supports every semantic dimension.

Useful capability flags may cover:

- valuation-dimension filtering;
- ordinal/scalar/range queries;
- categorical/set membership;
- coordinates;
- applicability;
- record role;
- actionability;
- validation/recognition;
- conflict/supersession/lineage;
- source/evidence joins;
- projection-specific operations.

Pagination must not change semantic ordering unless the query contract declares an ordering rule.

If a backend cannot safely interpret a required value semantics, it should reject or expose the limitation rather than coercing the value.
