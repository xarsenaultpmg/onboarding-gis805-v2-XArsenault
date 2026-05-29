# Rétroaction automatisée -- S02 (Schéma en étoile, grain et dimensions conformes : le premier modèle NexaMart)

_Générée le 2026-05-29T00:08:39+00:00 -- Run `20260529T000815Z-d3e6663b`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

> ⚠️ **Avertissement instructeur (à retirer avant publication) :** cette analyse a été générée avec `--skip-pull`. Le contenu correspond au commit local et **n'est peut-être pas la dernière version poussée par l'étudiant·e**.

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief s'exécute correctement et produit la forme attendue. Bon travail sur l'auto-validation.

<details><summary>Requête analysée — cliquez pour déplier</summary>

```sql
SELECT
    p.category,
    s."région" AS region,
    d.quarter,
    SUM(f.revenue) AS total_sales,
    COUNT(*)       AS line_count
FROM fact_sales AS f
INNER JOIN dim_product AS p
    ON f.product_key = p.product_key
INNER JOIN dim_store AS s
    ON f.store_key = s.store_key
INNER JOIN dim_date AS d
    ON f.date_key = d.date_key
GROUP BY
    p.category,
    s."région",
    d.quarter
ORDER BY
    total_sales DESC;
```

</details>

- Colonnes retournées : `category, region, quarter, total_sales, line_count`
- Correspondance avec les colonnes attendues :
  - `category` → `category`
  - `region` → `region`
  - `quarter` → `quarter`
  - `revenue` → `total_sales`
- Présence de NULLs dans des colonnes de groupement : `category` =0, `region` =0, `quarter` =0. Pensez à documenter le traitement de ces cas.

## 2. Rétroaction pédagogique sur le brief

> Très bon brief : grain et étoile sont clairement définis, la requête et les contrôles montrent que la question CEO est répétable. Améliorer la traçabilité git et fournir des instructions de reproduction courtes pour faciliter la mise en production.

### Observations par dimension

**Model quality**
- Observation : Le brief précise un grain '1 ligne = 1 ligne de commande' (order_number, sale_line_id), une étoile à cinq dimensions et les mesures (quantity, revenue).
- Piste d'amélioration : Documenter brièvement le raisonnement derrière l'absence de dim_order et expliciter tout choix de clés substitut pour faciliter la revue architecturale.

**Validation quality**
- Observation : Le SQL fourni calcule category × region × quarter et le tableau de contrôles indique: SUM(revenue) ≈ SUM(line_total), 0 orphelins et grain unique (validation/checks.sql).
- Piste d'amélioration : Ajouter des checks explicites pour les valeurs NULL, les dates hors plage et un jeu de tests automatisés minimal pour reproduire les contrôles.

**Executive justification**
- Observation : La 'Réponse au CEO' explique en langage métier que la même jointure produit les résultats souhaités et propose une recommandation concrète (investiguer baisses >20%).
- Piste d'amélioration : Préciser un KPI cible et un seuil opérationnel (ex.: volume minimal pour prioriser une investigation) pour faciliter la décision du board.

**Process trace**
- Observation : Le brief référence des fichiers et diagrammes (diagrams/schema-v1.mmd, sql/analysis/s02-first-answer.sql) et inclut une invite utilisée avec l'assistant IA.
- Piste d'amélioration : Fournir l'historique git (≥3 commits) avec messages signifiants et indiquer la validation humaine des sorties IA dans le decision log.

**Reproducibility**
- Observation : Le brief mentionne des chemins de fichiers relatifs (sql/analysis/..., diagrams/...) mais n'inclut pas d'instructions 'clone → run' ni README d'exécution.
- Piste d'amélioration : Ajouter un README minimal indiquant les commandes pour cloner, lancer les checks (ex. script DuckDB) et reproduire les résultats en <5 minutes.

## 3. Déclaration d'utilisation de l'IA

> La déclaration est détaillée et documente bien les modèles utilisés, les étapes et les validations manuelles. En revanche, elle ne décrit pas explicitement les limites rencontrées ni les erreurs observées lors des interactions avec l'IA.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain

**Sujets à ajouter ou expliciter pour la prochaine itération :**

- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Compléter i-usage.md en y ajoutant : limites ou erreurs observées.

---

## 5. Traçabilité

- **Run ID :** `20260529T000815Z-d3e6663b`
- **Devoir :** `S02`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `686d997`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260529T000815Z-d3e6663b/XArsenault/`
- **Prompts (SHA-256) :**
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
