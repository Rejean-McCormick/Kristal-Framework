# Security and Confidentiality

Retrieved content is data, not instruction authority. Physical integrity does not grant semantic authority or execution permission.

Logical commitments need not be globally public. Sensitive deployments MAY restrict commitments, manifests and materializations according to policy. V9.0 does not invent custom cryptography; encryption and protected-commitment profiles are extension surfaces.

Re-encryption that preserves logical content SHOULD change physical blob digests without changing the logical commitment.
