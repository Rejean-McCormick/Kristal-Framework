# Kristal Framework 11.0.0-draft.4 — qualification locale

**17 octobre 2026** — révision additive d'interopérabilité, pas de ratification de norme ni de publication réseau.

## Validation exécutée

- `python tools/validate_all.py` : **PASS** sur le dépôt complet (v6–v10, v11, v10 ecosystem, Kit/bootstrap local, outils JS, schémas, TCK et liens).
- `python -m unittest discover -s tools/tests -p test_v11_interop_preflight.py -v` : **7/7 PASS** : couverture directe/repli, restriction Kit sur couches entrantes, SHA-256, correspondance non acceptée, mismatch namespace, sortie non destructive, invariance du canon.
- Précontrôle `tools/v11/interop_preflight.py` avec `examples/v11/*` : **PASS** (rapport réversible de source SHA et couverture KQ/KP).
- **Test croisé réel avec Authoring Kit 4.0.0-draft.3 sur une copie temporaire de son exemple** : précontrôle Framework sur un catalogue synthétique conforme au format diK, puis `import-dik-catalog --register`, `select-v11-catalog`, `check-v11`, `coverage-v11` : **PASS**. Le Kit n'a pas été modifié par ce test et aucune donnée de production n'a été activée.
- Vérification des archives d'origine : **12 fichiers `schemas/v11` + 9 fichiers `tck/v11` inchangés octet à octet**, **37 schémas v6–v10 inchangés**, ainsi que les verrous de compatibilité historiques. La ligne de version du core-spec v11 a été mise à jour, pas les règles sémantiques.
- Wiki : liens internes `[[...]]` et navigation vérifiés localement, aucun lien manquant signalé.

## Ce qui n'est PAS qualifié

- Exécution de la suite *effective de diK 1.0.0-alpha.7* sur toutes ses sorties : le test de Kit utilise un catalogue synthétique conforme, pas l'archive binaire diK alpha.7.
- Conformité stable de l'Authoring Kit, des migrations historiques arbitraires, de tous les dépôts externes et de la publication/activation en conditions réelles.
- Dump Wikidata complet, grande volumétrie, 300 langues remplies, authenticité des preuves/signes des approbateurs et reprise après panne du système.
- Changements de contrats : **aucun nouveau schéma v11 normatif** dans cette révision. Tout changement futur nécessitera de nouveaux vecteurs et un processus de ratification.

## Gardes de version

- Release Framework : `11.0.0-draft.4`, marquée `draft`.
- Schémas/TCK v11 : empreintes inchangées depuis `11.0.0-draft.3` (profil `kristal.semantic-identity/11.0`).
- Auteur canonique Kit : `4.0.0-draft.3` (pin originel Framework draft.3 conservé).
- Gestionnaire lexical diK : `1.0.0-alpha.7` (externe, import reprenable non certifié en grande échelle).

**Preflight ≠ approbation sémantique ≠ import/registration ≠ activation.**
