<!-- kOA Doc Server · Docs IA · lot 01 · source datée, non-certifiante -->
# Documentation IA — Kristal Framework

**Périmètre :** Norme sémantique Kristal : contrats v6–v10 préservés et projet v11 `11.0.0-draft.4` pour identités canoniques et lexiques séparés.

**Origine :** snapshot local documenté (20 novembre 2026, ou archive complémentaire). Les chemins et versions actifs sont à vérifier sur le poste avant toute modification.

**Autorité :** Le Framework possède les schémas, contraintes, profils et tests de conformité qu’il publie. Les détenteurs des Kristals restent propriétaires de leurs états et migrations.

## Ordre de lecture conseillé à un agent

1. [`README.md`](../../README.md) — Versions et périmètre.
2. [`VERSION`](../../VERSION) — Version du checkout capturé.
3. [`spec/v11/Home.md`](../../spec/v11/Home.md) — Orientation v11.
4. [`spec/v11/Conformance.md`](../../spec/v11/Conformance.md) — Tests/conformité du projet v11.
5. [`spec/v11/Identity-and-Wikidata.md`](../../spec/v11/Identity-and-Wikidata.md) — KQ/KP/KA/KS et crosswalk Wikidata.
6. [`docs/02_ARCHITECTURE.md`](../../docs/02_ARCHITECTURE.md) — Séparation état, dérivation, matérialisation, échange, runtime.
7. [`contracts/v11-compatibility-lock.json`](../../contracts/v11-compatibility-lock.json) — Références de compatibilité.
8. [`tools/v11/validate_v11.py`](../../tools/v11/validate_v11.py) — Validateur v11.

## Documents produits par cet overlay

- [`AI_CONTEXT.md`](AI_CONTEXT.md) — limites, parcours et points de contrôle.
- `PROFIL_INGENIERIE.md` — produit **sur demande** à partir d'un scan RepoSurveyor du code local; ce fichier n'est pas fourni par le lot rédactionnel.
- `AGENTS.md` à la racine — consignes de dépôt existantes conservées ou nouvelles si elles n'existaient pas.

## Règles transversales

- Une capture documentaire n'établit ni conformité, ni maturité, ni disponibilité en production.
- Ne pas remplacer contrats, ADR, README ou preuves propriétaires par cette aide de navigation.
- Nouveau Framework v11 : lire le profil effectivement adopté; ne jamais imposer une migration par défaut.

## Procédure opérationnelle proposée (lot 04)

- [`OPERATIONS.md`](OPERATIONS.md) — parcours concret et points de contrôle à vérifier avant tout effet.
