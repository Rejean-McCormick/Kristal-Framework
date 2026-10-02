# Workflow: Activate, Roll Back, Downgrade

Activation in v6 normally selects which state/projection/policy version a consumer uses. It does not change the canonical historical record.

## Activation inputs

An activation decision may consider:

- source state/content hash;
- artifact lifecycle status;
- validation/recognition references;
- reader/view policy;
- environment/tenant applicability;
- projection compatibility;
- operational owner policy.

## Rollback

Rollback should select a previously known artifact/projection version. Do not rewrite the newer state to pretend it never existed.

## Actionability

Changing an active knowledge artifact may change which actions are considered automatic or human-gated. Operational systems must still apply their own versioned admission/authority policy before executing changes.

## Legacy Runtime Packs

Existing Runtime Pack consumers may still use them as activation targets. In v6 they should be treated as derived materializations tied to canonical source state(s).
