# Rétroaction automatisée -- S04 (Panier d'achat et drapeaux : les patterns que l'étoile simple ne couvre pas)

_Générée le 2026-05-29T00:09:41+00:00 -- Run `20260529T000917Z-46f8532c`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

> ⚠️ **Avertissement instructeur (à retirer avant publication) :** cette analyse a été générée avec `--skip-pull`. Le contenu correspond au commit local et **n'est peut-être pas la dernière version poussée par l'étudiant·e**.

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief n'a pas pu être validée automatiquement. Quelques pistes constructives ci-dessous pour vous aider à la rendre exécutable et alignee avec la question posée.

_Observation technique : erreur d'exécution SQL: Catalog Error: Table with name dim_order_profile does not exist!_

<details><summary>Requête analysée — cliquez pour déplier</summary>

```sql
SELECT
    p.profile_name,
    COUNT(DISTINCT f.order_number) AS order_count,
    ROUND(SUM(f.revenue), 2) AS total_revenue
FROM fact_sales AS f
INNER JOIN dim_order_profile AS p ON f.profile_key = p.profile_key
GROUP BY 1
ORDER BY 2 DESC
LIMIT 8;
```

</details>


**Pistes :**
> Tables référencées dans votre requête mais absentes de la base : `dim_order_profile`.
> Tables disponibles dans `db/nexamart.duckdb` : `dim_channel`, `dim_customer`, `dim_date`, `dim_product`, `dim_store`, `fact_sales`, `raw_bridge_campaign_allocation`, `raw_bridge_customer_segment`, `raw_customer_changes`, `raw_customer_profile_bands`, `raw_customer_scd3_history`, `raw_dim_channel`, `raw_dim_customer`, `raw_dim_date`, `raw_dim_geography`, `raw_dim_product`, `raw_dim_segment_outrigger`, `raw_dim_store`, `raw_fact_budget`, `raw_fact_daily_inventory`.

## 2. Rétroaction pédagogique sur le brief

> Très bon brief: modèle solide, validations reproductibles et recommandations métiers claires qui répondent à la question CEO. Compléter la traçabilité (commits et déclaration d'usage IA) et préciser KPI du pilote pour faciliter la prise de décision.

### Observations par dimension

**Model quality**
- Observation : Le brief définit une junk dimension dim_order_profile avec 8 flags consolidés, indique le grain (order_number dégénéré) et justifie le choix par le fait que 99 profils observés sur 256 combinaisons théoriques.
- Piste d'amélioration : Ajouter un exemple de schéma (liste des colonnes de dim_order_profile et types) et expliciter une contrainte d'unicité pour profile_key.

**Validation quality**
- Observation : Le document inclut des requêtes SQL de validation, des contrôles PASS (grain unique: 3 000 lignes, TABLE_EXISTS) et la couverture profile_key documentée (755/934 ≈ 81%).
- Piste d'amélioration : Ajouter un test SQL pour les cas limites (NULL profile_key impact sur ratios) et une vérification des doublons dans la junk dim.

**Executive justification**
- Observation : La section 'Réponse exécutive' propose deux actions claires au VP opérations (pilote pour profils 'Achat employé' et 'Livraison fragile' et test merchandising) en langage métier.
- Piste d'amélioration : Préciser les KPI cibles du pilote (ex. réduction du temps de picking, uplift % attendu pour le bundle) pour faciliter la décision.

**Process trace**
- Observation : La reproduction liste les commandes make (generate/load/check) mais il n'y a aucune trace des commits git ni de note IA déclarée.
- Piste d'amélioration : Inclure l'historique git (≥3 commits avec messages) et une note IA précisant outils utilisés et validation humaine.

**Reproducibility**
- Observation : Les instructions 'make generate / make load / make check' et la commande pour exécuter la SQL sont fournies, avec références de docs et scripts listés.
- Piste d'amélioration : Ajouter un README minimal indiquant les prérequis exacts (version DuckDB, dépendances) et un test automatisé qui s'exécute de bout en bout sur un clone propre.

_Quelques points appellent une attention particulière lors de la prochaine itération : absence_de_journal_git, note_IA_non_fournie._

## 3. Déclaration d'utilisation de l'IA

> La déclaration documente bien les outils (avec versions) et les étapes d'utilisation, et décrit clairement comment les résultats ont été validés localement. Par contre elle ne mentionne pas explicitement les limites, biais ou erreurs constatées du comportement de l'IA (ex. hallucinations, réponses incorrectes, ou situations à risque).

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain

**Sujets à ajouter ou expliciter pour la prochaine itération :**

- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Reprendre la requête de la section « Preuve » pour qu'elle s'exécute sur db/nexamart.duckdb et qu'elle produise la forme attendue (voir pistes en section 1).
- Réviser le brief en tenant compte des observations par dimension de la section 2.
- Compléter i-usage.md en y ajoutant : limites ou erreurs observées.

---

## 5. Traçabilité

- **Run ID :** `20260529T000917Z-46f8532c`
- **Devoir :** `S04`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `686d997`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260529T000917Z-46f8532c/XArsenault/`
- **Prompts (SHA-256) :**
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
