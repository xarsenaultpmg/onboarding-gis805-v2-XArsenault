# Rétroaction automatisée -- S04 (Panier d'achat et drapeaux : les patterns que l'étoile simple ne couvre pas)

_Générée le 2026-05-29T13:01:55+00:00 -- Run `20260529T125427Z-dfc5d65b`_

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

> Le brief présente un modèle dimensionnel clair avec preuves SQL solides et recommandations opérationnelles actionnables. Améliorer la traçabilité du processus (commits + note IA) et ajouter KPI attendus pour cadrer les tests.

### Observations par dimension

**Model quality**
- Observation : Le brief indique un grain clair (clé composite order_number + sale_line_id), définit une junk dimension dim_order_profile avec 8 flags et justifie le choix par la couverture réelle (99 profils observés sur 256 possibles).
- Piste d'amélioration : Ajouter un diagramme simple (ERD) montrant les relations fact_sales ↔ dim_order_profile et les clés pour faciliter la revue structurelle.

**Validation quality**
- Observation : Le document fournit des requêtes SQL de validation et des checks : grain unique (3 000 lignes, grain_unique_fact_sales PASS), existence de dim_order_profile (99 lignes) et couverture profile_key (755/934 ~81%).
- Piste d'amélioration : Inclure un test automatique pour les cas limites (NULL profile_key) et un assert sur la distribution attendue des pairs produits pour détecter régressions.

**Executive justification**
- Observation : La section 'Réponse exécutive' présente des actions claires pour le VP Opérations (prioriser fragile et employé) et une recommandation merchandising basée sur co-occurrence produit, en langage décisionnel.
- Piste d'amélioration : Ajouter un KPI quantitatif attendu pour chaque action (ex. réduction du time-to-pick de X %, hausse du taux d'attachement de Y %) pour cadrer l'expérimentation.

**Process trace**
- Observation : Le brief documente la pipeline (make generate/load/check) mais n'inclut pas d'historique git incrémental ni de note IA détaillée.
- Piste d'amélioration : Ajouter l'historique git avec ≥3 commits significatifs et une note IA précisant outil/usage et validations humaines effectuées.

**Reproducibility**
- Observation : Les instructions de reproduction sont fournies (make generate; make load; make check; make sql FILE=...), facilitant la reproduction avec un clone propre.
- Piste d'amélioration : Documenter explicitement les prérequis (versions, dépendances) et garantir l'absence de chemins codés en dur dans les scripts.

## 3. Déclaration d'utilisation de l'IA

> La déclaration est détaillée sur les modèles utilisés, les étapes d'usage et les méthodes de validation par l'humain. Elle n'indique cependant pas clairement les limites du modèle ni des erreurs ou hallucinations observées lors des interactions.

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

- **Run ID :** `20260529T125427Z-dfc5d65b`
- **Devoir :** `S04`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `a634588`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260529T125427Z-dfc5d65b/XArsenault/`
- **Prompts (SHA-256) :**
  - `sql_extractor_system` : `90ee9e277de7a27f...`
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
