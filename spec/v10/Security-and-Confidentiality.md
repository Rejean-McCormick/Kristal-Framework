# Security and Confidentiality

V10 introduces host metadata and therefore adds disclosure and execution boundaries that are separate from semantic confidentiality.

Requirements:

1. Host bindings MUST NOT embed reusable credentials.
2. Public directories and public profile text MUST NOT enumerate private node locations by default.
3. A host visibility flag is not a cryptographic confidentiality guarantee.
4. Public mirrors of a private state require an explicit policy decision.
5. Host attestations and workflow identity MUST NOT be confused with epistemic authority.
6. Bootstrap tooling SHOULD use least-privilege credentials and MUST distinguish absence, permission denial and transient API failure when they affect guarantees.
7. Automation MUST fail closed when a protection is required but unavailable; optional features MUST NOT be advertised as configured merely because software supports them.
8. Workflow inputs MUST be handled as data, not interpolated into executable shell fragments. Repository-relative paths MUST be resolved inside the intended workspace and symlink/path traversal MUST be rejected where the path controls privileged publication.
9. Third-party Actions and the Kristal Framework used by a qualification or publication workflow MUST be pinned to immutable commits in the managed GitHub profile. Updates occur by reviewed configuration change.
10. Public status, receipts and attestations MUST be filtered so that optional operational proof does not disclose private identifiers.
