# Profil d'interopérabilité Spek : verrou éditorial privé (v1)

Ce document décrit le schéma `profiles/spek/private-editorial-handoff.schema.json`.
Il s'agit d'un **profil d'interopérabilité non normatif**, distinct du canon
Kristal, des projections v6/v11 et des contrats de publication C1/C2/C3.

## Usage

Un plan éditorial explicite de Spek lie chaque emplacement à une
`CommunicationRequest` SemantiK et à ses identifiants sources. Le paquet
`private-editorial-handoff/1.0` épingle les empreintes des templates et
requêtes; les identités v6 historiques peuvent être contrôlées contre le
graphe v11 uniquement avec la table `identity-migration-map.json` fournie
et vérifiée séparément.

## Garanties et exclusions

- Lecture seule : ne modifie ni les Kristals ni les assertions.
- Les relations rhétoriques restent `declared_unverified` et n'ont **aucun**
  statut de preuve scientifique.
- Le paquet contient des identifiants privés : il n'est **pas** une page Wiki
  ni un contenu pour `kristal-public`.
- Les approbations et attestations signées C1/C2/C3 ne peuvent **jamais** être
  inscrites ou inférées par ce profil.
- L'existence d'une requête n'implique pas la présence d'un GF/PGF qualifié.

Ce profil n'étend pas `knowledge-model-contract.v5.json` ou les verrouillages
normatifs du Framework : il sert seulement aux échanges locaux entre Spek,
Manager et Architect.
