# Directories and Federation

V9 already provides exact semantic federation by pinning external state commitments. V10 adds discovery for finding those states.

A common large deployment has two complementary artifacts:

```text
private root node
  ├─ directory.json              # where child nodes live
  └─ federation state snapshot   # exact child state commitments
```

The directory MAY change when a repository moves while the federation snapshot remains unchanged. Conversely, a child state may logically advance while its host location remains unchanged.

A public directory MUST NOT advertise confidential/private nodes unless disclosure of that metadata is explicitly intended. Deployments containing both public and private collections SHOULD keep the authoritative all-node directory private and MAY publish a filtered public directory containing only public nodes.
## Hierarchical directories

A directory entry MAY advertise another node whose role includes `directory`. This permits directory-of-directories topologies for large installations:

```text
private root directory
  ├─ public collections directory
  │    ├─ domain A
  │    └─ domain B
  ├─ private science directory
  │    ├─ chemistry
  │    └─ biology
  └─ private operational collections
```

Directory hierarchy remains an operational discovery graph. It MUST NOT be interpreted as semantic containment, epistemic authority, or exact federation membership unless those relationships are separately expressed by semantic artifacts and v9 pinned state references.

