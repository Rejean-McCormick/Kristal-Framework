# Workflows

Kristal v6 workflows preserve canonical state while allowing validation, recognition, projection and operational routing to evolve independently.

A common lifecycle is:

```text
source / observation / rule / human or AI work
        ↓
Kristal State
        ↓
validation / recognition / correction / supersession
        ↓
updated or successor Kristal State
        ↓
reader/query/projection
        ↓
optional actionability routing
        ↓
explicit operational owner contract
```

## Key rule

Compilation, validation, recognition, visibility, actionability and execution are different transitions.

A state can exist before validation. A validated assertion may still require human decision. An automatically actionable item still requires the target system's admission/authority.

## Main workflows

- [Workflow-Build-and-Validate](Workflow-Build-and-Validate.md)
- [Workflow-Publish-and-Distribute](Workflow-Publish-and-Distribute.md)
- [Workflow-Activate-Rollback-Downgrade](Workflow-Activate-Rollback-Downgrade.md)
- [Workflow-Subsets-Recipes](Workflow-Subsets-Recipes.md)
- [Workflow-Federation-and-Curation](Workflow-Federation-and-Curation.md)
