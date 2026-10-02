# Operations: Release Strategy

A Kristal v6 release strategy controls how canonical states, policies, validation/recognition material and derived projections move through environments.

## Release units

A release may include:

- one or more `kristal_state` artifacts;
- validation / recognition records;
- Referent Registry changes;
- reader/view policies;
- authority/trust material;
- derived indexes/query stores/runtime projections;
- compatibility adapters for legacy Exchange/Runtime Pack consumers.

## Release stages

Common stages:

1. build canonical state;
2. validate structure and declared policies;
3. recognize under authority channels when applicable;
4. publish content-addressed artifacts;
5. derive consumer projections;
6. verify projection/source linkage;
7. activate consumer version;
8. monitor semantic + operational behavior;
9. rollback the active pointer when necessary.

## Activation scope

Activation may be scoped by:

- tenant;
- environment;
- region/jurisdiction;
- service;
- authority channel;
- reader/view policy;
- source state hash;
- projection profile/version.

## Canary strategy

Validate:

- hash/signature verification;
- query behavior;
- valuation/value-state preservation;
- role/actionability preservation;
- reader policy enforcement;
- no accidental promotion of `automatic` to authority;
- rollback readiness.

## Rollback

Keep prior known-good states/projections available and verifiable. Rollback selects an older active target; it does not erase later canonical history.

## Related pages

- [Workflow-Publish-and-Distribute](Workflow-Publish-and-Distribute.md)
- [Workflow-Activate-Rollback-Downgrade](Workflow-Activate-Rollback-Downgrade.md)
- [Operations-Compatibility](Operations-Compatibility.md)
