# Rétroaction automatisée -- S04 (Panier d'achat et drapeaux : les patterns que l'étoile simple ne couvre pas)

_Générée le 2026-05-29T00:20:20+00:00 -- Run `20260529T001953Z-efa55432`_

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

> Très bon brief : modèle bien conçu et justifié, validations et recommandations opérationnelles claires pour le VP. Améliorer la traçabilité Git et ajouter petits KPI/tests de stabilité pour faciliter le passage en production.

### Observations par dimension

**Model quality**
- Observation : Le brief décrit clairement une junk dimension dim_order_profile (8 flags consolidés, profils nommés) et justifie le grain en gardant order_number comme dimension dégénérée.
- Piste d'amélioration : Ajouter un diagramme simple (schéma fact/dim) montrant keys et cardinalités pour clarifier l'usage opérationnel des profils.

**Validation quality**
- Observation : Le document inclut des requêtes SQL de preuve, des checks (grain_unique_fact_sales PASS) et des métriques de couverture (755/934 commandes ≈81%) avec limites documentées.
- Piste d'amélioration : Inclure une vérification explicite des valeurs NULL dans les flags et un test de stabilité temporelle (p.ex. window month-over-month) pour renforcer la robustesse.

**Executive justification**
- Observation : La section 'Réponse exécutive' donne une décision claire pour le VP Opérations (prioriser fragile et employé) et une recommandation commerciale (tester bundle Home & Garden + Books & Media).
- Piste d'amélioration : Ajouter un KPI attendu (p.ex. réduction du temps de picking ou lift attendu du bundle) pour aider le CEO à mesurer le succès du changement.

**Process trace**
- Observation : Le brief documente la pipeline (make generate/load/check) mais ne fournit pas d'historique git ni de note d'usage IA ou log de décisions détaillé.
- Piste d'amélioration : Fournir au moins 3 commits significatifs et une courte note IA indiquant outil + prompt + validation humaine dans le decision log.

**Reproducibility**
- Observation : La section 'Reproduction' donne les commandes make à exécuter et des chemins vers docs et SQL (make generate; make load; make check).
- Piste d'amélioration : Préciser les prérequis environnementaux (versions, dépendances) et éviter tout chemin codé en dur dans les scripts pour atteindre l'état 'clone → run' sans ajustement.

## 3. Déclaration d'utilisation de l'IA

> Bonne traçabilité des interactions IA avec preuve d'exécution et validation locale. Indiquez la version/modèle pour tous les agents nommés (p.ex. Cursor) et explicitez davantage les limites ou erreurs attribuables directement aux suggestions de l'IA.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain
- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Reprendre la requête de la section « Preuve » pour qu'elle s'exécute sur db/nexamart.duckdb et qu'elle produise la forme attendue (voir pistes en section 1).

---

## 5. Traçabilité

- **Run ID :** `20260529T001953Z-efa55432`
- **Devoir :** `S04`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `686d997`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260529T001953Z-efa55432/XArsenault/`
- **Prompts (SHA-256) :**
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
