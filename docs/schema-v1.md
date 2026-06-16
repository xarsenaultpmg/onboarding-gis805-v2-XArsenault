# Schéma en étoile NexaMart — version 1 (S02)

## Portée

Ce document décrit le **premier schéma en étoile** centré sur les ventes NexaMart. Il formalise le **grain**, les **dimensions** conformes v1 et le lien avec la **couche physique** : tables `raw_*` chargées depuis les CSV, puis dimensions **`dim_*`** matérialisées dans DuckDB par `sql/dims/`.

- Diagramme Mermaid : [diagrams/schema-v1.mmd](../diagrams/schema-v1.mmd)
- Diagramme Draw.io (éditable) : [diagrams/schema-v1.drawio](../diagrams/schema-v1.drawio)
- Preuve SQL : [sql/analysis/s02-first-answer.sql](../sql/analysis/s02-first-answer.sql)
- Référence lab : [docs/lab-guides/GIS805-02_lab.md](lab-guides/GIS805-02_lab.md), exemple annoté [docs/s02-sample-brief.md](s02-sample-brief.md)

## Modèle cible (S02 — lab)

Le schéma suit le **Sprint 1 / lab S02** : cinq dimensions reliées au fait par des **clés substitut** (`*_key`), sans table **`dim_order`**.

- **Fait `fact_sales`** : `product_key`, `customer_key`, `store_key`, `date_key`, `channel_key` ; identité de grain **`sale_line_id`** ; dimension dégénérée **`order_number`** ; mesures **`revenue`**, **`quantity`**, **`discount_amount`**, **`cost`** (`line_total` dupliqué sous le nom `revenue` pour les briefs ; colonne `line_total` conservée pour les checks du dépôt).
- **Dimensions** : `dim_date`, `dim_product`, `dim_store`, `dim_customer`, `dim_channel` (cinq fichiers dans `sql/dims/`).

## Grain statement (contrat de conception)

**Une ligne dans `fact_sales` = une ligne de commande** (un article dans une commande). Le grain est vérifiable par **`(order_number, sale_line_id)`** (voir `validation/checks.sql`). **`order_number`** est une **dimension dégénérée** : elle reste dans le fait, sans dimension propre.

## Table de faits `fact_sales` (logique)

| Rôle | Colonnes |
|------|-----------|
| FK substitut (pas de `*_id` de dimension dans le fait) | `product_key`, `customer_key`, `store_key`, `date_key`, `channel_key` |
| Identité de grain | `sale_line_id` |
| Dimension dégénérée | `order_number` |
| Mesures | `revenue`, `quantity`, `discount_amount`, `cost` |

`revenue` = `line_total` source ; `discount_amount` = `quantity × unit_price × discount_pct` ; `cost` = `quantity × unit_cost` (via `dim_product`).

## Dimensions v1

| Dimension | Attributs principaux |
|-----------|----------------------|
| `dim_product` | `product_key`, `name`, `category`, `subcategory`, `brand`, `unit_cost`, … |
| `dim_customer` | `customer_key`, `name`, `segment`, `city`, `"région"` (province source) |
| `dim_date` | `date_key`, `"date"`, `month`, `quarter`, `year`, … |
| `dim_store` | `store_key`, `name`, `city`, `"région"` (region source), `province` |
| `dim_channel` | `channel_key`, `channel_id`, `channel_name`, `channel_type` |

Les scripts [sql/dims/](../sql/dims/) lisent les **`raw_dim_*`**.

## Dimensions conformes et drill-across

Les dimensions **date**, **produit** et **magasin** sont **conformes** entre elles : mêmes définitions d’attributs (`quarter`, `category`, `region`) quel que soit le fait qui les consomme. Une fois d’autres faits ajoutés (retours, inventaire, etc.), le partage de ces dimensions permettra le **drill-across** sans réconcilier des définitions divergentes.

## Clés substitutives (SK) et SCD — périmètre S02

Les fichiers `sql/dims/*.sql` matérialisent les **SK** ; [sql/facts/fact_sales.sql](../sql/facts/fact_sales.sql) joint les dimensions via **`*_key`** uniquement (pas de `product_id`, `store_id`, etc. dans le fait). Les **SCD** restent hors périmètre S02.

## Couche physique dans DuckDB

1. **Landing** : `raw_*` — import CSV par [src/run_pipeline.py](../src/run_pipeline.py).
2. **Dimensions** : `dim_date`, `dim_product`, `dim_store`, `dim_customer`, `dim_channel`.
3. **Fait** : [sql/facts/fact_sales.sql](../sql/facts/fact_sales.sql).
4. **Preuve S02** : [sql/analysis/s02-first-answer.sql](../sql/analysis/s02-first-answer.sql) — `SUM(revenue)` par catégorie / région / trimestre.

## Decision log — choix de grain (trace processus)

| Date (S02) | Décision | Justification métier |
|------------|----------|----------------------|
| 2026-05 | Grain = ligne de commande (`sale_line_id`, `order_number`) | Le CEO demande des **catégories** et des **régions** : il faut conserver le niveau **article** dans le fait. |
| 2026-05 | Rejet du grain « une ligne = client × mois » | Inutilisable pour isoler une catégorie ; empêcherait les analyses de panier fines. |
| 2026-05 | `order_number` en dimension dégénérée (pas de `dim_order`) | Alignement lab S02 / [s02-sample-brief.md](s02-sample-brief.md) ; la commande n’a pas besoin d’une dimension séparée à ce stade. |
| 2026-05 | Cinq FK : date, produit, magasin, client, **canal** | Liste Sprint 1 (`dim_channel.sql`) ; le canal est un axe analytique réel dans les ventes. |
| 2026-05 | Mesures `revenue`, `discount_amount`, `cost` | `revenue` = chiffre d’affaires ligne ; coût = quantité × `unit_cost`. |
