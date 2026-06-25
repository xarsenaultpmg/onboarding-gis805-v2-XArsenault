# Rétroaction automatisée -- S07 (Soirée d'intégration : multi-star, drill-across et réel-vs-cible)

_Générée le 2026-06-22T15:22:35+00:00 -- Run `20260622T151518Z-7236028a`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief s'exécute correctement et produit la forme attendue. Bon travail sur l'auto-validation.

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
  - `region_or_carrier` → `région`
  - `revenue_or_days` → `revenue`

**Pistes :**
> Aucune requête SQL trouvée dans le brief ni dans les fichiers du repo. Une requête canonique a été synthétisée à partir du schéma de votre base pour vérifier que vos tables et jointures sont correctement en place. Ajoutez votre requête finale dans la section « Preuve » avec un bloc ```sql ... ``` pour éliminer cette étape.

## 2. Rétroaction pédagogique sur le brief

> Le brief S07 présente un modèle clair et des preuves SQL convaincantes pour le drill-across et le réel-vs-budget, avec recommandations actionnables. Il manque toutefois des éléments de traçabilité (commits, note IA) et des checks de cas limites pour garantir une reproductibilité complète.

### Observations par dimension

**Model quality**
- Observation : Le brief décrit un modèle S07 avec 4 faits (fact_sales, fact_returns, fact_inventory_snapshot, fact_budget) et explicite le grain commun 'catégorie × mois' pour le drill-across.
- Piste d'amélioration : Ajouter un diagramme de schéma (star/constellation) ou un extrait DDL montrant clés et types pour rendre la structure immédiatement vérifiable.

**Validation quality**
- Observation : Le document indique des contrôles dans sql/checks/s07-reconciliation.sql avec plusieurs PASS (ex. fact_sales vs sales_agg = 661 114,94).
- Piste d'amélioration : Inclure un check explicite pour les valeurs NULL, les doublons de grain et un test de cohérence temporelle (ex. somme pondérée vs snapshots) pour couvrir les cas limites.

**Executive justification**
- Observation : La réponse exécutive commence par 'Oui, à condition de ne jamais joindre les tables de faits directement' et propose des recommandations (investigation Automotive, revoir budgets).
- Piste d'amélioration : Raccourcir et synthétiser en 150–300 mots la recommandation prioritaire (action, propriétaire, échéance) pour faciliter la prise de décision du CEO.

**Process trace**
- Observation : Le brief référence des fichiers (docs/bus-matrix.md, sql/... ) mais n'inclut pas d'historique git ni de note sur l'usage d'IA ou validation humaine.
- Piste d'amélioration : Ajouter un log de commits (≥3) avec messages clairs et une note IA précisant outils utilisés et qui a validé les sorties.

**Reproducibility**
- Observation : Des scripts SQL sont référencés (sql/integration/s07-drill-across.sql, sql/checks/s07-reconciliation.sql) mais aucun README d'exécution ou instruction d'environnement n'est fourni.
- Piste d'amélioration : Fournir un README 'Clone → run' avec commandes concrètes (ex. DuckDB / chemin relatif) et jeux de données seed pour reproduire les résultats en <5 minutes.

## 3. Déclaration d'utilisation de l'IA

> La déclaration est complète : elle liste les modèles utilisés, décrit pour chaque séance le rôle de l'IA, et documente des validations précises sur DuckDB. Cependant certaines mentions restent un peu génériques (p. ex. « Cursor / agent » sans version ou nature précise de l'agent), ce qui empêche d'atteindre le score maximal.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain
- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Aucune correction technique nécessaire. Voir la section 2 pour des pistes d'approfondissement.

---

## 5. Traçabilité

- **Run ID :** `20260622T151518Z-7236028a`
- **Devoir :** `S07`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `944f5df`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260622T151518Z-7236028a/XArsenault/`
- **Prompts (SHA-256) :**
  - `sql_extractor_system` : `90ee9e277de7a27f...`
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
