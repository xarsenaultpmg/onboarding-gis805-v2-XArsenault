# Rétroaction automatisée -- S03 (Dimensions à changement lent : garder la vérité historique chez NexaMart)

_Générée le 2026-06-22T14:59:25+00:00 -- Run `20260622T145220Z-c416c71f`_

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

> Le brief répond clairement à la question du CEO : il justifie l'usage de SCD2 pour les attributs décisionnels et fournit preuves et scripts. Améliorer la traçabilité (commits, note IA) et ajouter tests de cas limites renforcera la robustesse opérationnelle.

### Observations par dimension

**Model quality**
- Observation : La note précise une politique SCD (Type 2 pour segment, city, région; Type 1 pour corrections) et décrit valid_from/valid_to, is_current et la jointure temporelle sur order_date.
- Piste d'amélioration : Ajouter un diagramme logique (schéma des tables avec clés substituts) et expliciter le grain exact de la table fact_sales pour lever toute ambiguïté.

**Validation quality**
- Observation : Le brief liste des contrôles PASS (unicité de customer_key, une version courante, grain de 3 000 lignes) et renvoie au script sql/scd/type1_vs_type2_demo.sql exécuté sur db/nexamart.duckdb.
- Piste d'amélioration : Inclure au moins un test de cas limite (NULLs, chevauchement de périodes, SUM(weights)=1) et fournir le résultat de ces checks ou assertions automatisées.

**Executive justification**
- Observation : La section 'Réponse exécutive' explique en langage d'affaires que Type 1 fausse l'attribution par segment et recommande SCD2 comme base décisionnelle, avec chiffres d'impact (129,78 $ et 5 527,41 $).
- Piste d'amélioration : Ajouter une recommandation chiffrée sur l'effort/coût estimé (ex. heures de pipeline ou impact performance) pour faciliter la priorisation exécutive.

**Process trace**
- Observation : Le brief mentionne des fichiers et scripts (docs/scd-policy.md, sql/...) et le seed utilisé, mais n'inclut pas d'historique git ni de note IA détaillée.
- Piste d'amélioration : Fournir un journal de décisions et un log git avec ≥3 commits signifiants et une note IA précisant outils et validation humaine.

**Reproducibility**
- Observation : Les requêtes sont exécutées sur db/nexamart.duckdb (seed fourni) et les chemins vers les scripts sont listés, facilitant la reproduction.
- Piste d'amélioration : Ajouter un README pas-à-pas 'Clone → seed → run' avec commandes exactes et éviter tout chemin codé en dur pour atteindre l'exécution en <5 minutes.

## 3. Déclaration d'utilisation de l'IA

> La déclaration documente bien les outils (avec versions), les étapes d'utilisation et les méthodes de validation humaine détaillées pour chaque séance. Elle ne précise toutefois pas de limites, d'erreurs ou de comportements inattendus observés dans les sorties IA.

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

- **Run ID :** `20260622T145220Z-c416c71f`
- **Devoir :** `S03`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `944f5df`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260622T145220Z-c416c71f/XArsenault/`
- **Prompts (SHA-256) :**
  - `sql_extractor_system` : `90ee9e277de7a27f...`
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
