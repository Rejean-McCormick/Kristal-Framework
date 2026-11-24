<!-- kOA Doc Server · Docs IA · lot 04 · proposition non certifiante -->
# Procédure IA — Kristal-Framework

**Objet :** Standard v11 évolutif et non bloquant.

**Source de rédaction :** `Kristal-Framework_Code_snapshot.zip` (capture datée). Ce document ne déclare pas que les commandes ont été exécutées sur le poste local.

## Parcours recommandé

1. Déterminer le profil réellement épinglé par le consommateur avant toute lecture des contrats v11.
2. Lire `spec/v11/Home.md`, `spec/v11/Conformance.md` et `contracts/v11-compatibility-lock.json` pour comprendre l’écart entre proposition et conformité.
3. Préserver les identités KQ/KP/KA/KS et les dictionnaires séparés lors d’une migration **seulement si le propriétaire l’a approuvée**.
4. Ne pas faire d’une absence de v11 un blocage du Doc Server, de Kompiler ou des lecteurs historiques.
5. Les tests locaux valident une révision et un profil; ne pas en déduire publication, activation ou vérification en exploitation.

## Documents propriétaires à consulter

`spec/v11/Home.md`, `spec/v11/Conformance.md`, `contracts/v11-compatibility-lock.json`.

## Vérifications avant effet

- Confirmer la racine, la révision et les versions du dépôt réellement installé.
- Ne pas substituer la présente fiche aux `AGENTS.md`, contrats, ADR et validations propriétaires.
- Ne pas copier de secrets, données privées, rapports de maturité ou sauvegardes dans un ZIP public.
- Exécuter tout diagnostic, synchronisation ou publication **seulement après décision explicite**; préserver les rapports existants.
- Le Framework v11 demeure **facultatif et non bloquant** pour Doc Server.
