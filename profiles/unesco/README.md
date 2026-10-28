# Classification UNESCO unifiée — profil compagnon (v11)

**Décision d’intégration pour Kristal-Manager et Icon Generator, sans changement rétroactif des contrats v6–v11 :** le Thésaurus UNESCO est le **seul référentiel de domaine actif** de ces outils pour la découverte thématique, la classification des sujets et les icônes. Le Framework conserve la possibilité de correspondances vers d’autres KOS ; celles-ci ne remplacent ni la référence UNESCO retenue ni les identités internes. Le découpage ISCED-F 2013 n’est plus un second système de classification ou de décoration. La taxonomie Arketype reste **indépendante** : elle décrit la structure et l’usage, pas les sujets.

Référence épinglée : [`spec/v7/UNESCO-Thesaurus-Alignment.md`](../../spec/v7/UNESCO-Thesaurus-Alignment.md) et [`spec/v7/reference-kos/unesco-thesaurus-profile.json`](../../spec/v7/reference-kos/unesco-thesaurus-profile.json). Baseline : **7 domaines et 88 microthésaurus**. Conserver notation et URI UNESCO, sans fabriquer de nouveaux codes. Domaine **7** : facette géographique dans le TOC par défaut.

## Exemple de métadonnées workspace

```json
{
  "classification": {
    "primary_archetype": "ARK-04",
    "unesco_thesaurus": {
      "kos_id": "kos:unesco-thesaurus",
      "domains": ["3"],
      "microthesauri": ["3.20"],
      "mapping_status": "reviewed",
      "mapping_provenance": "curated local review"
    }
  }
}
```

Un exemple de fragment est aussi fourni dans [`examples/classification.fragment.example.json`](examples/classification.fragment.example.json). Les domaines et microthésaurus doivent être les notations épinglées ou leurs URI officielles, jamais des codes `UT#`. Le statut `reviewed` signifie revue locale documentée, **pas** approbation de l’UNESCO ni qualification du Framework.

Le schéma compagnon [`kristal-unesco-classification.schema.json`](kristal-unesco-classification.schema.json) porte uniquement sur `classification.unesco_thesaurus`. Une notation de microthésaurus doit appartenir au(x) domaine(s) déclaré(s) ; la validation de relation doit se faire depuis le profil épinglé. `mapping_status=candidate` n’autorise pas la génération automatique comme s’il s’agissait d’un mapping validé.

Une icône peut utiliser l’identifiant de présentation **`UT1` … `UT7`** (préfixe neutre pour éviter toute collision avec l’ancien `00`–`10` d’ISCED-F). Son identité de sujet reste `1` … `7`, avec URI UNESCO intacte dans les métadonnées. **Aucune conversion automatique** de codes ISCED-F ou d’anciens fichiers ICO en mapping UNESCO. Les dossiers sans alignement UNESCO explicite restent `unmapped`, à examiner.

L’outil de vérification en lecture seule `python tools/v11/check_unesco_classification.py <chemin/kristal.workspace.json> --json` contrôle le schéma et l’appartenance des microthésaurus aux domaines déclarés ; il ne modifie aucun fichier. `candidate` et une absence de correspondance sont signalés, pas convertis. Le générateur d’icônes de Manager reste responsable de son propre contrôle avant toute écriture ; **la personnalisation Windows des dossiers locaux doit être activée explicitement, et reste désactivée par défaut**. Le Framework n’applique pas d’icônes.

Ce profil n’altère ni `state_ref`, ni les identités KQ/KP, ni les commitments, ni les données du canon. Les anciens attributs `isced_f2013` restent lisibles comme historique de migration, mais ne sont plus utilisés pour la classification, les filtres ou les icônes.
