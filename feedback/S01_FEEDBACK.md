# Rétroaction automatisée -- S01 (NexaMart kickoff : pourquoi l'organisation ne peut pas répondre à ses propres questions)

_Générée le 2026-06-22T15:34:40+00:00 -- Run `20260622T152646Z-9f8024aa`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief n'a pas pu être validée automatiquement. Quelques pistes constructives ci-dessous pour vous aider à la rendre exécutable et alignee avec la question posée.

_Observation technique : colonnes manquantes (oracle): category, quarter_

<details><summary>Requête analysée — cliquez pour déplier</summary>

```sql
SELECT s.région, ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_store s USING (store_key)
GROUP BY s.région
ORDER BY revenue DESC
```

</details>

- Colonnes retournées : `région, revenue`
- Correspondance avec les colonnes attendues :
  - `category` → `(à ajouter ou renommer)`
  - `region` → `région`
  - `quarter` → `(à ajouter ou renommer)`
  - `revenue` → `revenue`

**Pistes :**
> Aucune requête SQL trouvée dans le brief ni dans les fichiers du repo. Une requête canonique a été synthétisée à partir du schéma de votre base pour vérifier que vos tables et jointures sont correctement en place. Ajoutez votre requête finale dans la section « Preuve » avec un bloc ```sql ... ``` pour éliminer cette étape.
> Synonymes acceptés par colonne:
  category: ['category', 'categorie', 'p.category', 'sous_categorie']
  region: ['region', 's.region']
  quarter: ['quarter', 'trimestre', 'd.quarter', 'q']
  revenue: ['net_revenue', 'revenue', 'revenu', 'total_revenue', 'ca', 'sales', 'line_total', 'gross_revenue']

## 2. Rétroaction pédagogique sur le brief

> Bon diagnostic opérationnel et preuve SQL solide : le brief identifie des déclins précis et fournit des validations convaincantes. Il manque toutefois la traçabilité (commits/IA) et une garantie de reproductibilité complète pour productionnaliser le livrable.

### Observations par dimension

**Model quality**
- Observation : Le brief déclare explicitement le grain («une ligne = une ligne de vente») et liste dim_product, dim_store et dim_date comme dimensions clés.
- Piste d'amélioration : Préciser le traitement des changements historiques (SCD) et justifier le choix du pattern (ex. SCD Type 2 vs Type 1) pour préserver l'historique des catégories.

**Validation quality**
- Observation : La section Preuve inclut une requête SQL avec agrégations et LAG, et la section Validation montre réconciliation des totaux, intégrité référentielle (0 orphelins) et vérification du grain.
- Piste d'amélioration : Ajouter des checks explicites pour les NULLs et documenter les seuils/exclusions (ex. prev_quarter_sales = 0) pour éviter divisions par zéro.

**Executive justification**
- Observation : La Réponse exécutive synthétise les déclins clés (ex. Québec/Home & Garden -87% en Q2) et propose des recommandations court/moyen/long terme pour le CEO.
- Piste d'amélioration : Formuler une décision claire demandée au CEO (par ex. valider budget d'investigation pour les 3 combos région/catégorie prioritaires).

**Process trace**
- Observation : Aucune mention d'un historique de commits git, ni de note d'utilisation d'IA ou de decision log dans le brief.
- Piste d'amélioration : Fournir un journal de commits (≥3 commits significatifs) et une note IA précisant outil, prompts et validation humaine.

**Reproducibility**
- Observation : Le brief inclut le SQL et les checks, mais il n'y a pas d'instructions de clonage/README ni d'indication que les chemins ou dépendances sont génériques.
- Piste d'amélioration : Ajouter un README avec étapes exactes (clone → DuckDB → make check) et supprimer tout chemin codé en dur pour garantir exécution sur un clone propre.

## 3. Déclaration d'utilisation de l'IA

> La déclaration est complète et détaillée : outils nommés avec versions, étapes d'utilisation, validations reproductibles et exemples d'erreurs/écarts sont fournis. Bonne pratique de traçabilité et de validation locale — rien d'interdit détecté, la note maximale est justifiée.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain
- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Reprendre la requête de la section « Preuve » pour qu'elle s'exécute sur db/nexamart.duckdb et qu'elle produise la forme attendue (voir pistes en section 1).

---

## 5. Traçabilité

- **Run ID :** `20260622T152646Z-9f8024aa`
- **Devoir :** `S01`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `944f5df`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260622T152646Z-9f8024aa/XArsenault/`
- **Prompts (SHA-256) :**
  - `sql_extractor_system` : `90ee9e277de7a27f...`
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
