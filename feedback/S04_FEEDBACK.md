# Rétroaction automatisée -- S04 (Panier d'achat et drapeaux : les patterns que l'étoile simple ne couvre pas)

_Générée le 2026-05-29T00:26:04+00:00 -- Run `20260529T002537Z-9384f7ff`_

Ce document est produit par un pipeline reproductible (validation automatique du livrable + analyse LLM du brief et de la déclaration IA). Une revue humaine précède toujours sa publication. **À ce stade expérimental, aucune note ni étiquette de niveau n'est diffusée : l'objectif est purement formatif.**

> ⚠️ **Avertissement instructeur (à retirer avant publication) :** cette analyse a été générée avec `--skip-pull`. Le contenu correspond au commit local et **n'est peut-être pas la dernière version poussée par l'étudiant·e**.

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

> Très bon brief : modèle dimensionnel bien justifié, validations SQL présentes et recommandations opérationnelles claires. Compléter le process trace (commits, note IA) et ajouter quelques vérifications automatisées pour renforcer la reproductibilité.

### Observations par dimension

**Model quality**
- Observation : Le brief décrit une junk dimension dim_order_profile avec 8 flags consolidés et justifie le choix (99 profils observés sur 256 théoriques) et l'usage de profile_key dans fact_sales.
- Piste d'amélioration : Ajouter un diagramme simple (star schema) montrant les clés et la granularité pour rendre explicite l'impact sur les requêtes analytiques.

**Validation quality**
- Observation : Des requêtes SQL sont fournies (agrégats par profile_name, top paires produits) et des checks listés (grain unique PASS, TABLE_EXISTS PASS, couverture profile_key 81%).
- Piste d'amélioration : Inclure une vérification explicite des cas limites (NULLs dans profile_key traités, et fréquence des combinaisons rares) ou des assertions automatisées dans make check.

**Executive justification**
- Observation : La section 'Réponse exécutive' propose des décisions claires au VP Opérations (prioriser fragile et employé, tester bundle Home & Garden + Books & Media).
- Piste d'amélioration : Ajouter un court chiffrage attendu (ex. : impact % sur temps de picking ou CA projeté pour le bundle) pour faciliter la prise de décision budgétaire.

**Process trace**
- Observation : Le brief documente la pipeline (make generate/load/check) et des docs référencés mais n'indique pas d'historique git ni de note IA détaillée.
- Piste d'amélioration : Fournir le log git avec ≥3 commits incrémentaux et une note d'utilisation IA indiquant outil, prompt et validation humaine.

**Reproducibility**
- Observation : Instructions de reproduction fournies (make generate; make load; make check; make sql FILE=...) et références vers docs/schema-v2.md et autres.
- Piste d'amélioration : Préciser les prérequis exacts et tester sur un clone propre pour éliminer chemins codés en dur ; ajouter un script d'installation des dépendances.

## 3. Déclaration d'utilisation de l'IA

> La déclaration couvre toutes les thématiques demandées : outils (avec modèle/version le plus souvent), étapes d'utilisation et méthodes de validation humaine sont documentées, et quelques limites de données sont mentionnées. Toutefois certaines mentions d'outils restent génériques (p.ex. « Cursor / agent » sans version précise), ce qui empêche d'atteindre la note maximale.

**Sujets bien couverts dans votre déclaration :**

- outils utilisés (nom + version/modèle)
- à quelle étape l'IA a été utilisée
- comment la sortie a été validée par l'humain
- limites ou erreurs observées

## 4. Pistes d'action pour la prochaine itération

- Aucune correction technique nécessaire. Voir la section 2 pour des pistes d'approfondissement.

---

## 5. Traçabilité

- **Run ID :** `20260529T002537Z-9384f7ff`
- **Devoir :** `S04`
- **Étudiant·e :** `XArsenault`
- **Commit analysé :** `a634588`
- **Audit (côté instructeur) :** `tools/instructor/feedback_pipeline/audit/20260529T002537Z-9384f7ff/XArsenault/`
- **Prompts (SHA-256) :**
  - `rubric_grader_system` : `505f32d1d8319d66...`
  - `ai_usage_grader_system` : `81cb7fdf89bda55a...`
- **Fournisseur (rubrique) :** `openai`
- **Fournisseur (IA-usage) :** `openai` (gpt-5-mini-2025-08-07)

_Ce feedback a été produit par un pipeline automatisé et **revu par l'équipe pédagogique avant publication**. Aucun chiffre ni étiquette de niveau n'est diffusé à ce stade expérimental : l'objectif est uniquement formatif. Ouvrez une issue dans ce dépôt pour toute question._
