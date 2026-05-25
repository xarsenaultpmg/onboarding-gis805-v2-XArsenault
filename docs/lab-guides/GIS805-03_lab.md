# GIS805 — Séance 03 / 14 — Dimensions à changement lent : garder la vérité historique chez NexaMart

> Guide de studio (version Markdown). PDF équivalent : `docs/lab-guides/GIS805-03_lab.pdf`.

## En bref

- **Date :** 21 mai 2026
- **Horaire :** 19 h 00 – 22 h 00
- **Lieu :** Longueuil
- **Temps estimé :** 105 min (~1.8 h)

## Objectif

Maîtriser les types SCD 1, 2 et 3 en simulant des changements dans les dimensions NexaMart. Produire la politique SCD du modèle et démontrer l'impact sur les rapports exécutifs.

## Question du CEO

> « Quels changements dans nos dimensions doivent garder la vérité historique, et lesquels peuvent être écrasés ? »

## Contexte du soir

**NexaMart S03 : Quels changements dans nos dimensions doivent garder la véri**

Des clients changent de segment, des magasins changent de région, des noms sont corrigés. Le CEO veut des rapports fiables par rapport à la réalité du moment de la vente, pas celle d'aujourd'hui.

## Résultats d'apprentissage

- Distinguer et implémenter les types SCD 1, 2 et 3.
- Démontrer comment un mauvais choix SCD produit un rapport exécutif trompeur.
- Rédiger une politique SCD justifiée pour les dimensions du modèle.
- Implémenter des clés subrogées et la logique historique dans DuckDB.

## Points clés

- SCD est un choix de politique, pas un choix technique.
- Montrer le mauvais rapport avant le bon rapport est la meilleure pédagogie SCD.
- La politique SCD est un livrable, pas une discussion informelle.

## Idées reçues à déjouer

  **Réalité :** Un UPDATE écrase l'histoire. Si le CEO demande 'ventes par ancienne région', la réponse est perdue.
  **Réalité :** Type 2 préserve l'histoire mais crée de la complexité. Certains attributs (correction de typo) méritent un Type 1.

## Déroulé

### Partie 1 — SCD theory + wrong report demo  *(25 min)*

Types 1/2/3 expliqués, démo du rapport trompeur

### Partie 2 — Sprint 1 : simulate changes  *(40 min)*

make generate && make load, implémenter Type 1 et Type 2 côte à côte dans DuckDB

### Partie 3 — Sprint 2 : SCD policy + board brief  *(40 min)*

Rédiger la politique SCD, prouver par SQL que l'historique est preservé

## Lab

**Objectif du lab :** Simuler des changements dans les dimensions NexaMart, produire un rapport trompeur (Type 1) vs correct (Type 2), et rediger une politique SCD justifiee par dimension pour le CFO.


Votre DuckDB (db/nexamart.duckdb) contient les dimensions du modele NexaMart avec des donnees uniques generees depuis votre username GitHub. Ce soir, deux regions fusionnent : votre mission est de montrer l'impact sur les rapports selon le choix SCD, puis de documenter votre politique de facon a ce qu'un analyste junior puisse l'appliquer.

**Livrable :** docs/scd-policy.md + sql/scd/type1_vs_type2_demo.sql + answers/S03_executive_brief.md

### Sprint 1 — simuler Type 1 vs Type 2  *(40 min)*

**Objectif :** Implementer le meme changement de dimension en Type 1 et en Type 2 cote a cote, puis montrer l'impact sur le rapport de ventes par region.

Fichier cible : sql/scd/type1_vs_type2_demo.sql. NexaMart rattache le magasin Gatineau (region Outaouais) a la region Québec au 2026-03-01. dim_store contient la region Outaouais avant le changement. Meme requete de rapport, resultats differents selon le type SCD choisi.

1. Vérifiez votre base : make generate && make load (ou make check)
2. Creez le fichier : sql/scd/type1_vs_type2_demo.sql
3. -- SETUP : dim_store est encore en version S02 (sans colonnes SCD). Ajoutez-les :
4. ALTER TABLE dim_store ADD COLUMN effective_date DATE DEFAULT '2025-01-01';
5. ALTER TABLE dim_store ADD COLUMN end_date DATE;
6. ALTER TABLE dim_store ADD COLUMN is_current BOOLEAN DEFAULT TRUE;
7. Vérifiez : SELECT store_key, region, is_current FROM dim_store LIMIT 5; -- toutes les lignes doivent avoir is_current = true
8. -- BLOC 1 : Type 1 (rapport trompeur)
9. UPDATE dim_store SET region = 'Québec' WHERE region = 'Outaouais' AND is_current = true;
10. SELECT region, SUM(line_total) AS revenue FROM fact_sales JOIN dim_store USING(store_key) GROUP BY 1 ORDER BY 2 DESC;
11. Notez le resultat : Outaouais a disparu. Revenue absorbé dans Québec — rapport trompeur.
12. -- RESET avant BLOC 2 : BLOC 1 a ecrase Outaouais → make reset && make load
13. -- Puis re-executez les 3 ALTER TABLE du SETUP (effective_date, end_date, is_current)
14. -- BLOC 2 : Type 2 (rapport correct) — nouvelle ligne + expiration ancienne
15. INSERT INTO dim_store (store_key, store_id, store_name, region, effective_date, end_date, is_current) SELECT (SELECT MAX(store_key) FROM dim_store) + ROW_NUMBER() OVER (ORDER BY store_id), store_id, store_name, 'Québec', '2026-03-01', NULL, true FROM dim_store WHERE region = 'Outaouais' AND is_current = true;
16. UPDATE dim_store SET end_date = '2026-02-28', is_current = false WHERE region = 'Outaouais' AND end_date IS NULL;
17. SELECT s.region, SUM(f.line_total) AS revenue FROM fact_sales f JOIN dim_store s ON f.store_key = s.store_key GROUP BY 1 ORDER BY 2 DESC;
18. Resultat correct : Outaouais reste visible pour les ventes de janv-fevrier (store_key=4 intact).
19. Ajoutez un commentaire SQL expliquant la difference business entre les deux blocs
20. Committez : git add -A && git commit -m 'S03 sprint1 type1-vs-type2'

**Résultat attendu :** Fichier sql/scd/type1_vs_type2_demo.sql avec deux blocs annotes : premier bloc montre Outaouais disparu (Type 1), second bloc montre Outaouais pour ventes historiques et Québec pour ventes post-fusion (Type 2).


**Erreurs fréquentes :**
- ⚠️ JOIN sur store_id au lieu de store_key : Type 2 retourne des doublons — toujours joindre sur la cle subrogee
- ⚠️ Oublier is_current = false sur les anciennes lignes : la requete ramene toutes les versions
- ⚠️ UPDATE sans WHERE is_current = true : ecrase les lignes historiques archivees
- ⚠️ Justification technique dans les commentaires SQL : ecrivez la raison BUSINESS (impact sur les rapports du VP)

### Sprint 2 — politique SCD + brief executif  *(40 min)*

**Objectif :** Rediger docs/scd-policy.md et answers/S03_executive_brief.md justifiant les choix SCD avec un chiffre d'impact observe dans vos donnees.

La politique SCD est le livrable central de ce soir. Elle doit etre lisible par un CFO : raisons business, pas de jargon technique. Le brief explique pourquoi le rapport Q1 par region etait inexact avec Type 1 et ce que Type 2 corrige.

1. Creez docs/scd-policy.md avec ce squelette (minimum 3 dimensions) :
2.   dim_store | region | Type 2 | les ventes doivent refleter la region AU MOMENT de la transaction
3.   dim_store | store_name | Type 1 | correction de typo, aucune valeur historique
4.   dim_customer | segment | Type 2 | VP Marketing suit les migrations entre segments
5.   dim_customer | email | Type 1 | correction uniquement, pas de rapport strategique
6. Verifiez votre Type 2 : SELECT COUNT(*) FROM dim_store WHERE is_current = false; -- doit etre > 0
7. Committez : git add docs/scd-policy.md && git commit -m 'S03 scd-policy declared'
8. Creez answers/S03_executive_brief.md (150-300 mots) : expliquez au VP pourquoi le rapport Q1 etait inexact et ce que Type 2 corrige
9. Incluez un chiffre observe dans vos donnees (ex: 'X % du revenue attribue a la mauvaise region avec Type 1')
10. Notez dans ai-usage.md chaque interaction IA significative (outil, prompt utilise, validation manuelle)
11. git add -A && git commit -m 'S03 brief executif et ai-usage' && git push

**Résultat attendu :** docs/scd-policy.md commite avec >= 3 dimensions documentees (attribut + type + raison business) + answers/S03_executive_brief.md avec un chiffre d'impact observe dans les donnees.


**Erreurs fréquentes :**
- ⚠️ Raison technique : 'Type 2 parce que c'est plus robuste' n'est pas acceptable — reecrivez en termes business
- ⚠️ Brief sans chiffre : nommez un ecart observe, une baisse de revenue attribuee a la mauvaise region
- ⚠️ ai-usage.md vide ou generique : decrivez precisement le prompt et ce que vous avez valide
- ⚠️ Oublier de committer docs/scd-policy.md : c'est 10 % de la note (process_trace)

Rappel S02 : committez incrementalement (>= 3 commits) et documentez chaque interaction IA dans ai-usage.md (outil, prompt utilise, validation manuelle). Ces deux points valent 15 % de votre note (process_trace 10 % + reproducibility 5 %).

**Fichiers à produire (`repo_artifacts`) :**

- `answers/S03_executive_brief.md` — Brief VP expliquant l'impact des choix SCD sur les rapports NexaMart (avec chiffre observe)
- `sql/scd/type1_vs_type2_demo.sql` — Deux blocs SQL annotes — rapport trompeur (Type 1) vs rapport correct (Type 2)
- `docs/scd-policy.md` — Politique SCD par dimension avec type retenu et raison business
- `ai-usage.md` — Trace des interactions IA avec validation manuelle

## Remise

- **Échéance :** Before next session starts
- **Artefacts requis :**
  - `answers/S03_executive_brief.md`
  - `db/nexamart.duckdb`
  - `ai-usage.md`
- **Rubrique de notation :**
  - **model_quality** (40 %) — SCD Type déclaré pour au moins dim_store(région). Schéma distingue current_value et historical_value.
  - **validation_quality** (25 %) — Deux requêtes : rapport trompeur (Type 1) vs rapport correct (Type 2) côte à côte pour une dimension modifiée.
  - **executive_justification** (20 %) — Brief explique au VP pourquoi le rapport historique était inexact et ce qui a changé.
  - **process_trace** (10 %) — docs/scd-policy.md commité avec type retenu + raisonnement business (pas technique).
  - **reproducibility** (5 %)

## Lectures

- [Kimball Group -- Slowly Changing Dimensions](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-1-2-3/) — Les trois types de SCD et quand utiliser chacun
- [dbt Labs -- Snapshots (SCD Type 2)](https://docs.getdbt.com/docs/build/snapshots) — Implémentation moderne des SCD Type 2 avec dbt snapshots

---

*Généré automatiquement à partir de `content/sessions/GIS805-03.yaml`. Pour corriger une coquille, modifiez le YAML source et poussez sur `master` — la CI régénère PDF + Markdown.*
