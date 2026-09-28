# Profil d'application Konstellation Reader JSON v1

Ce profil optionnel fournit une sortie directement consommable par Konstellation v0.4. Il ne change aucun schéma de Kristal v5 et n'annonce pas une conformité universelle des compilateurs.

L'outil `tools/publish_konstellation_pack.mjs` reçoit un catalogue normalisé, des assertions avec métadonnées épistémiques explicites, une ReaderPolicy v5 et l'identité de l'Exchange source. Il publie atomiquement un dossier neuf comprenant catalogue, table JSON, politique, manifeste avec hashes et tailles, puis la configuration `konstellation.json`.

Prérequis : Node.js et Python avec `jsonschema` (déjà déclaré dans requirements-dev.txt). La variable `PYTHON` peut désigner l'interpréteur. Les schémas officiels de politique et manifeste sont vérifiés avant publication. Aucune signature ou validation d'autorité n'est synthétisée.

Depuis la racine du dépôt, exemple synthétique :

```bash
node tools/publish_konstellation_pack.mjs --catalog examples/konstellation/catalog.json --assertions examples/konstellation/assertions.json --policy examples/konstellation/policy.json --exchange-id sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --artifact-status working --created-at 2026-09-27T00:00:00Z --output output/konstellation-demo
```

L'Exchange d'exemple est une identité de fixture. En production, passer l'identité effective et le statut attesté. Le profil émet un `working_exchange`; il ne transforme pas une collection de preuves en Exchange de référence.

Depuis Konstellation : `KONSTELLATION_BACKEND_CONFIG=/chemin/output/konstellation-demo/konstellation.json npm start`. La validation du lecteur refuse les incompatibilités de registre, de politiques ou de métadonnées. Adapter les Lens au registre du catalogue.

Les colonnes obligatoires sont id, subject, relation, value, status, certainty, validationStatus, validatedAs, authority, recognitionStatus, scope et sourceRefs. Un intervalle exige ruleRef et derivedFrom. Les doublons, sources inconnues, domaines incompatibles et métadonnées absentes sont refusés. Les données existantes ne sont jamais écrasées. Les qualificatifs et données supplémentaires sont conservés, mais leur éventuelle utilisation comme filtre nécessite un profil de lecture explicite.

La table contient au maximum 100000 assertions triées par sujet, prédicat, objet et identité, comparés en JSON canonique ECMAScript. Elle forme un groupe unique. Aucun bitmap n'est émis; le lecteur construit ses index. Les politiques bitmap du manifeste décrivent la convention réservée et déclarent explicitement cette absence dans notes.

Les données EncyKlopedia doivent d'abord recevoir leurs métadonnées par leur pipeline Kristal. La présence d'un lien Wikidata ou d'une preuve ne suffit pas à inventer une validation ou une reconnaissance d'autorité.
