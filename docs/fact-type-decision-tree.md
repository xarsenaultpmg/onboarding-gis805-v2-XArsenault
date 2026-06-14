# Arbre de décision — Types de tables de faits NexaMart

> S09 — Livrable `docs/fact-type-decision-tree.md`
>
> **Instructions :** Complétez les colonnes **Type** et **Justification** pour chaque processus NexaMart. Puis appliquez l'arbre de décision général à un processus de votre choix hors NexaMart.

---

## Partie 1 — Carte des processus NexaMart

| Processus NexaMart | Table de faits | Type de fait | Question CEO à laquelle il répond | Justification du choix |
|---|---|---|---|---|
| Ventes | `fact_sales` | *(à compléter)* | *(à compléter)* | *(à compléter)* |
| Ordres détaillés | `fact_orders_transaction` | *(à compléter)* | *(à compléter)* | *(à compléter)* |
| Retours | `fact_returns` | *(à compléter)* | *(à compléter)* | *(à compléter)* |
| Stock quotidien | `fact_daily_inventory` | *(à compléter)* | *(à compléter)* | *(à compléter)* |
| Pipeline de commandes | `fact_order_pipeline` | *(à compléter)* | *(à compléter)* | *(à compléter)* |
| Exposition promotionnelle | `fact_promo_exposure` | *(à compléter)* | *(à compléter)* | *(à compléter)* |

### Colonnes d'aide

**Types valides :** `Transaction` / `Periodic Snapshot` / `Accumulating Snapshot` / `Factless`

**Indices :**
- Une table dont les lignes sont mises à jour au fil du temps → ?
- Une table sans aucune colonne de montant ou de quantité → ?
- Une table où SUM sur le temps produit un résultat absurde → ?
- Une table où chaque ligne représente un événement irréversible → ?

---

## Partie 2 — Arbre de décision général

Utilisez cet arbre pour diagnostiquer le type correct d'un processus inconnu.

```
Est-ce que le processus enregistre un ÉVÉNEMENT PONCTUEL (une vente,
un retour, un paiement) ?
    │
    ├─ OUI ──→ Transaction Fact Table
    │           Grain : un événement individuel
    │           Mesures : additives (SUM partout)
    │           Règle : INSERT-ONLY
    │
    └─ NON ──→ Est-ce que le processus capture un ÉTAT À INTERVALLES
               RÉGULIERS (stock quotidien, solde mensuel) ?
                    │
                    ├─ OUI ──→ Periodic Snapshot Fact Table
                    │           Grain : entité × période
                    │           Mesures : semi-additives (ne PAS SUM sur le temps)
                    │           Règle : INSERT-ONLY (nouvelle photo chaque période)
                    │
                    └─ NON ──→ Est-ce que le processus suit un CYCLE DE VIE
                               avec des ÉTAPES SÉQUENTIELLES (commande → paiement
                               → livraison) ?
                                    │
                                    ├─ OUI ──→ Accumulating Snapshot Fact Table
                                    │           Grain : une entité par ligne (commande)
                                    │           Colonnes : une date par jalon
                                    │           Règle : UPDATE quand un jalon est atteint
                                    │
                                    └─ NON ──→ Factless Fact Table
                                                Grain : présence d'une relation
                                                Mesures : aucune (COUNT(*) est la seule)
                                                Règle : INSERT-ONLY
```

---

## Partie 3 — Application à un processus hors NexaMart

*(Choisissez un processus de votre propre expérience professionnelle ou académique.)*

**Processus choisi :** *(à compléter)*

**Type de fait approprié :** *(à compléter)*

**Justification :**
- Question business à laquelle il répond : *(à compléter)*
- Grain de la table : *(à compléter)*
- Mesures ou absence de mesures : *(à compléter)*
- Règle d'update (INSERT-ONLY ou UPDATE) : *(à compléter)*

---

*Document à commiter dans `docs/fact-type-decision-tree.md` avant le 15 juin 18h00.*
