# Kristal Icon Generator

Générateur autonome d’icônes pour le **Kristal Icon Code**.

## Ce que le programme encode

- **Bande supérieure** : domaine(s), maximum 3.
  - 1 domaine : 100 %.
  - 2 domaines : 65 % / 35 %.
  - 3 domaines : 50 % / 25 % / 25 %.
- **Pictogramme central** : nature du Kristal.
  - REF — Référence
  - COL — Collection
  - MOD — Modèle
  - PRT — Protocole
  - TWN — Twin
  - INV — Investigation
  - SRC — Sources
- **Barre inférieure** : maturité 0–5.

## Résolutions Windows

Chaque fichier `.ico` contient maintenant **10 images PNG intégrées** :

- 16 × 16 px
- 20 × 20 px
- 24 × 24 px
- 32 × 32 px
- 40 × 40 px
- 48 × 48 px
- 64 × 64 px
- 96 × 96 px
- 128 × 128 px
- 256 × 256 px

Windows peut ainsi choisir automatiquement la résolution adaptée à l’Explorateur, au mode d’affichage et au facteur DPI.

### Rendu aux petites tailles

À 16–24 px, l’icône conserve les trois informations principales, mais le rendu est volontairement simplifié. Le chiffre de maturité est omis aux tailles compactes afin de préserver la lisibilité; les cinq cases restent visibles. À partir des tailles supérieures, le chiffre réapparaît.

Les aperçus 16–64 px sont agrandis dans l’interface du générateur pour faciliter leur inspection; les fichiers produits gardent leur vraie résolution.

## Utilisation

1. Ouvrir `index.html` dans Chrome ou Edge récent.
2. Ajuster la charte des domaines au besoin.
3. Vérifier les aperçus de 16 à 256 px.
4. Cliquer **Choisir un dossier et générer tout**.
5. Choisir un dossier vide ou dédié au pack.

Le programme crée :

```text
<dossier choisi>/
├── ico/
│   ├── KR-REF-ALG-M0.ico
│   ├── KR-INV-NUM-ALG-ANA-M4.ico
│   ├── ...
│   └── ...
├── png/             # si l’option PNG est cochée
│   ├── 16/
│   ├── 20/
│   ├── 24/
│   ├── 32/
│   ├── 40/
│   ├── 48/
│   ├── 64/
│   ├── 96/
│   ├── 128/
│   └── 256/
└── manifest.json
```

## Nomenclature des fichiers

Le nom est déterministe et facilement analysable par programme :

```text
KR-{TYPE}-{DOMAINE1}[-{DOMAINE2}][-{DOMAINE3}]-M{0..5}.ico
```

Exemples :

```text
KR-MOD-ALG-M4.ico
KR-INV-NUM-ALG-ANA-M4.ico
KR-PRT-MED-M3.ico
KR-TWN-EDU-M5.ico
KR-COL-FOOD-M2.ico
```

Codes de nature : `REF`, `COL`, `MOD`, `PRT`, `TWN`, `INV`, `SRC`.

Pour les domaines mathématiques initiaux : `ALG`, `NUM`, `GEO`, `TOP`, `ANA`, `PRB`, `LOG`, `TCS`.

L’ordre des domaines est significatif : le domaine principal vient toujours en premier. Les domaines secondaires sont triés canoniquement par code pour stabiliser les noms de fichiers. Avec trois domaines, les deux secondaires ont le même poids visuel (25 % / 25 %) et ne produisent donc pas de doublons d’ordre.

La taille n’est jamais ajoutée au nom du fichier `.ico`, puisqu’un même ICO contient toutes les résolutions. Les PNG individuels ajoutent leur taille en suffixe, par exemple `KR-MOD-AUTO-M4_32.png`.

Le `manifest.json` contient aussi l’identifiant compact, les domaines, le type, la maturité et la règle de nomenclature.

## Taille de la méga collection par défaut

Avec les 8 domaines initiaux, les 7 natures et les 6 maturités :

- profils à 1 domaine : 8
- profils à 2 domaines : 8 × 7 = 56
- profils à 3 domaines : 8 × C(7,2) = 168
- total profils domaine : 232
- total icônes : 232 × 7 × 6 = **9 744 fichiers ICO**
- images PNG intégrées dans les ICO : **97 440** (10 résolutions par ICO)

Les deux domaines secondaires d’un profil à 3 domaines sont considérés équivalents, car ils occupent chacun 25 % de la bande. Cela évite de générer deux fichiers visuellement identiques.

## Pourquoi un ICO multi-résolutions ?

Windows peut choisir automatiquement la résolution la plus adaptée à l’affichage. C’est particulièrement utile pour une association ultérieure via `desktop.ini`.

## Dépendances

Aucune. Le fichier HTML fonctionne entièrement côté navigateur et ne contacte aucun serveur.


## Couleur du pictogramme central

Tous les pictogrammes de nature au centre utilisent la couleur fixe **`#1e6864`**. Les couleurs des domaines restent réservées à la bande supérieure et aux blocs de maturité.


## Version de nomenclature

Le générateur utilise le schéma de pack `kristal-icon-pack/1.3` et le profil visuel `kristal-icon/1.0`.

Le profil est documenté dans [`../../spec/v8/Kristal-Icon-Code.md`](../../spec/v8/Kristal-Icon-Code.md). Le schéma JSON de tooling est `kristal-icon-profile.schema.json`.

## Liaison de dossier Windows (`desktop.ini`)

Le framework v8 définit aussi la convention informative `kristal-desktop/1.0`. Elle ne change pas le dessin de l’icône : elle associe l’ICO à un dossier et expose un résumé au survol.

Format de survol recommandé :

```text
NOM • NATURE • DOMAINES • MATURITÉ • VOLUME
```

Exemple :

```text
Vehicle Diagnostics • Modèle • Auto / Électrique / Data • Maturité 4/5 • 833 assertions · 29 sources
```

Le `desktop.ini` peut aussi contenir une section `[Kristal]` avec `IconCode`, `Nature`, `Domain1..3`, `Maturity` et des compteurs informatifs. Cette section est un cache local régénérable, jamais une source d’autorité sémantique.

Exemple complet : [`../../examples/v8/desktop.ini.example`](../../examples/v8/desktop.ini.example).

