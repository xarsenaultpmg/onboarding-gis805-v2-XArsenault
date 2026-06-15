# Définitions de métriques — NexaMart

> **Minimum 4 KPIs couvrant au moins 2 tables de faits différentes.**
> Ce document complète votre handoff pack : il traduit vos requêtes SQL en
> KPIs compréhensibles par le CEO.
>
> Chaque formule SQL doit être **testée sur votre DuckDB** avant la remise S11.
> Un KPI sans valeur observée est un KPI non livrable.

## Format d'une entrée

| Champ | Contenu attendu |
|---|---|
| **Nom** | Nom court utilisable dans un tableau de bord |
| **Définition business** | Ce que le CEO peut décider avec ce chiffre — sans jargon SQL |
| **Formule SQL** | Requête exécutable, grain explicite, alias de colonnes clairs |
| **Source** | Tables interrogées (`fact_*`, `dim_*`) |
| **Fréquence** | À quelle fréquence ce KPI est recalculé en production |

---

## KPIs de votre modèle

| Nom | Définition business | Formule SQL (grain explicite) | Source | Fréquence |
|---|---|---|---|---|
| **Revenu net mensuel** | Montant total facturé aux clients en CAD par mois — base de toute décision de pricing et de performance | `SELECT d.year_month, ROUND(SUM(s.line_total), 2) AS net_revenue FROM fact_sales s JOIN dim_date d ON d.date_key = s.date_key GROUP BY d.year_month ORDER BY d.year_month` | `fact_sales`, `dim_date` | Mensuel |
| **Taux de livraison** | % de commandes ayant franchi le jalon livraison — mesure directe de l'efficacité opérationnelle entrepôt | `SELECT ROUND(100.0 * COUNT(delivery_date) / NULLIF(COUNT(*), 0), 1) AS pct_delivery FROM fact_order_pipeline` | `fact_order_pipeline` | Quotidien |
| <!-- KPI 3 : nom --> | <!-- Ce que le CEO décide avec ce chiffre → pas de jargon technique --> | <!-- SELECT ... FROM fact_* JOIN dim_* ... GROUP BY ... --> | <!-- fact_* + dim_* --> | <!-- Quotidien / Hebdo / Mensuel / Trimestriel --> |
| <!-- KPI 4 : nom --> | <!-- définition business --> | <!-- formule SQL complète, grain explicite --> | <!-- source --> | <!-- fréquence --> |

> **Idées pour KPI 3 et 4 :**
> - Revenu par segment de fidélité (`fact_sales` × `bridge_customer_segment` × `dim_segment_outrigger`)
> - Couverture campagne — % de clients actifs exposés (`fact_promo_exposure` + anti-jointure)
> - Stock moyen par magasin (`fact_daily_inventory` grain produit×magasin×jour → `AVG`, jamais `SUM`)
> - Taux de retour (`COUNT(fact_returns) / COUNT(fact_sales)` par catégorie)
> - Délai moyen pick → ship en jours (`fact_order_pipeline`, jalons `pick_date` et `ship_date`)
> - Écart réel vs cible (`fact_sales` drill-across `fact_budget` via `dim_store` et `dim_date`)

---

## Valeurs observées (à remplir avant soumission)

Exécutez chaque formule et notez le chiffre clé obtenu :

| KPI | Valeur observée sur votre DuckDB | Testé ? |
|---|---|---|
| Revenu net mensuel | ex. `2026-01 : 87 432,50 $` | [ ] |
| Taux de livraison | ex. `70,4 %` | [ ] |
| KPI 3 | | [ ] |
| KPI 4 | | [ ] |

---

## Règles de qualité

1. **Grain explicite** — la formule doit indiquer le niveau d'agrégation. `SUM(revenue)` seul n'est pas un KPI livrable. `SUM(revenue) GROUP BY dim_date.month` l'est.
2. **Alias clairs** — chaque colonne de résultat doit avoir un alias lisible (`AS net_revenue`, pas `AS col1`).
3. **NULLs traités** — utilisez `NULLIF(COUNT(*), 0)` pour éviter la division par zéro. Documentez comment les NULLs sont interprétés.
4. **Au moins 2 tables de faits différentes** — si vos 4 KPIs viennent tous de `fact_sales`, vous n'avez pas démontré la portée de votre modèle.
