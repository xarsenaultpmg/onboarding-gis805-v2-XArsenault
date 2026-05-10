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

<!-- Ajoutez vos entrées ci-dessous -->
