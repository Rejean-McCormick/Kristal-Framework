# Query model

v7 queries can address either source truth or a projection.

## Source query

Retrieves assertions from explicitly selected Kristal states without Kristall synthesis.

## Mesh query

Traverses entities, assertion families and structural edges. A path result is not a factual assertion.

## Surface query

Adds a subject and orientation:

```text
subject + primary_axis + secondary_axis? + filters → Surface
```

## Projection query

Materializes a Surface into a v6-compatible Kristal state under a declared recipe.

Consumers SHOULD expose which mode produced an answer.
