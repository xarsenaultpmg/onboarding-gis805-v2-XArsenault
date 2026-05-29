# Rétroaction automatisée -- S03 (Dimensions à changement lent : garder la vérité historique chez NexaMart)

_Générée le 2026-05-29T00:09:10+00:00 -- Run `20260529T000845Z-f60682c0`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

> ⚠️ **Avertissement instructeur (à retirer avant publication) :** cette analyse a été générée avec `--skip-pull`. Le contenu correspond au commit local et **n'est peut-être pas la dernière version poussée par l'étudiant·e**.

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief n'a pas pu être validée automatiquement. Quelques pistes constructives ci-dessous pour vous aider à la rendre exécutable et alignee avec la question posée.

_Observation technique : erreur d'exécution SQL: Catalog Error: Table with name demo_dim_customer_type1 does not exist!_

<details><summary>Requête analysée — cliquez pour déplier</summary>

```sql
-- Segment = dernière valeur connue (écrasement)
SELECT c.segment, ROUND(SUM(f.line_total), 2) AS total_revenue
FROM raw_fact_sales f
JOIN demo_dim_customer_type1 c ON f.customer_id = c.customer_id
GROUP BY 1 ORDER BY 2 DESC;
```

</details>


**Pistes :**
> Tables référencées dans votre requête mais absentes de la base : `demo_dim_customer_type1`, `raw_fact_sales`.
> Tables disponibles dans `db/nexamart.duckdb` : `dim_channel`, `dim_customer`, `dim_date`, `dim_product`, `dim_store`, `fact_sales`, `raw_bridge_campaign_allocation`, `raw_bridge_customer_segment`, `raw_customer_changes`, `raw_customer_profile_bands`, `raw_customer_scd3_history`, `raw_dim_channel`, `raw_dim_customer`, `raw_dim_date`, `raw_dim_geography`, `raw_dim_product`, `raw_dim_segment_outrigger`, `raw_dim_store`, `raw_fact_budget`, `raw_fact_daily_inventory`.
> Pour `demo_dim_customer_type1`, peut-être vouliez-vous : `dim_customer` ?
> Pour `raw_fact_sales`, peut-être vouliez-vous : `fact_sales` ?

## 2. Rétroaction pédagogique sur le brief

> Très bon brief : la politique SCD est claire, la démonstration chiffrée et la recommandation exécutive sont présentes. Compléter la traçabilité (commits et decision log) et automatiser les checks pour une reproductibilité parfaite.

### Observations par dimension

**Model quality**
- Observation : Le brief documente une politique SCD Type 2 pour segment, city et région, clé substitut customer_key et jointure temporelle (valid_from / valid_to) entre faits et dimension.
- Piste d'amélioration : Préciser le grain exact des dimensions et des faits (ex. grain de la ligne de vente vs. commande) et ajouter un diagramme du schéma pour lever toute ambiguïté structurelle.

**Validation quality**
- Observation : Des scripts SQL de démonstration sont fournis (sql/scd/type1_vs_type2_demo.sql) et des contrôles PASS listés (unicité customer_key, une version courante, grain fact_sales).
- Piste d'amélioration : Ajouter des tests automatisés (CI) qui exécutent ces checks et valident les cas limites (NULLs, chevauchements de périodes, dates frontières).

**Executive justification**
- Observation : La section 'Réponse exécutive' répond directement au CEO et recommande d'adopter SCD2 pour les attributs critiques avec exemples chiffrés (écart Gold = 129,78 $ et exemple client CUS-00152).
- Piste d'amélioration : Raccourcir légèrement la partie technique et ajouter une phrase chiffrée sur l'impact opérationnel attendu (ex. % d'accords marketing corrigés) pour renforcer la décision.

**Process trace**
- Observation : Le brief référence des fichiers et l'exécution sur db/nexamart.duckdb mais n'inclut pas d'historique git ni de note IA détaillée sur les validations humaines.
- Piste d'amélioration : Inclure un journal de décisions et l'historique git (≥3 commits significatifs) ainsi qu'une note IA précisant outils utilisés et contrôles manuels effectués.

**Reproducibility**
- Observation : Les chemins vers les scripts et la base (db/nexamart.duckdb) et le seed sont indiqués, facilitant la reproduction avec un ajustement mineur.
- Piste d'amélioration : Ajouter un README pas-à-pas indiquant comment cloner, charger le dump DuckDB et exécuter les scripts pour obtenir les mêmes résultats en <5 minutes.

## 3. Déclaration d'utilisation de l'IA

> La déclaration documente clairement les modèles employés, les étapes d'usage et les validations manuelles reproduites sur la base locale. Il manque en revanche toute mention explicite des limites, biais ou erreurs observées liées aux suggestions de l'IA.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain

**Sujets à ajouter ou expliciter pour la prochaine itération :**

- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Reprendre la requête de la section « Preuve » pour qu'elle s'exécute sur db/nexamart.duckdb et qu'elle produise la forme attendue (voir pistes en section 1).
- Compléter i-usage.md en y ajoutant : limites ou erreurs observées.

---

## 5. Traçabilité

- **Run ID :** `20260529T000845Z-f60682c0`
- **Devoir :** `S03`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `686d997`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260529T000845Z-f60682c0/XArsenault/`
- **Prompts (SHA-256) :**
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
