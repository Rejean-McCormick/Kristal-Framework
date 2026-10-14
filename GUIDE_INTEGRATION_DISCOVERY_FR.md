# Framework — profils de lecture et découverte

Le Framework ajoute un **profil complémentaire non canonique** pour exploiter les trois fichiers du Kristal Authoring Kit 3.3.0 : `kristal.discovery.json`, `derived/reader-inventory.json` et `derived/reader-profile.json`.

Le lecteur JS de référence valide leur cohérence, calcule un plan indicatif et peut contrôler la taille et SHA-256 de tous les fichiers locaux référencés. Il propose un mode JSON ou JSONL différent ; pour JSONL, la taille maximum d'un enregistrement doit encore être mesurée avant de configurer le streaming de simdjson. Le Framework ne compile **pas** simdjson.

Arketype annonce la structure et l'usage ; la taille réelle et le format physique déterminent la configuration du parseur. Les profils inconnus reviennent au lecteur générique. Il faut vérifier l'accès autorisé, le format réel, la compression et le chiffrement avant de lire les données. Les informations dérivées ne créent pas de droits et ne changent ni le canon ni les engagements logiques v9.

## Exemple

```bash
cd reference/js
node bin/kristal-ref.mjs inspect-reader-discovery ../../profiles/reader-discovery/examples/demo-kristal --verify-files
```

Le catalogue de schémas et la description du protocole se trouvent sous `profiles/reader-discovery/` et `spec/v10/Reader-Discovery-Profile.md`. Le wiki fournit la page `Reader-Discovery-and-Arketype-v10.md`.
