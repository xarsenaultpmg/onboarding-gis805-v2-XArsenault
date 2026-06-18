# Rétroaction automatisée -- S03 (Dimensions à changement lent : garder la vérité historique chez NexaMart)

_Générée le 2026-05-29T00:56:53+00:00 -- Run `20260529T004953Z-f2a5f6ff`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

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

> Très bon brief : la politique SCD est claire, la preuve chiffrée est fournie et la recommandation est actionnable. Améliorez la traçabilité des décisions (commits, note IA) et ajoutez contrôles de cas limites pour renforcer la reproductibilité.

### Observations par dimension

**Model quality**
- Observation : La note indique clairement SCD Type 2 pour segment, city, région et Type 1 pour corrections, avec clé substitut customer_key et jointure par valid_from/valid_to.
- Piste d'amélioration : Inclure un diagramme de schéma (DDL simplifié) montrant les colonnes de dim_customer et les clés pour faciliter la revue technique.

**Validation quality**
- Observation : Le brief fournit des scripts référencés (sql/scd/type1_vs_type2_demo.sql), des résultats chiffrés (écart 129,78 $) et une table de contrôles indiquant PASS pour plusieurs vérifications.
- Piste d'amélioration : Ajouter un contrôle explicite des cas limites (NULLs, périodes chevauchantes, et SUM(weights)=1) et un extrait de sortie SQL montrant ces cas traités.

**Executive justification**
- Observation : La section 'Réponse exécutive' répond à la question CEO en langage d'affaires, montre l'impact chiffré et propose une recommandation claire (geler la politique SCD et industrialiser les changements).
- Piste d'amélioration : Synthétiser en une phrase-action priorisée (ex. : 'Appliquer SCD2 pour clients et magasins d'ici la prochaine release') et préciser l'impact attendu sur KPI clés.

**Process trace**
- Observation : Le brief réfère des documents et scripts (docs/scd-policy.md, sql/...), mais n'indique pas d'historique git ni de note IA détaillée ni de logs de décisions incrémentaux.
- Piste d'amélioration : Ajouter un journal de décisions (CHANGELOG) avec ≥3 commits et un encart 'usage IA' précisant outils, prompts et validations humaines.

**Reproducibility**
- Observation : Indication du fichier de base de données (db/nexamart.duckdb), seed utilisé et chemins vers les scripts SQL pour reproduire la démonstration.
- Piste d'amélioration : Fournir un README pas-à-pas 'clone → seed → run' et supprimer chemins codés en dur pour atteindre l'exécution en <5 minutes sur un clone propre.

## 3. Déclaration d'utilisation de l'IA

> La déclaration est complète et fournit des preuves concrètes (modèles nommés avec version, étapes d'utilisation, validations exécutées et limites observées). Continuez à conserver ce niveau de détail pour chaque future séance, en ajoutant si possible une brève note sur les paramètres ou prompts sensibles modifiés entre itérations.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain
- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Aucune correction technique nécessaire. Voir la section 2 pour des pistes d'approfondissement.

---

## 5. Traçabilité

- **Run ID :** `20260529T004953Z-f2a5f6ff`
- **Devoir :** `S03`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `a634588`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260529T004953Z-f2a5f6ff/XArsenault/`
- **Prompts (SHA-256) :**
  - `sql_extractor_system` : `90ee9e277de7a27f...`
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
