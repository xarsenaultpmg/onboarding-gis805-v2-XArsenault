# Rétroaction automatisée -- S08 (Ponts pondérés, SCD avancés et relations many-to-many chez NexaMart)

_Générée le 2026-06-22T13:54:35+00:00 -- Run `20260622T134648Z-21dabff8`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief s'exécute correctement et produit la forme attendue. Bon travail sur l'auto-validation.

<details><summary>Requête analysée — cliquez pour déplier</summary>

```sql
-- ============================================================
-- S08 -- Allocation ponderee du revenu par segment
-- ============================================================
-- Source d'analyse : db/nexamart.duckdb apres .\run.ps1 generate/load.
-- Objectif : montrer le fan-out de la jointure naive, puis corriger
-- l'allocation avec bridge_customer_segment.weight.
-- ============================================================

WITH segment_revenue AS (
    SELECT
        seg.segment,
        SUM(f.line_total) AS revenue_naive,
        SUM(CASE WHEN b.is_primary THEN f.line_total ELSE 0 END) AS revenue_primary,
        SUM(f.line_total * b.weight) AS revenue_weighted
    FROM fact_sales AS f
    JOIN bridge_customer_segment AS b
      ON b.customer_key = f.customer_key
    JOIN dim_segment_outrigger AS seg
      ON seg.segment_key = b.segment_key
    GROUP BY seg.segment
),
total_sales AS (
    SELECT SUM(line_total) AS total_revenue
    FROM fact_sales
),
campaign_spend AS (
    -- planned_spend is already allocated per campaign x segment row in S08.
    SELECT
        segment,
        SUM(planned_spend) AS allocated_spend
    FROM raw_bridge_campaign_allocation
    GROUP BY segment
)
SELECT
    sr.segment,
    ROUND(sr.revenue_naive, 2) AS revenue_naive,
    ROUND(sr.revenue_primary, 2) AS revenue_primary,
    ROUND(sr.revenue_weighted, 2) AS revenue_weighted,
    ROUND(COALESCE(cs.allocated_spend, 0), 2) AS campaign_allocated_spend,
    ROUND(sr.revenue_naive - sr.revenue_weighted, 2) AS naive_overstatement,
    ROUND(sr.revenue_naive / NULLIF(sr.revenue_weighted, 0), 4) AS naive_to_weighted_ratio,
    ROUND(sr.revenue_weighted / NULLIF(ts.total_revenue, 0), 4) AS weighted_share_of_total
FROM segment_revenue AS sr
CROSS JOIN total_sales AS ts
LEFT JOIN campaign_spend AS cs
  ON cs.segment = sr.segment
ORDER BY sr.revenue_weighted DESC
```

</details>

- Colonnes retournées : `segment, revenue_naive, revenue_primary, revenue_weighted, campaign_allocated_spend, naive_overstatement, naive_to_weighted_ratio, weighted_share_of_total`
- Correspondance avec les colonnes attendues :
  - `segment` → `segment`
  - `revenue` → `revenue_naive`
- Présence de NULLs dans des colonnes de groupement : `segment` =0. Pensez à documenter le traitement de ces cas.

**Pistes :**
> Aucun bloc ```sql ... ``` détecté et l'extracteur LLM n'a trouvé aucune requête. Encadrez votre requête finale dans la section « Preuve » avec un bloc ```sql ... ``` pour fiabiliser l'auto-validation.
> Extracteur LLM : Le brief ne contient aucune requête SQL explicite — seuls des fichiers référencés et des tableaux de résultats sont fournis, donc aucune requête principale à extraire.
> Requête extraite depuis les fichiers SQL du repo (`sql\analysis\basket_pairs.sql`, `sql\analysis\s02-first-answer.sql`, `sql\bridges\bridge_customer_segment.sql`, `sql\bridges\s08-weighted-allocation.sql`, `sql\checks\s07-reconciliation.sql`) — aucun bloc SQL inline dans le brief. Ajoutez un bloc ```sql ... ``` dans la section « Preuve » de votre brief pour fiabiliser l'auto-validation à l'avenir.

## 2. Rétroaction pédagogique sur le brief

> Le brief présente un modèle solide et des vérifications convaincantes démontrant que l'attribution pondérée conserve le total réel; la recommandation au CEO est claire et chiffrée. Pour atteindre l'excellence complète, ajoutez un historique de commits, une note IA/validation humaine et des instructions reproductibles pas à pas.

### Observations par dimension

**Model quality**
- Observation : Vous décrivez un bridge pondéré (bridge_customer_segment) avec SUM(weight) = 1,0 et un dim_customer_scd3 pour comparer previous/current.
- Piste d'amélioration : Ajouter un diagramme de schéma (crow's foot) ou dictionnaire de colonnes pour clarifier les clés et contraintes implémentées.

**Validation quality**
- Observation : Vous fournissez des scripts de vérification (sql/checks/s08-weighted-reconciliation.sql) montrant que le total pondéré revient au total réel et que 0 client est en anomalie.
- Piste d'amélioration : Inclure un test automatisé reproductible (CI) qui exécute ces checks sur un clone propre.

**Executive justification**
- Observation : La recommandation au CEO est explicite : utiliser l'attribution pondérée pour les rapports board et interdire la jointure naïve qui crée 224 167,61 $ de revenu fictif.
- Piste d'amélioration : Ajouter un court plan d'action chiffré (timeline et impact budgétaire) pour faciliter la décision du board.

**Process trace**
- Observation : Le brief référence des fichiers SQL et un seed `team_[REDACTED-PHONE]` mais n'indique pas d'historique de commits ni de note IA détaillée.
- Piste d'amélioration : Fournir l'historique git (≥3 commits incrémentaux) et une note IA précisant outils/usage et validation humaine.

**Reproducibility**
- Observation : Vous indiquez les chemins des scripts (sql/bridges/... et sql/checks/...) mais le seed est référencé sans instructions de reproduction complètes.
- Piste d'amélioration : Documenter exactement comment cloner, charger le seed et exécuter les checks (README avec commandes et dépendances).

_Quelques points appellent une attention particulière lors de la prochaine itération : aucun_historique_git_fourni, seed_de_donnees_referencE_sans_instructions_de_reproduction._

## 3. Déclaration d'utilisation de l'IA

> Très bonne déclaration : les outils (avec versions), les étapes d'utilisation, les validations humaines et des limites de données sont documentées de façon claire et répétée. Veillez seulement à préciser la version/model quand vous évoquez des «agents/Cursor» pour éviter toute ambiguïté sur l'outil exact employé.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain
- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Réviser le brief en tenant compte des observations par dimension de la section 2.

---

## 5. Traçabilité

- **Run ID :** `20260622T134648Z-21dabff8`
- **Devoir :** `S08`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `f06e67e`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260622T134648Z-21dabff8/XArsenault/`
- **Prompts (SHA-256) :**
  - `sql_extractor_system` : `90ee9e277de7a27f...`
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
