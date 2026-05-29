# Rétroaction automatisée -- S03 (Dimensions à changement lent : garder la vérité historique chez NexaMart)

_Générée le 2026-05-29T00:25:32+00:00 -- Run `20260529T002510Z-9cdeddd0`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

> ⚠️ **Avertissement instructeur (à retirer avant publication) :** cette analyse a été générée avec `--skip-pull`. Le contenu correspond au commit local et **n'est peut-être pas la dernière version poussée par l'étudiant·e**.

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief s'exécute correctement et produit la forme attendue. Bon travail sur l'auto-validation.

<details><summary>Requête analysée — cliquez pour déplier</summary>

```sql
SELECT s.région, ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_store s USING (store_key)
GROUP BY s.région
ORDER BY revenue DESC
```

</details>

- Colonnes retournées : `région, revenue`
- Correspondance avec les colonnes attendues :
  - `region` → `région`
  - `revenue` → `revenue`
- Présence de NULLs dans des colonnes de groupement : `région` =0. Pensez à documenter le traitement de ces cas.

**Pistes :**
> Aucune requête SQL trouvée dans le brief ni dans les fichiers du repo. Une requête canonique a été synthétisée à partir du schéma de votre base pour vérifier que vos tables et jointures sont correctement en place. Ajoutez votre requête finale dans la section « Preuve » avec un bloc ```sql ... ``` pour éliminer cette étape.

## 2. Rétroaction pédagogique sur le brief

> Le brief répond clairement à la question CEO : politique SCD bien justifiée, preuves chiffrées et requêtes de validation exécutées. Améliorer la traçabilité (commits, note IA) et fournir un README de reproduction pour faciliter la production et la revue.

### Observations par dimension

**Model quality**
- Observation : La note explique clairement l'adoption de SCD Type 2 pour segment, city et région, la création de clés de version (customer_key) et l'usage de valid_from/valid_to pour joindre les faits à la date de commande.
- Piste d'amélioration : Préciser le grain exact des faits (niveau ligne/commande/transaction) et montrer un diagramme simple du schéma dim_customer + fact_sales pour faciliter la revue technique.

**Validation quality**
- Observation : La section Validation liste des contrôles PASS (une version courante, clé unique, grain fact_sales) et référence le script sql/scd/type1_vs_type2_demo.sql exécuté sur db/nexamart.duckdb.
- Piste d'amélioration : Ajouter une vérification explicite des NULLs et des bornes par date (tests pour orders aux dates limites) et inclure les résultats chiffrés des scripts d'assertion.

**Executive justification**
- Observation : La Réponse exécutive indique que le Type 1 fausse les rapports et fournit des chiffres d'impact (129,78 $ et 5 527,41 $ pour CUS-00152) avec une recommandation claire d'appliquer SCD2.
- Piste d'amélioration : Condensez la recommandation en une action opérationnelle priorisée (ex. échéancier et propriétaire pour industrialisation S03→S04).

**Process trace**
- Observation : Le brief référence des fichiers (docs/scd-policy.md, sql/...) et la base db/nexamart.duckdb mais n'indique pas d'historique de commits ni de note IA détaillée.
- Piste d'amélioration : Fournir l'historique git avec ≥3 commits significatifs et une note IA décrivant l'outil utilisé et comment les sorties ont été validées manuellement.

**Reproducibility**
- Observation : Les chemins vers scripts et la base (db/nexamart.duckdb) et le seed mentionné facilitent la reproduction, mais aucun README d'exécution n'est cité.
- Piste d'amélioration : Ajouter un README 'Reproduce.md' avec étapes exactes (commande DuckDB, seed, chemins relatifs) pour exécuter les scripts en moins de 5 minutes.

## 3. Déclaration d'utilisation de l'IA

> La déclaration est complète et fournit des preuves concrètes pour chaque point requis (outil nommé et version, étape d'utilisation, validation humaine et limite identifiée). Pensez à conserver ce niveau de détail pour chaque séance future et, si possible, ajoutez la date et l'heure pour faciliter la traçabilité.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain
- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Aucune correction technique nécessaire. Voir la section 2 pour des pistes d'approfondissement.

---

## 5. Traçabilité

- **Run ID :** `20260529T002510Z-9cdeddd0`
- **Devoir :** `S03`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `a634588`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260529T002510Z-9cdeddd0/XArsenault/`
- **Prompts (SHA-256) :**
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
