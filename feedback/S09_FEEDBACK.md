# Rétroaction automatisée -- S09 (Les quatre types de tables de faits : transaction, snapshot, accumulating et factless)

_Générée le 2026-06-22T14:07:19+00:00 -- Run `20260622T135856Z-2faa194c`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief s'exécute correctement et produit la forme attendue. Bon travail sur l'auto-validation.

<details><summary>Requête analysée — cliquez pour déplier</summary>

```sql
-- ── Étape 2 : Funnel de complétion par jalon ─────────────────
-- Calcule le % des commandes ayant atteint chaque jalon.
--        Utilisez les colonnes booléennes reached_payment, reached_pick,
--        reached_ship, reached_delivery.
--        Attendu : pct_payment ≥ pct_pick ≥ pct_ship ≥ pct_delivery

SELECT
    COUNT(*)                                            AS total_commandes,
    SUM(reached_payment::INT)                           AS nb_payment,
    SUM(reached_pick::INT)                              AS nb_pick,
    SUM(reached_ship::INT)                              AS nb_ship,
    SUM(reached_delivery::INT)                          AS nb_delivery,
    ROUND(100.0 * SUM(reached_payment::INT)  / COUNT(*), 1) AS pct_payment,
    ROUND(100.0 * SUM(reached_pick::INT)     / COUNT(*), 1) AS pct_pick,
    ROUND(100.0 * SUM(reached_ship::INT)     / COUNT(*), 1) AS pct_ship,
    ROUND(100.0 * SUM(reached_delivery::INT) / COUNT(*), 1) AS pct_delivery
FROM fact_order_pipeline
```

</details>

- Colonnes retournées : `total_commandes, nb_payment, nb_pick, nb_ship, nb_delivery, pct_payment, pct_pick, pct_ship, pct_delivery`
- Correspondance avec les colonnes attendues :
  - `pct_payment` → `pct_payment`
  - `pct_ship` → `pct_ship`

**Pistes :**
> Aucun bloc ```sql ... ``` détecté et l'extracteur LLM n'a trouvé aucune requête. Encadrez votre requête finale dans la section « Preuve » avec un bloc ```sql ... ``` pour fiabiliser l'auto-validation.
> Extracteur LLM : Le brief ne contient aucune requête SQL imprimée — seules les conclusions chiffrées et les chemins de fichiers sont fournis, pas de SELECT à extraire.
> Requête extraite depuis les fichiers SQL du repo (`sql\analysis\basket_pairs.sql`, `sql\analysis\s02-first-answer.sql`, `sql\bridges\bridge_customer_segment.sql`, `sql\bridges\s08-weighted-allocation.sql`, `sql\checks\s07-reconciliation.sql`) — aucun bloc SQL inline dans le brief. Ajoutez un bloc ```sql ... ``` dans la section « Preuve » de votre brief pour fiabiliser l'auto-validation à l'avenir.

## 2. Rétroaction pédagogique sur le brief

> Brief solide et orienté décision : les types de faits sont correctement identifiés, les validations s'exécutent et la recommandation opérationnelle est claire. Améliorer la traçabilité des décisions (commits, note IA) et fournir des artefacts de validation SQL en annexe pour faciliter la revue.

### Observations par dimension

**Model quality**
- Observation : Le brief liste et justifie les quatre types de faits (transaction, periodic snapshot, accumulating, factless) et précise le grain pour chaque table.
- Piste d'amélioration : Préciser le grain exact et un diagramme de schéma (PK/FK) pour au moins une table critique pour lever toute ambiguïté structurelle.

**Validation quality**
- Observation : L'auteur indique avoir exécuté les scripts (generate/load/check) et rapporte '31 PASS, 0 FAIL, 0 SKIP' et comptages détaillés (1 662 transactions, 301 commandes livrées...).
- Piste d'amélioration : Ajouter les requêtes SQL principales de validation dans le brief (ou en annexe) pour permettre une revue rapide des checks clés.

**Executive justification**
- Observation : La section 'Réponse exécutive' donne des chiffres clairs (ex. 70,2 % livrées, délai moyen 10,3 jours) et une recommandation de suivi des commandes bloquées et d'alertes.
- Piste d'amélioration : Synthétiser la recommandation en un KPI unique (définition, seuil, action) et indiquer l'impact attendu en termes financiers ou opérationnels.

**Process trace**
- Observation : La validation mentionne l'exécution de scripts et un seed nommé, mais il n'y a pas d'historique git ni de note IA détaillée dans le brief.
- Piste d'amélioration : Fournir un journal de commits (≥3 commits significatifs) et une note IA précisant outil, prompts et validation humaine.

**Reproducibility**
- Observation : Le candidat décrit les commandes exactes à exécuter ('.\run.ps1 generate' / 'load' / 'check') et le seed utilisé pour reproduire les tests.
- Piste d'amélioration : Inclure un README pas-à-pas avec exigences système et un exemple de sortie attendue pour exécuter le pipeline sur une machine propre.

## 3. Déclaration d'utilisation de l'IA

> La déclaration documente clairement les modèles utilisés, les étapes où l'IA a aidé et les validations humaines effectuées. En revanche, elle ne signale pas explicitement de limites, d'erreurs ou de comportements incorrects produits par les outils IA.

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

- **Run ID :** `20260622T135856Z-2faa194c`
- **Devoir :** `S09`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `f06e67e`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260622T135856Z-2faa194c/XArsenault/`
- **Prompts (SHA-256) :**
  - `sql_extractor_system` : `90ee9e277de7a27f...`
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
