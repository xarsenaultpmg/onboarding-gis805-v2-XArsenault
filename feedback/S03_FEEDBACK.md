# Rétroaction automatisée -- S03 (Dimensions à changement lent : garder la vérité historique chez NexaMart)

_Générée le 2026-05-29T00:19:48+00:00 -- Run `20260529T001921Z-d85680b2`_

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

> Très bon brief : la décision SCD2 est bien justifiée avec preuves chiffrées et scripts reproductibles indiqués. Améliorer la traçabilité (commits + note IA) et ajouter checks pour cas limites afin d'augmenter la robustesse opérationnelle.

### Observations par dimension

**Model quality**
- Observation : La note décrit clairement une politique SCD Type 2 pour segment/city/région, clé substitut customer_key, et la jointure temporelle (order_date BETWEEN valid_from AND valid_to).
- Piste d'amélioration : Préciser le grain exact des faits dans la section modèle (p. ex. fact_sales au niveau de la ligne de commande) et inclure un diagramme star simple montrant clés et cardinalités.

**Validation quality**
- Observation : Le brief fournit des scripts de démonstration (sql/scd/type1_vs_type2_demo.sql), des requêtes d'agrégat avant/après et un tableau de contrôles indiquant plusieurs PASS.
- Piste d'amélioration : Ajouter des checks explicites pour les cas limites (NULLs, chevauchements de périodes, sommes de poids, et tests de non-régression) et montrer une sortie de résultat clé reproduite.

**Executive justification**
- Observation : La section 'Réponse exécutive' répond clairement à la question CEO, explique l'impact (ex. écart Gold = 129,78 $) et se termine par des recommandations opérationnelles concrètes.
- Piste d'amélioration : Condenser en une phrase d'action directe pour le board (p. ex. 'Adopter SCD2 pour segments/regions immédiatement; suspendre rapports critiques pendant la migration').

**Process trace**
- Observation : Le brief cite des fichiers (docs/scd-policy.md, sql/...), l'exécution sur db/nexamart.duckdb et un seed, mais n'inclut pas d'historique de commits ni de note IA détaillée.
- Piste d'amélioration : Ajouter l'historique git (≥3 commits incrémentaux avec messages) et une note IA précisant l'outil utilisé et la validation humaine réalisée.

**Reproducibility**
- Observation : Les chemins vers les scripts et la base (db/nexamart.duckdb) sont fournis ainsi que le seed utilisé, suggérant que les requêtes peuvent être rejouées.
- Piste d'amélioration : Fournir un README pas-à-pas 'Clone → DuckDB → run demo' sans chemins codés en dur et inclure un script d'installation pour exécuter les démonstrations en <5 minutes.

## 3. Déclaration d'utilisation de l'IA

> La déclaration est complète et documente les outils (avec version), les étapes d'utilisation, les validations humaines et des limites pertinentes. Bon niveau de détail reproduisant prompts, validations et décisions finales prises par l'étudiant.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain
- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Aucune correction technique nécessaire. Voir la section 2 pour des pistes d'approfondissement.

---

## 5. Traçabilité

- **Run ID :** `20260529T001921Z-d85680b2`
- **Devoir :** `S03`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `686d997`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260529T001921Z-d85680b2/XArsenault/`
- **Prompts (SHA-256) :**
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
