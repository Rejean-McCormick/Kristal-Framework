# Polymorphic workloads

## 1. Why reference workloads matter

V9 is intentionally polymorphic. The architecture must therefore be tested against different knowledge shapes rather than optimized around a single benchmark.

The workloads in this document are design probes. Existing implementations may be corrected or migrated; they are not treated as untouchable constraints.

## 2. Pokémon — large homogeneous relation sets

### Native pressure

The Pokémon corpus exposes hundreds of thousands of independently meaningful claims, especially learnset and encounter relations.

The expanded portable representation repeats large amounts of identical epistemic envelope and long identifiers.

### V9 lesson

The logical claims remain individually addressable, but a physical materialization can factorize:

```text
shared predicate
shared epistemic envelope
shared coordinate schema
local identifier dictionaries
segment metadata
```

Only member-specific values need to repeat physically.

### Conformance requirement

A compact representation must reconstruct the same claims, provenance, valuations, applicability and identity expected by the logical contract or declared v6 projection.

## 3. Kristal-Recipes — procedural DAG

### Native shape

The domain separates:

```text
RecipeFamily
RecipeVariant
RecipeSourceInstance
PreparationEvent
```

A `RecipeVariant` owns a procedural DAG of ingredients, operations, intermediate states and outputs.

### V9 lesson

The procedure graph is the domain-native canon. It must not be replaced by an assertion list simply because a portable v6 projection exists.

```text
DOMAIN-NATIVE CANON != PORTABLE PROJECTION
```

Derived classification indexes and fingerprints remain runtime/read-side material.

## 4. Kristal-VehiculeDiag — conditional multiplex graph

### Native shape

The model separates:

- component identity;
- ports;
- typed connections;
- operating-state conditions;
- functional paths;
- failure modes;
- test points and observability.

The graph can carry parallel power/control paths and conditional transfers.

### V9 lesson

The graph is close to an executable diagnostic model. Flattening it into generic triples would make sequencing, convergence and operating conditions harder to preserve.

Convenience structures such as `*_by_id` should be derived indexes when they are rebuildable from canonical collections.

## 5. Kristal-Pi-Theory — small layered epistemic corpus

### Native shape

The corpus distinguishes layers such as:

```text
mechanical
structural
ontological
epistemic
resonance
historical
validation
```

and explicitly separates comparative resonance from evidence.

### V9 lesson

Small artifacts should remain inline and readable. V9 must not impose segmentation or storage machinery whose overhead exceeds the corpus itself.

Physical factorization must never merge epistemic distinctions merely because fields look similar.

## 6. Kristal-HospitalOps — security-separated authority planes

### Native shape

The architecture separates:

```text
Clinical Commons
Clinical Practice
Clinician Identity Vault
Patient Identity Vault
Security Audit
source clinical systems
```

### V9 lesson

Polymorphism includes authority and confidentiality, not only data structure.

A composed state must not imply shared decryption keys, shared ownership or authority merger.

The architecture must support references to protected logical artifacts whose physical representation and commitment visibility are restricted.

## 7. UCKK — hierarchical federation

### Native shape

The hierarchy reserves:

```text
1 university Kristal
10 voie Kristals
100 course Kristals
```

Parents own topology and reference children without copying child semantic content.

### V9 lesson

A semantic shard is a lifecycle/ownership boundary, not a physical segment.

Federation should pin child commitments and retain independent child states.

Derived glossary/navigation indexes do not become a second canon.

## 8. MathKristal — multiple formal authorities and graphs

### Native shape

The architecture separates responsibilities among:

```text
MathKristal epistemic state
MMT theory graph
OpenMath semantic objects
Formula IR
Representation Graph
Proof adapters
Action Graph
language realization systems
```

The Action Graph is explicitly derived rather than canonical proof authority.

### V9 lesson

A state can contain several logical contracts with different authorities.

A Formula AST must preserve binding/order. A Representation Graph is not a Proof Graph. A derived navigation/action graph is not evidence of theorem validity.

## 9. Kristal-kOA-Ecosystem — heterogeneous ecosystem graph

### Native shape

The model distinguishes components, functions, capabilities, needs, utilities, workflows, scenarios, repositories, artifacts, contracts and authorities.

It already maintains invariants such as:

```text
scenario != deployment
repository != authority
hosting != ownership
projection != canon
```

### V9 lesson

Heterogeneous property graphs require strong anti-corruption boundaries. Discovery/evidence layers may support promotion decisions without automatically becoming canonical components.

## 10. Acceptance rule

A proposed v9 core feature should answer:

1. Does it preserve each workload's native logical shape?
2. Does it preserve independent authority boundaries?
3. Does it allow a small workload to remain simple?
4. Does it allow a massive workload to avoid monolithic amplification?
5. Can derived indexes be discarded without destroying canon?
6. Can two physical materializations preserve the same logical commitment?

If the answer is no for one class, the feature probably belongs in a profile rather than the core.
