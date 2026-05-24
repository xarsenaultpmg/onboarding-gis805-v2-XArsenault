# Trace d'usage IA — GIS805

> Chaque interaction significative avec un outil IA doit être documentée ici.
> Ce fichier est **obligatoire** et évalué à chaque remise.

## Format par entrée

```
### YYYY-MM-DD — Séance SXX
- **Modèle :** (ChatGPT-4o, Claude, Copilot, etc.)
- **Prompt :** (copier-coller exact)
- **Résultat :** (résumé de ce que l'IA a produit)
- **Validation :** (comment vous avez vérifié/modifié le résultat)
- **Justification :** (pourquoi cette interaction était nécessaire)
```

---

### 2026-05-10 — Séance S01
- **Modèle :** Claude Sonnet 4.6
- **Prompt :** « Aide-moi à remplir le document S01_executive_brief.md pour répondre à la question du CEO : quelles catégories déclinent dans quelles régions et pourquoi ? »
- **Résultat :** Claude a guidé la rédaction de chaque section du brief : réponse exécutive, décisions de modélisation, preuve SQL, validation et risques. Il a aussi construit la requête SQL avec window function LAG pour identifier les déclins trimestriels.
- **Validation :**
  - J'ai roulé toutes les requêtes dans mon Codespace sur ma base `db/nexamart.duckdb` pour vérifier les résultats.
  - J'ai validé la réconciliation des totaux (896 840.55 $ brut = 896 840.55 $ avec jointures).
  - J'ai vérifié manuellement Québec/Home & Garden : seulement 5 transactions en Q2 — signal retiré des priorités CEO.
  - J'ai confirmé que mes données ne couvrent que 2025, ce qui a justifié le choix d'une comparaison QoQ plutôt qu'YoY.
- **Justification :** Claude a servi de co-équipier analytique pour structurer la démarche, construire les requêtes SQL et valider la cohérence des chiffres avant présentation au CEO. Toutes les décisions finales et la validation des résultats ont été faites par moi.

### 2026-05-14 — Séance S02
- **Modèle :** Claude Sonnet 4.6
- **Prompt :** « Implement the plan Livrables S02 (par artefact) : SQL d’analyse, diagramme Mermaid, docs/schema-v1.md, board brief, S02_executive_brief.md, ai-usage ; commentaires SQL en français ; valider sur db/nexamart.duckdb. » — puis, dans des échanges suivants : modèle Draw.io, lisibilité (texte noir), cohérence des libellés avec le Mermaid, clarification SK/SCD vs lab S02.
- **Résultat :** Fichiers créés selon le plan (`sql/analysis/s02-first-answer.sql`, `diagrams/schema-v1.mmd`, `docs/schema-v1.md`, `docs/board-briefs/s02-star-schema.md`, `answers/S02_executive_brief.md`) ; ajout de `diagrams/schema-v1.drawio` ; chiffres de preuve et validation issus d’une exécution locale sur `db/nexamart.duckdb`. Ensuite : alignement des étiquettes de liaison Draw.io sur les libellés du `.mmd`, bloc `FACT_SALES` harmonisé avec les colonnes du Mermaid, note sur les clés naturelles v1 ; section **« Clés substitutives (SK) et SCD »** dans `docs/schema-v1.md` (hors exigences explicites du [GIS805-02_lab.md](docs/lab-guides/GIS805-02_lab.md)).
- **Validation :**
  - Requête S02 exécutée sans erreur ; `SUM(line_total)` identique avec et sans jointures ; 0 orphelin sur les trois dimensions utilisées ; 3 000 lignes et 3 000 `sale_line_id` distincts.
  - Relu les textes pour alignement avec [docs/schema-v1.md](docs/schema-v1.md) et la rubrique du lab (grain, catégorie / région / trimestre).
  - Vérifié la cohérence visuelle entre [diagrams/schema-v1.mmd](diagrams/schema-v1.mmd) et [diagrams/schema-v1.drawio](diagrams/schema-v1.drawio) (mêmes relations et libellés de rôles sur les flèches ; colonnes du fait alignées).
  - Relu la section SK/SCD : formulation conforme au guide de lab S02 (pas d’obligation de SK ni de SCD à cette séance).
- **Justification :** Accélérer la mise en forme des livrables et la validation SQL tout en conservant les décisions de conception et les montants vérifiés manuellement sur la base locale ; itérer sur les diagrammes et la doc pour lever l’ambiguïté SK/SCD et garder une trace d’usage complète.

### 2026-05-15 — Séance S02 (harmonisation lab)
- **Modèle :** Cursor / agent
- **Prompt :** Harmoniser tous les livrables S02 sur le lab (pas de `dim_order`, cinq dimensions dont `dim_channel`, `order_number` dégénérée).
- **Résultat :** Mise à jour de `fact_sales.sql`, `schema-v1.mmd`, `schema-v1.md`, `schema-v1.drawio`, briefs, `sql/dims/README.md`.
- **Validation :** `.\run.ps1 load` puis `.\run.ps1 check` ; `.\run.ps1 sql sql\analysis\s02-first-answer.sql`.
- **Justification :** Aligner le dépôt sur GIS805-02 et `s02-sample-brief.md` après écart avec une variante « diapo order_key ».

### 2026-05-21 — Séance S03
- **Modèle :** Claude Sonnet 4.6
- **Prompt :** « Aide-moi à livrer la séance S03 : quels changements dans nos dimensions doivent garder la vérité historique, et lesquels peuvent être écrasés ? Je dois montrer au VP pourquoi l’ancien rapport était trompeur, rédiger la politique SCD, et prouver la différence entre Type 1 et Type 2 avec du SQL sur mes données NexaMart. »
- **Résultat :** Claude a guidé la rédaction du brief exécutif (réponse au CEO, décisions de modélisation, risques), de la politique SCD par attribut dans `docs/scd-policy.md`, et du brief conseil. Il a aidé à construire la démo `sql/scd/type1_vs_type2_demo.sql` (rapport trompeur vs correct par segment) et à historiser `dim_customer` / `dim_store` avec `valid_from`, `valid_to` et `is_current`, ainsi que les jointures temporelles dans `fact_sales`.
- **Validation :**
  - J’ai roulé `.\run.ps1 generate`, `.\run.ps1 load` et les requêtes de démo sur `db/nexamart.duckdb` pour vérifier les chiffres du brief.
  - J’ai confirmé le check `scd2_one_current` (PASS) et que `dim_customer` passe de 285 à 443 lignes après historisation — cohérent avec les événements de `raw_customer_changes`.
  - J’ai vérifié l’exemple **CUS-00152** : 5 527,41 $ identiques, mais segment **Inactive** (Type 2, juste) vs **New** (Type 1, faux) — retenu comme illustration principale dans le brief.
  - J’ai validé l’écart agrégé sur le segment **Gold** (129,78 $) entre les deux rapports, pour montrer que l’erreur n’est pas seulement théorique.
  - J’ai relu `docs/scd-policy.md` et les sections exécutives pour m’assurer que les justifications restent en langage d’affaires (segment, région, moment de la vente), pas en jargon technique.
- **Justification :** Claude a servi de co-équipier pour structurer la politique SCD, formuler l’argument VP (« pourquoi l’historique était faux ») et accélérer le SQL de preuve. Le choix Type 1 vs Type 2 par attribut, l’exemple client retenu et la validation des montants ont été faits par moi.

<!-- Ajoutez vos entrées ci-dessous -->
