# Rétroaction automatisée -- S04 (Panier d'achat et drapeaux : les patterns que l'étoile simple ne couvre pas)

_Générée le 2026-06-22T15:11:08+00:00 -- Run `20260622T150322Z-f6a7bca4`_

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

> Brief solide et orienté décisionnel : modèle bien justifié (junk dim & dégénérée), validations exécutées et recommandations actionnables. Améliorer la traçabilité des décisions (commits + note IA) et détailler quelques tests limites pour renforcer la confiance opérationnelle.

### Observations par dimension

**Model quality**
- Observation : « Les commandes opérationnelles ne se lisent pas en huit colonnes booléennes. Sur notre seed, 99 profils distincts existent réellement (sur 256 combinaisons théoriques). » — justification et choix de junk dimension exposés.
- Piste d'amélioration : Ajouter un schéma graphique (ERD) montrant les clés et exemples de valeurs de profile_key pour faciliter la revue technique par l'équipe.

**Validation quality**
- Observation : « Grain fact_sales : 3 000 lignes, clé composite (order_number, sale_line_id) unique (grain_unique_fact_sales PASS). » — contrôles exécutés et résultats reportés.
- Piste d'amélioration : Compléter les tests en montrant explicitement le traitement des NULLs pour profile_key dans la requête principale et un test d'intégrité pour sommes/aggrégats extrêmes.

**Executive justification**
- Observation : « Décision proposée au VP Opérations : renforcer capacité picking/livraison pour les profils fragile et employé ; lancer un test merchandising Home & Garden + Books & Media en bundle. » — recommandation claire et actionnable.
- Piste d'amélioration : Ajouter un chiffrage d'impact rapide (coût estimé vs. gain attendu ou KPI à suivre) pour prioriser la mise en œuvre.

**Process trace**
- Observation : « Pipeline : make generate → make load → make check (Windows : .\run.ps1). » — process d'exécution décrit mais pas d'historique de commits ni note IA.
- Piste d'amélioration : Inclure un petit log de commits (≥3) avec messages significatifs et une note indiquant l'usage d'IA/outils et la validation humaine effectuée.

**Reproducibility**
- Observation : Section Reproduction : « make generate; make load; make check; make sql FILE=sql/analysis/basket_pairs.sql » — instructions de reproduction fournies.
- Piste d'amélioration : Préciser l'environnement exact (DuckDB/version, dépendances) et vérifier l'absence de chemins codés en dur dans les scripts pour atteindre l'excellent.

## 3. Déclaration d'utilisation de l'IA

> La déclaration décrit bien quels modèles ont été utilisés, à quelles étapes et comment vous avez validé les sorties avec des exécutions et relectures locales. En revanche elle ne documente pas clairement les limites, erreurs ou comportements inattendus des outils IA — ajoutez des exemples concrets d'erreurs/limitations observées et comment vous y avez remédié.

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

- **Run ID :** `20260622T150322Z-f6a7bca4`
- **Devoir :** `S04`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `944f5df`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260622T150322Z-f6a7bca4/XArsenault/`
- **Prompts (SHA-256) :**
  - `sql_extractor_system` : `90ee9e277de7a27f...`
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
