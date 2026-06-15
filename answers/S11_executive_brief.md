# Board Brief — S11 : Documentation et handoff

> **Question du CEO :** Si vous quittez NexaMart demain, est-ce qu'une nouvelle personne pourrait prendre la suite de l'entrepôt ?

---

## Réponse exécutive

<!-- TODO : En 3–4 phrases, répondez directement au CEO.
     Votre handoff pack couvre-t-il les 5 questions du passage de relais ?
     Exemple : "Oui. Les quatre documents produits ce soir permettent à une nouvelle personne
     de comprendre la structure du modèle, les décisions de conception, et d'exécuter
     les vérifications sans assistance. La seule lacune connue est [...]." -->

## Livrables de handoff

<!-- TODO : Listez vos 4 documents avec une phrase de description spécifique à VOTRE modèle.
     Remplacez les crochets par votre contenu réel.

- `docs/model-card.md` — [décrivez votre modèle : combien de facts, grain principal, SCD utilisés]
- `docs/bus-matrix.md` — [décrivez quelles facts et dims sont couvertes, cases vides notables]
- `docs/data-dictionary.md` — auto-généré par CI depuis vos tables DuckDB (ne pas modifier)
- `docs/decision-log.md` — [combien de décisions documentées, exemples des 2 plus importantes]
-->

## Test du passage de relais

<!-- TODO : Répondez à ces 5 questions en vous basant uniquement sur vos documents.
     Si vous ne pouvez pas répondre à l'une, votre documentation est incomplète.

1. Quelle est la table de faits principale, et quel est son grain ?
   → [votre réponse]

2. Quelles dimensions sont historisées (SCD 2) ? Lesquelles ne le sont pas ?
   → [votre réponse]

3. Comment reproduire l'entrepôt depuis un clone vide ?
   → [votre réponse — commandes make check, make load, etc.]

4. Où se trouve la preuve qu'un check de contrainte passe ?
   → [votre réponse — fichier, commande, ou output CI]

5. Qui est le propriétaire fonctionnel de chaque fait ?
   → [votre réponse]
-->

## Preuve — KPI principal

<!-- TODO : Une requête SQL qui retourne AU MOINS 1 KPI clé de votre modèle.
     Elle doit s'exécuter sur votre db/nexamart.duckdb sans aucune modification.
     L'alias de colonne doit refléter la métrique : net_revenue, pct_delivery, taux_retour...
     IMPORTANT : exécutez cette requête et collez le résultat dans le tableau ci-dessous. -->

```sql
-- TODO : remplacez par votre requête réelle
SELECT ...
FROM fact_...
```

| Métrique | Valeur observée | Interprétation |
|---|---|---|
| <!-- TODO : alias SQL --> | <!-- valeur --> | <!-- ce que ça signifie pour NexaMart --> |

## Réponse au CEO

<!-- TODO : 2–3 phrases.
     Répondez directement à la question d'ouverture.
     Indiquez ce qui est couvert, et si des lacunes subsistent, lesquelles et pourquoi.
     Exemple : "L'entrepôt est transmissible. Les quatre documents couvrent la structure,
     les décisions, et les KPIs. La prochaine priorité serait d'automatiser le rechargement
     complet via un pipeline dbt." -->
