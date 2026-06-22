# Rétroaction automatisée -- S11 (Processus de modélisation, documentation et revue de design)

_Générée le 2026-06-22T14:20:53+00:00 -- Run `20260622T141241Z-ebab080d`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief n'a pas pu être validée automatiquement. Quelques pistes constructives ci-dessous pour vous aider à la rendre exécutable et alignee avec la question posée.

_Observation technique : erreur d'exécution SQL: Parser Error: syntax error at or near ".."_

<details><summary>Requête analysée — cliquez pour déplier</summary>

```sql
-- TODO : remplacez par votre requête réelle
SELECT ...
FROM fact_...
```

</details>


**Pistes :**
> Tables référencées dans votre requête mais absentes de la base : `fact_`.
> Tables disponibles dans `db/nexamart.duckdb` : `bridge_customer_segment`, `dim_channel`, `dim_customer`, `dim_customer_scd3`, `dim_date`, `dim_order_profile`, `dim_product`, `dim_segment_outrigger`, `dim_store`, `fact_budget`, `fact_daily_inventory`, `fact_inventory_snapshot`, `fact_order_pipeline`, `fact_orders_transaction`, `fact_promo_exposure`, `fact_returns`, `fact_sales`, `raw_bridge_campaign_allocation`, `raw_bridge_customer_segment`, `raw_customer_changes`.
> Pour `fact_`, peut-être vouliez-vous : `fact_budget`, `fact_daily_inventory`, `fact_inventory_snapshot`, `fact_order_pipeline`, `fact_orders_transaction`, `fact_promo_exposure`, `fact_returns`, `fact_sales` ?

## 2. Rétroaction pédagogique sur le brief

> Le brief est actuellement un squelette contenant des placeholders et n'apporte aucune preuve ni justification exécutive. Remplissez les sections clés (réponse exécutive, livrables, requêtes de preuve et instructions de reproduction) et réessayez la soumission.

### Observations par dimension

**Model quality**
- Observation : Le brief ne présente aucun schéma ni description du modèle ; la section 'Livrables de handoff' contient uniquement des TODO et des commentaires.
- Piste d'amélioration : Compléter la section avec la description du schéma : table de faits principale, grain, dimensions, SCD utilisés et diagramme ER minimal.

**Validation quality**
- Observation : Aucune requête SQL exécutable fournie : la section 'Preuve — KPI principal' contient un placeholder 'SELECT ... FROM fact_...'.
- Piste d'amélioration : Fournir et exécuter une requête de validation concrète (alias net_revenue ou pct_delivery) et coller le résultat observé.

**Executive justification**
- Observation : La section 'Réponse exécutive' est vide et limitée à un commentaire TODO demandant 3–4 phrases directes au CEO.
- Piste d'amélioration : Rédiger 2–3 phrases en langage décisionnel répondant clairement à la question du CEO, incluant au moins une recommandation actionnable.

**Process trace**
- Observation : Aucune trace de commits, de note IA ou de decision-log effective n'est fournie dans le brief (seul un placeholder pour 'decision-log').
- Piste d'amélioration : Inclure un résumé des commits (≥3) et une note IA précisant outils et validation humaine, et joindre le decision-log avec exemples.

**Reproducibility**
- Observation : Instructions de reproduction absentes : la section 'Comment reproduire l'entrepôt' n'est pas remplie et renvoie à des TODO.
- Piste d'amélioration : Ajouter des instructions pas-à-pas (commandes make, chemin DuckDB, checks) permettant à un tiers de reproduire le résultat depuis un clone.

_Quelques points appellent une attention particulière lors de la prochaine itération : contenu_incomplet._

## 3. Déclaration d'utilisation de l'IA

> La déclaration documente clairement les outils (avec versions pour plusieurs modèles), les étapes d'utilisation et les vérifications humaines par exécution locale. En revanche, elle ne signale pas explicitement de limites ou d'erreurs observées liées aux sorties IA.

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

- **Run ID :** `20260622T141241Z-ebab080d`
- **Devoir :** `S11`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `f06e67e`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260622T141241Z-ebab080d/XArsenault/`
- **Prompts (SHA-256) :**
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
  - `sql_extractor_system` : `90ee9e277de7a27f...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
