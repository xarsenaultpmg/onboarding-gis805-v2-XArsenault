# Rétroaction automatisée -- S02 (Schéma en étoile, grain et dimensions conformes : le premier modèle NexaMart)

_Générée le 2026-05-29T00:19:16+00:00 -- Run `20260529T001852Z-0965533f`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

> ⚠️ **Avertissement instructeur (à retirer avant publication) :** cette analyse a été générée avec `--skip-pull`. Le contenu correspond au commit local et **n'est peut-être pas la dernière version poussée par l'étudiant·e**.

---

## 1. Vérification automatique de la requête SQL

La requête extraite de votre brief n'a pas pu être validée automatiquement. Quelques pistes constructives ci-dessous pour vous aider à la rendre exécutable et alignee avec la question posée.

_Observation technique : colonnes manquantes (oracle): category, quarter_

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
  - `category` → `(à ajouter ou renommer)`
  - `region` → `région`
  - `quarter` → `(à ajouter ou renommer)`
  - `revenue` → `revenue`

**Pistes :**
> Aucune requête SQL trouvée dans le brief ni dans les fichiers du repo. Une requête canonique a été synthétisée à partir du schéma de votre base pour vérifier que vos tables et jointures sont correctement en place. Ajoutez votre requête finale dans la section « Preuve » avec un bloc ```sql ... ``` pour éliminer cette étape.
> Synonymes acceptés par colonne:
  category: ['category', 'categorie', 'p.category', 'product_category']
  region: ['region', 's.region', 'store_region']
  quarter: ['quarter', 'trimestre', 'd.quarter', 'q']
  revenue: ['revenue', 'total_revenue', 'line_total', 'net_revenue', 'revenu', 'ca', 'sales', 'total_sales']

## 2. Rétroaction pédagogique sur le brief

> Excellente réponse : grain, étoile et preuves SQL sont clairs et convaincants, et le brief fournit des validations concrètes. Améliorer la traçabilité git et ajouter des tests automatiques/README pour faciliter la reproductibilité en production.

### Observations par dimension

**Model quality**
- Observation : Le brief précise le grain «1 ligne = 1 ligne de commande (order_number, sale_line_id)» et décrit une étoile à cinq dimensions avec mesures `quantity` et `revenue`.
- Piste d'amélioration : Ajouter un court diagramme d'exemple de requête OLAP (ex. vue matérialisée) et préciser les types/contraintes (not null, keys) pour production.

**Validation quality**
- Observation : Le document fournit un fichier SQL canonique, un extrait de résultats (top 10) et un tableau de contrôles (SUM(revenue) ≈ SUM(line_total), orphelins = 0, grain unique).
- Piste d'amélioration : Inclure des checks sur valeurs NULL et un test automatisé qui échoue si SUM(revenue) diverge au-delà d'un seuil.

**Executive justification**
- Observation : La section «Réponse au CEO» explique que la jointure fact→dimensions permet d'obtenir catégorie × région × trimestre et propose une recommandation opérationnelle (industrialiser en modèle dbt, croiser avec fact_returns).
- Piste d'amélioration : Ajouter un KPI chiffré (ex. liste des 3 combinaisons à surveiller avec seuils) pour rendre la décision immédiatement exécutable.

**Process trace**
- Observation : Le brief référence clairement des fichiers/diagrammes (diagrams/schema-v1.mmd, sql/analysis/s02-first-answer.sql) et inclut une instruction IA pour générer le diagramme.
- Piste d'amélioration : Fournir l'historique git avec au moins 3 commits et un court log explicite des décisions de modélisation.

**Reproducibility**
- Observation : Le brief indique des chemins relatifs vers les scripts et le SQL canonique (`sql/analysis/s02-first-answer.sql`) facilitant la reproduction.
- Piste d'amélioration : Ajouter un README pas-à-pas et un script 'run_checks.sh' qui exécute les validations sur un clone propre.

## 3. Déclaration d'utilisation de l'IA

> La déclaration décrit clairement quand et comment les modèles ont été utilisés et comment les résultats ont été vérifiés localement. Toutefois, certaines mentions d'outil restent génériques (p.ex. «Cursor / agent») sans version/modèle précis, ce qui empêche une traçabilité complète.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain
- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Reprendre la requête de la section « Preuve » pour qu'elle s'exécute sur db/nexamart.duckdb et qu'elle produise la forme attendue (voir pistes en section 1).

---

## 5. Traçabilité

- **Run ID :** `20260529T001852Z-0965533f`
- **Devoir :** `S02`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `686d997`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260529T001852Z-0965533f/XArsenault/`
- **Prompts (SHA-256) :**
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
