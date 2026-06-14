# Arbre de décision — Types de tables de faits NexaMart

> S09 — Livrable `docs/fact-type-decision-tree.md`
>
> **Instructions :** Complétez les colonnes **Type** et **Justification** pour chaque processus NexaMart. Puis appliquez l'arbre de décision général à un processus de votre choix hors NexaMart.

---

## Partie 1 — Carte des processus NexaMart

| Processus NexaMart | Table de faits | Type de fait | Question CEO à laquelle il répond | Justification du choix |
|---|---|---|---|---|
| Ventes | `fact_sales` | Transaction | Quel revenu et quelle marge NexaMart génère-t-il par produit, magasin, client ou canal ? | Une ligne représente une ligne de commande déjà survenue. Les montants et quantités sont additifs sur toutes les dimensions et la table est insert-only. |
| Ordres détaillés | `fact_orders_transaction` | Transaction | Quel revenu brut provient des ventes, retours et échanges par catégorie ou magasin ? | Une ligne représente une transaction atomique identifiée par `transaction_id`. Les événements passés ne sont pas mis à jour ; on ajoute de nouvelles transactions. |
| Retours | `fact_returns` | Transaction | Quels produits, régions ou périodes concentrent les remboursements ? | Une ligne représente un retour observé. Les remboursements et quantités retournées sont des mesures additives au grain de l'événement. |
| Stock quotidien | `fact_daily_inventory` | Periodic Snapshot | Quel niveau de stock moyen et quels jours d'approvisionnement observe-t-on par magasin ? | Une ligne capture l'état produit x magasin x jour. Le stock est semi-additif : on peut sommer par produit ou magasin, mais pas sur le temps. |
| Pipeline de commandes | `fact_order_pipeline` | Accumulating Snapshot | Quel pourcentage des commandes atteint chaque jalon et combien de jours prend la livraison ? | Une ligne suit une commande dans son cycle de vie. Les dates de jalons sont remplies au fil du processus, donc c'est le seul fait qui accepte l'UPDATE. |
| Exposition promotionnelle | `fact_promo_exposure` | Factless | Quelle part des clients a été exposée, et quels clients actifs n'ont pas été atteints ? | La table ne contient aucune mesure numérique. La présence d'une ligne indique l'exposition ; les analyses reposent sur `COUNT(*)` et les anti-jointures. |

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

**Processus choisi :** prise en charge d'un patient en pharmacie de spécialité chez PMG

**Type de fait approprié :** Accumulating Snapshot

**Justification :**
- Question business à laquelle il répond : combien de temps prend le parcours entre la réception d'une prescription spécialisée et la première dispensation au patient ?
- Grain de la table : une ligne = un dossier patient x médicament spécialisé.
- Mesures ou absence de mesures : délais entre jalons, statut courant du dossier, jours entre prescription, validation assurance, autorisation préalable, coordination et dispensation.
- Règle d'update (INSERT-ONLY ou UPDATE) : UPDATE, car le même dossier est enrichi à mesure que les jalons sont atteints.

---

*Document à commiter dans `docs/fact-type-decision-tree.md` avant le 15 juin 18h00.*
