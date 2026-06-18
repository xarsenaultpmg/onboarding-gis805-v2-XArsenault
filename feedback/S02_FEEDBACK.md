# Rétroaction automatisée -- S02 (Schéma en étoile, grain et dimensions conformes : le premier modèle NexaMart)

_Générée le 2026-05-29T00:25:05+00:00 -- Run `20260529T002442Z-532ebea1`_

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

> Très bon brief : grain et étoile sont clairement définis, la validation est documentée et la recommandation business est actionnable. Améliorer la traçabilité git et ajouter des checks explicites pour les NULLs et un petit guide de reproduction.

### Observations par dimension

**Model quality**
- Observation : Le brief déclare explicitement le grain «1 ligne = 1 ligne de commande (order_number, sale_line_id)» et décrit une étoile à cinq dimensions avec mesures `quantity` et `revenue`.
- Piste d'amélioration : Ajouter une phrase justifiant le choix des clés substitut et expliquer pourquoi `order_number` est dégénéré plutôt qu'une dim_order.

**Validation quality**
- Observation : Le fichier SQL canonique est référencé et le tableau de contrôles indique : `SUM(revenue) sur fact_sales ≈ SUM(line_total) sur raw_fact_sales` et `Orphelins ... 0`.
- Piste d'amélioration : Inclure une vérification explicite des valeurs NULL et un exemple de requête traitant les valeurs manquantes (p.ex. coalesce ou condition WHERE).

**Executive justification**
- Observation : La section 'Réponse au CEO' affirme que la même jointure répond à la question mensuelle et propose une recommandation claire : industrialiser la requête et investiguer baisses >20% via drill-across.
- Piste d'amélioration : Raccourcir légèrement le texte pour respecter une longueur board brief ciblée (150–300 mots) et ajouter un KPI chiffré prioritaire pour la décision immédiate.

**Process trace**
- Observation : Le brief référence des fichiers (diagrams/schema-v1.mmd, sql/analysis/s02-first-answer.sql) et inclut un prompt IA pour générer le diagramme, mais n'indique pas l'historique git.
- Piste d'amélioration : Ajouter un petit log de commits (≥3) ou des messages de commit significatifs dans le README et préciser l'usage/validation humaine de l'IA.

**Reproducibility**
- Observation : Les chemins relatifs vers diagrammes et le fichier SQL canonique sont fournis, facilitant la reproduction du résultat par un collègue.
- Piste d'amélioration : Fournir un README pas-à-pas 'Clone → run' avec commandes exactes (ex. DuckDB load + script de checks) pour atteindre le résultat en <5 minutes.

## 3. Déclaration d'utilisation de l'IA

> La déclaration décrit clairement les modèles utilisés (p. ex. Claude Sonnet 4.6), les étapes d'utilisation et les validations humaines exécutées. Il manque cependant une section explicite sur les limites ou erreurs observées des sorties IA (comportements incorrects, hallucinations, ou besoins de prudence).

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

- **Run ID :** `20260529T002442Z-532ebea1`
- **Devoir :** `S02`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `a634588`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260529T002442Z-532ebea1/XArsenault/`
- **Prompts (SHA-256) :**
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
