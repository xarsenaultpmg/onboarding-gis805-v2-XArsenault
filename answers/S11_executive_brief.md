# Board Brief — S11 : Documentation et handoff

> **Question du CEO :** Si vous quittez NexaMart demain, est-ce qu'une nouvelle personne pourrait prendre la suite de l'entrepôt ?

---

## Réponse exécutive

Oui. Le handoff pack couvre la structure du modèle (8 tables de faits, grains,
SCD et ponts), les décisions de conception en langage d'affaires, le
dictionnaire de données, et cinq KPIs testés sur DuckDB. Une personne qui
clone le dépôt peut reconstruire l'entrepôt avec `.\run.ps1 generate`, `load`
et `check`, puis reproduire les métriques sans assistance. La seule lacune
connue est l'absence de pipeline ELT automatisé — le rechargement reste manuel
via les scripts du cours.

## Livrables de handoff

- `docs/model-card.md` — décrit 8 tables de faits (grain, type Kimball,
  additivité mesure par mesure, politique NULL, pont segment et risques) pour
  l'entrepôt NexaMart v0.11.
- `docs/bus-matrix.md` — matrice S11 des 8 processus × 7 dimensions conformes,
  avec symboles `~` pour budget×catégorie et segment via pont, plus règles de
  drill-across.
- `docs/data-dictionary.md` — définitions business de chaque `dim_*`, `fact_*`
  et `bridge_*` DuckDB, en complément des CSV sources bruts.
- `docs/decision-log.md` — huit décisions (D01–D08) reliant grain, SCD,
  drill-across, pont pondéré, types de faits S09 et KPIs officiels aux
  questions CEO du trimestre.
- `docs/metric-definitions.md` — cinq KPIs officiels (revenu, retours,
  livraison, promo, écart budget) avec formule SQL, grain, fréquence et
  valeurs observées sur le seed local.

## Test du passage de relais

1. Quelle est la table de faits principale, et quel est son grain ?
   → `fact_sales` : une ligne = une ligne de commande (`sale_line_id` +
   `order_number`). C'est le processus ventes de référence pour revenu,
   volume et marges.

2. Quelles dimensions sont historisées (SCD 2) ? Lesquelles ne le sont pas ?
   → SCD Type 2 : `dim_customer` (segment, ville, province) et `dim_store`
   (région). Type 1 : `dim_product`, `dim_channel`, `dim_segment_outrigger`.
   Hybride Type 2 + Type 1 : corrections de nom client et type de magasin
   écrasés. Type 3 : `dim_customer_scd3` pour segment actuel vs précédent.

3. Comment reproduire l'entrepôt depuis un clone vide ?
   → `pip install -r requirements.txt`, puis `.\run.ps1 generate`,
   `.\run.ps1 load`, `.\run.ps1 check`. Sur Unix/Codespace :
   `make generate && make load && make check`.

4. Où se trouve la preuve qu'un check de contrainte passe ?
   → `validation/checks.sql` définit les règles ; `.\run.ps1 check` écrit le
   résultat dans `validation/results/check_results.txt`. État courant :
   **31 PASS, 0 FAIL, 0 SKIP** (2026-06-18), incluant `FK_NOT_NULL`,
   `GRAIN_UNIQUE` et `BRIDGE_WEIGHT`.

5. Qui est le propriétaire fonctionnel de chaque fait ?
   → `fact_sales`, `fact_orders_transaction` : VP Commerce.
   `fact_returns` : VP Service client.
   `fact_inventory_snapshot`, `fact_daily_inventory` : VP Supply chain.
   `fact_budget` : CFO / Finance.
   `fact_order_pipeline` : VP Opérations / Fulfillment.
   `fact_promo_exposure` : VP Marketing.

## Preuve — KPI principal

Requête : revenu net mensuel (KPI #1 de `docs/metric-definitions.md`).

```sql
SELECT
    DATE_TRUNC('month', d."date") AS mois,
    ROUND(SUM(s.line_total), 2) AS net_revenue
FROM fact_sales AS s
JOIN dim_date AS d ON d.date_key = s.date_key
GROUP BY 1
ORDER BY 1;
```

| Métrique | Valeur observée | Interprétation |
|---|---|---|
| `net_revenue` (2025-01) | 62 630,86 $ | Revenu facturé en janvier 2025 sur le seed local — base comparable mois par mois pour le board |
| `net_revenue` (2025-12) | 54 228,47 $ | Dernier mois complet du jeu de données ; baisse observable pour prioriser l'analyse saisonnière |

## Réponse au CEO

L'entrepôt est transmissible. Les quatre documents de documentation, le journal
de décisions et les définitions de métriques permettent à l'équipe BI de
reproduire revenu facturé, taux de retour, taux de livraison, couverture promo
et écart réel vs budget sans appeler le Head of Data. La prochaine priorité
serait d'industrialiser le rechargement avec un pipeline dbt (GIS806), une fois
les définitions KPI figées comme contrat sémantique.
