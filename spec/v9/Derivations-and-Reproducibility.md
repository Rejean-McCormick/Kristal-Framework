# Derivations and Reproducibility

A `kristal_derivation` declares transform identity/version, exact logical inputs, parameters, toolchain context, outputs, and a determinism claim.

A deterministic build MUST NOT depend on unpinned mutable external state. All inputs that can affect the result MUST be declared or eliminated.

Implementations MAY perform change pruning when recomputation yields the same logical commitment.
