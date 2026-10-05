# Kristal Icon Code

Status: **informative presentation profile**

Profile identifier: `kristal-icon/1.0`

Kristal Icon Code is a compact visual presentation profile for identifying a Kristal at a glance. It is intentionally outside semantic identity and canonical epistemic state.

```text
VISUAL CODE != SEMANTIC IDENTITY
ICON NATURE != ARTIFACT TYPE
DOMAIN COLOR != DOMAIN MEANING
MATURITY != EPISTEMIC CERTAINTY
MATURITY != PROBLEM RESOLUTION
```

A conforming icon carries exactly three persistent visual signals:

```text
color band = where / domain
center pictogram = what kind of knowledge object
maturity bar = how mature the Kristal representation is
```

No storage version, schema version, assertion count, certainty score, source count or runtime detail belongs in the normal icon.

## 1. Domain band

The top strip encodes one to three domains. The first domain is primary.

Recommended deterministic geometry:

| Domains | Widths |
|---|---|
| 1 | `100%` |
| 2 | `65% / 35%` |
| 3 | `50% / 25% / 25%` |

A domain color is a presentation convention chosen by a deployment or palette. It MUST NOT be interpreted as semantic identity. The same semantic domain SHOULD keep the same color within one icon pack.

Machine domain codes SHOULD use 2-8 uppercase ASCII letters/digits, for example `ALG`, `NUM`, `AUTO`, `MED`.

## 2. Nature pictogram

The center pictogram describes the dominant knowledge-object nature of the Kristal, not its subject and not its storage layout.

| Code | Nature | Dominant question |
|---|---|---|
| `REF` | Reference | What consolidated knowledge is known about this domain? |
| `COL` | Collection | What objects belong to this set/catalog? |
| `MOD` | Model | How is this system composed and related? |
| `PRT` | Protocol | What action/rule applies in this situation? |
| `TWN` | Twin | What is the current reflected state of this individual real system? |
| `INV` | Investigation | What is being actively established, explored or proved? |
| `SRC` | Sources | What source/evidence material is the knowledge built from? |

Examples:

- a list of recipes is normally `COL`;
- a vehicle circuit graph used for diagnosis is normally `MOD`;
- police or hospital operating procedures are normally `PRT`;
- a live reflected representation of one university is normally `TWN`;
- a mathematical proof under active construction is normally `INV`;
- a consolidated scientific domain Kristal is normally `REF`;
- a documentary/source library is normally `SRC`.

A Kristal can contain several of these structures internally. The icon selects one dominant nature only.

The reference renderer uses the fixed center-pictogram color:

```text
#1e6864
```

This neutral center color avoids confusing nature with domain colors.

## 3. Maturity

The bottom bar contains five blocks plus an integer `0..5` when the render size permits it.

| Level | Meaning |
|---|---|
| `0` | embryonic |
| `1` | initialized |
| `2` | structured |
| `3` | well mapped |
| `4` | strongly validated |
| `5` | mature / stable |

Maturity describes the Kristal **as a knowledge representation artifact**. It does not mean that every claim is certain, and it does not mean that an open question has been solved. An `INV` Kristal MAY legitimately be maturity `5`.

## 4. Windows icon sizes

A multi-resolution `.ico` pack SHOULD contain:

```text
16, 20, 24, 32, 40, 48, 64, 96, 128, 256 px
```

Small-size renderers MAY simplify details. The reference generator keeps the five maturity blocks at compact sizes and omits the numeric maturity label where it would reduce legibility.

## 5. File naming

The deterministic file name is:

```text
KR-{NATURE}-{DOMAIN1}[-{DOMAIN2}][-{DOMAIN3}]-M{0..5}.ico
```

Rules:

- `DOMAIN1` is always the primary domain;
- secondary domains are canonicalized in stable order;
- the `.ico` file name does not contain a pixel size because the file is multi-resolution;
- individual PNG exports MAY append `_{SIZE}` before `.png`.

Examples:

```text
KR-MOD-AUTO-ELEC-M4.ico
KR-PRT-MED-M4.ico
KR-TWN-EDU-M4.ico
KR-INV-NUM-ALG-ANA-M4.ico
KR-COL-FOOD-M2.ico
```

## 6. Machine-readable presentation profile

A renderer MAY consume a `kristal-icon/1.0` profile containing:

- optional `kristal_ref`;
- one to three ordered domains with code, display name and color;
- one nature code;
- maturity `0..5`;
- optional rendering metadata.

The non-normative tooling schema is located at [`../../tools/icons/kristal-icon-profile.schema.json`](../../tools/icons/kristal-icon-profile.schema.json). An example is available at [`../../examples/v8/icon-profile.example.json`](../../examples/v8/icon-profile.example.json).

## 7. Rendering and derived artifacts

The icon profile is a read/presentation model. Generated ICO/PNG files are derived artifacts and MAY be regenerated from the profile.

The reference browser generator is documented at [`../../tools/icons/README.md`](../../tools/icons/README.md).

## 8. Windows desktop folder binding

Kristal defines an optional informative Windows folder-binding convention identified as:

```text
kristal-desktop/1.0
```

This convention does **not** add a fourth signal to the icon. It binds a generated Kristal icon to a Windows folder and provides a compact human tooltip plus machine-readable local presentation metadata.

The authority boundary is explicit:

```text
DESKTOP.INI != SEMANTIC AUTHORITY
INFOTIP != CANONICAL STATE
[Kristal] != SOURCE OF TRUTH
DESKTOP BINDING = REGENERABLE LOCAL CACHE
```

If local desktop metadata disagrees with the canonical Kristal or its presentation profile, the canonical source wins and the desktop binding SHOULD be regenerated. Deleting `desktop.ini` MUST NOT destroy semantic information.

### 8.1 Human tooltip (`InfoTip`)

The recommended tooltip answers, in stable order:

```text
NAME • NATURE • DOMAINS • MATURITY • VOLUME
```

Example:

```text
Vehicle Diagnostics • Modèle • Auto / Électrique / Data • Maturité 4/5 • 833 assertions · 29 sources
```

Rules:

- `NAME`, `NATURE` and domain labels are human-facing and MAY be localized through the v8 Language Layer;
- maturity is rendered as `N/5`;
- volume is optional and SHOULD contain only immediately useful counts, normally assertions and sources when those concepts apply;
- implementations SHOULD target roughly 120–180 characters for normal tooltips;
- when space is constrained, optional volume information SHOULD be dropped before identity/type/domain/maturity information;
- schema versions, hashes, storage paths, runtime details and internal IDs SHOULD NOT appear in the normal tooltip.

The tooltip is a convenience summary. Its text is not a machine identity and MUST NOT be parsed as the authoritative metadata representation.

### 8.2 Machine-readable `[Kristal]` section

A Windows `desktop.ini` MAY contain a `[Kristal]` section. Unknown consumers may ignore it; Kristal-aware tooling can use it as a deterministic local binding/cache.

Recommended keys are:

| Key | Meaning |
|---|---|
| `Profile` | MUST be `kristal-desktop/1.0` for this convention |
| `IconProfile` | icon presentation profile, normally `kristal-icon/1.0` |
| `IconCode` | deterministic icon identifier without path |
| `Title` | human display title |
| `KristalRef` | optional stable Kristal reference |
| `Nature` | `REF`, `COL`, `MOD`, `PRT`, `TWN`, `INV` or `SRC` |
| `Domain1` | primary domain code |
| `Domain2` | optional secondary domain code |
| `Domain3` | optional tertiary domain code |
| `Maturity` | integer `0..5` |
| `Assertions` | optional assertion count |
| `Sources` | optional source count |

`Domain1..3` preserve the same primary-first ordering as the icon code. Counts are informative snapshots and MAY become stale; they MUST NOT be treated as semantic truth.

### 8.3 Recommended `desktop.ini` layout

```ini
; Generated from Kristal presentation metadata. Regenerable local binding.
[.ShellClassInfo]
IconResource=.kristal\KR-MOD-AUTO-ELEC-NET-M4.ico,0
InfoTip=Vehicle Diagnostics • Modèle • Auto / Électrique / Data • Maturité 4/5 • 833 assertions · 29 sources

[Kristal]
Profile=kristal-desktop/1.0
IconProfile=kristal-icon/1.0
IconCode=KR-MOD-AUTO-ELEC-NET-M4
Title=Vehicle Diagnostics
KristalRef=Kristal-VehiculeDiag
Nature=MOD
Domain1=AUTO
Domain2=ELEC
Domain3=NET
Maturity=4
Assertions=833
Sources=29
```

A copyable example is provided at [`../../examples/v8/desktop.ini.example`](../../examples/v8/desktop.ini.example).

Shell extensions, file associations and operating-system integrations beyond this local folder binding remain implementation concerns rather than semantic authority.
