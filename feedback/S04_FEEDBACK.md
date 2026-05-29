# Rétroaction automatisée -- S04 (Panier d'achat et drapeaux : les patterns que l'étoile simple ne couvre pas)

_Générée le 2026-05-29T13:01:54+00:00 -- Run `20260529T125432Z-0258cabb`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief s'exécute correctement et produit la forme attendue. Bon travail sur l'auto-validation.

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

- Colonnes retournées : `profile_name, order_count, total_revenue`
- Correspondance avec les colonnes attendues :
  - `profile_label` → `profile_name`
  - `count` → `order_count`
- Présence de NULLs dans des colonnes de groupement : `profile_name` =0. Pensez à documenter le traitement de ces cas.

## 2. Rétroaction pédagogique sur le brief

> Très bon brief : le modèle est bien décrit, les validations sont reproductibles et les recommandations métiers sont actionnables. Compléter la traçabilité (commits et decision log) et ajouter quelques contrôles automatiques de cas limites améliorerait la robustesse.

### Observations par dimension

**Model quality**
- Observation : Le brief indique clairement le grain, conserve order_number comme dimension dégénérée et définit une junk dimension dim_order_profile avec 8 flags et profils nommés.
- Piste d'amélioration : Ajouter un diagramme schématique (star schema) montrant clés et relations pour faciliter la revue technique rapide.

**Validation quality**
- Observation : Des requêtes SQL d'agrégation et de paires produits sont fournies et des checks sont listés (grain unique, TABLE_EXISTS, couverture profile_key avec pourcentages).
- Piste d'amélioration : Ajouter au moins un contrôle d'intégrité traitant explicitement les NULLs dans profile_key et un test automatisé pour les cas limites (e.g. commandes mono-ligne).

**Executive justification**
- Observation : Le résumé exécutif formule des décisions claires : prioriser fragile et achat employé pour l'opération et tester un bundle Home & Garden + Books & Media.
- Piste d'amélioration : Condenser légèrement en 150–250 mots et quantifier l'impact attendu (ex. gain % sur SLA ou uplift de panier) pour renforcer la décision.

**Process trace**
- Observation : La section Reproduction liste les commandes make (generate/load/check) mais n'inclut pas d'historique git ni de note IA ou decision log détaillé.
- Piste d'amélioration : Inclure un journal de décision (CHANGELOG) et pousser ≥3 commits incrémentaux avec messages descriptifs ; documenter l'usage d'outils IA si utilisé.

**Reproducibility**
- Observation : Des commandes 'make' et un chemin vers les scripts SQL sont fournis pour reproduire (make generate, make load, make check, make sql).
- Piste d'amélioration : Ajouter un README minimal indiquant le temps d'exécution attendu, les prérequis (DuckDB/version Python) et vérifier l'absence de chemins codés en dur.

## 3. Déclaration d'utilisation de l'IA

> La déclaration documente clairement les outils (avec versions parfois) et décrit précisément quand et comment l'IA a été utilisée et validée. Il manque cependant une section explicite sur les limites de l'IA ou les erreurs observées lors des interactions.

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

- **Run ID :** `20260529T125432Z-0258cabb`
- **Devoir :** `S04`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `a634588`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260529T125432Z-0258cabb/XArsenault/`
- **Prompts (SHA-256) :**
  - `sql_extractor_system` : `90ee9e277de7a27f...`
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
