# v7 / v6 compatibility contract

A v7 implementation MUST accept valid v6 `kristal_state` unchanged and MUST NOT redefine v6 fields. Generated portable projections SHOULD remain `schema_version: 6.0`, `artifact_type: kristal_state`, with lineage under `extensions.kristal_v7`.

External adapters MAY map admitted inputs into a declared Kristal-native interface, but MUST NOT redefine portable v6 fields or claim Kristall semantic authority merely by transporting or mapping an input.
