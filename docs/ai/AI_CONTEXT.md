<!-- kOA Doc Server · Docs IA · lot 01 · source datée, non-certifiante -->
# Documentation IA — Kristal Framework

**Périmètre :** Norme sémantique Kristal : contrats v6–v10 préservés et projet v11 `11.0.0-draft.4` pour identités canoniques et lexiques séparés.

**Origine :** snapshot local documenté (20 novembre 2026, ou archive complémentaire). Les chemins et versions actifs sont à vérifier sur le poste avant toute modification.

**Autorité :** Le Framework possède les schémas, contraintes, profils et tests de conformité qu’il publie. Les détenteurs des Kristals restent propriétaires de leurs états et migrations.

## Méthode de travail IA

1. Lire le profil effectivement adopté par le consommateur; ne pas présumer que chaque Kristal est déjà v11.
2. Vérifier la séparation entre identifiants sémantiques KQ/KP/KA/KS, dictionnaires lexicaux et crosswalk Wikidata.
3. Préserver les vecteurs historiques, locks, assertions et identités des versions antérieures.
4. Tester les exemples/fixtures adéquats sans modifier les sources propriétaires des consommateurs.

## Entrées et validations attestées par les sources

- `python tools/validate_all.py`
- `python tools/v11/validate_v11.py`

*Avant exécution, vérifier les préconditions locales et les effets possibles de la commande. Les commandes sont des points d’entrée documentés, pas des validations effectuées par cet overlay.*

## Frontières à ne jamais franchir

- v11 est `draft.4` dans ce snapshot, non une obligation imposée à tout l’écosystème.
- Une réussite des tests du Framework ne certifie ni les consommateurs ni leur déploiement.
- Une proposition de rapprochement legacy ne réécrit jamais automatiquement les Kristals.

## Incertitudes et limites explicites

- Les références de conformité doivent être associées à un profil et une révision exacts.

## Sources à relire

- [`README.md`](../../README.md) — Versions et périmètre.
- [`VERSION`](../../VERSION) — Version du checkout capturé.
- [`spec/v11/Home.md`](../../spec/v11/Home.md) — Orientation v11.
- [`spec/v11/Conformance.md`](../../spec/v11/Conformance.md) — Tests/conformité du projet v11.
- [`spec/v11/Identity-and-Wikidata.md`](../../spec/v11/Identity-and-Wikidata.md) — KQ/KP/KA/KS et crosswalk Wikidata.
- [`docs/02_ARCHITECTURE.md`](../../docs/02_ARCHITECTURE.md) — Séparation état, dérivation, matérialisation, échange, runtime.
- [`contracts/v11-compatibility-lock.json`](../../contracts/v11-compatibility-lock.json) — Références de compatibilité.
- [`tools/v11/validate_v11.py`](../../tools/v11/validate_v11.py) — Validateur v11.
