# Federation, pagination and continuations

## Federation

A logical Kristall MAY span many shards and operators. Federated query MUST preserve:

- semantic identity namespace;
- source/shard provenance;
- snapshot or source fingerprints;
- unresolved/missing shard state;
- parent budget accounting.

A timeout or unavailable shard yields `partial` unless the query's policy requires fail-closed behavior.

## Pagination

v8 reuses the v6 principle that pagination must not change semantic ordering. Every paginated operation MUST declare or derive a stable ordering key.

A cursor is opaque client state. It SHOULD encode or bind to:

- normalized query fingerprint;
- source snapshot/fingerprint set;
- ordering profile;
- last emitted position;
- expiry or validity policy where applicable.

## Continuation safety

A continuation MUST fail rather than silently resume against incompatible source state if the query contract requires snapshot consistency.

## Streaming

Implementations MAY stream pages or atoms. Streaming transport is non-normative, but each emitted unit MUST remain attributable to the same query and source state. A stream ending early MUST produce an explicit partial/termination condition when the transport supports it.

## Unknown outcome

If a federated subquery's completion state cannot be determined, the coordinator MUST record the uncertainty rather than infer success or absence.
