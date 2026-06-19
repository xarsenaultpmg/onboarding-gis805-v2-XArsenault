# Dictionnaire de données — NexaMart

Ce document décrit les fichiers CSV produits par `make generate` et les tables
d'entrepôt construites dans DuckDB par `.\run.ps1 load`. Les sections CSV
documentent les sources brutes ; la section finale documente les tables
analytiques `dim_*`, `fact_*` et `bridge_*` utilisées dans les briefs.

Pour les KPIs officiels du handoff S11 (formule SQL, grain, fréquence et valeurs
observées sur DuckDB), voir [`docs/metric-definitions.md`](metric-definitions.md).
Les colonnes analytiques DuckDB ci-dessous complètent les CSV sources bruts.

## Lecture

- `team_N` = votre numéro d'équipe, calculé depuis votre username GitHub.
- Les tables `raw_*` dans DuckDB sont chargées depuis ces CSV par `make load`.
- Les tables `dim_*`, `fact_*` et `bridge_*` sont la couche à utiliser pour les
  analyses. Les CSV ne doivent pas être lus directement dans les briefs.

## Dimensions conformées partagées

*Lu par toutes les sessions.*

### `data/synthetic/team_N/shared/dim_channel.csv`

*Source : `scripts/datagen/gen_shared_seeds.py`*

| Colonne | Description |
|---|---|
| `channel_id` | Clé naturelle du canal (CH-WEB, CH-APP, etc.). |
| `channel_name` | Libellé du canal de vente. |
| `channel_type` | Famille du canal (online, physical, phone). |

### `data/synthetic/team_N/shared/dim_customer.csv`

*Source : `scripts/datagen/gen_shared_seeds.py`*

| Colonne | Description |
|---|---|
| `customer_id` | Clé naturelle du client (CUS-NNNNN). |
| `first_name` | Prénom du client. |
| `last_name` | Nom de famille du client. |
| `email_domain` | Domaine du courriel (pour analyses anonymes). |
| `city` | Ville du magasin ou du client. |
| `province` | Province canadienne (QC, ON, BC, AB). |
| `loyalty_segment` | Segment de fidélité (Platinum, Gold, Silver, Bronze, New, Inactive). |
| `join_date` | Date de création du compte client. |

### `data/synthetic/team_N/shared/dim_date.csv`

*Source : `scripts/datagen/gen_shared_seeds.py`*

| Colonne | Description |
|---|---|
| `date_key` | Clé naturelle de la date, format ISO YYYY-MM-DD. |
| `year` | Année (entier). |
| `quarter` | Trimestre 1-4. |
| `month` | Mois 1-12. |
| `month_name` | Nom du mois en anglais (pour affichage). |
| `week_iso` | Numéro de semaine ISO 8601. |
| `day_of_week` | Jour de la semaine 1-7 (lundi=1). |
| `day_name` | Nom du jour en anglais. |
| `is_weekend` | 1 si samedi/dimanche, sinon 0. |

### `data/synthetic/team_N/shared/dim_product.csv`

*Source : `scripts/datagen/gen_shared_seeds.py`*

| Colonne | Description |
|---|---|
| `product_id` | Clé naturelle du produit (PRD-NNNN). |
| `product_name` | Libellé commercial du produit. |
| `category` | Catégorie haut niveau (Electronics, Clothing, etc.). |
| `subcategory` | Sous-catégorie interne. |
| `brand` | Marque du produit. |
| `unit_cost` | Coût unitaire payé au fournisseur. |
| `unit_price` | Prix de vente suggéré (avant rabais). |

### `data/synthetic/team_N/shared/dim_store.csv`

*Source : `scripts/datagen/gen_shared_seeds.py`*

| Colonne | Description |
|---|---|
| `store_id` | Clé naturelle du magasin (STR-NNN). |
| `store_name` | Nom complet du magasin. |
| `city` | Ville du magasin ou du client. |
| `region` | Région administrative (Québec, Ontario, etc.). |
| `province` | Province canadienne (QC, ON, BC, AB). |
| `store_type` | Type de magasin (flagship, standard, compact, express). |

## S02 — Étoile & grain

*Grain d'une ligne de commande.*

### `data/synthetic/team_N/s02/fact_sales.csv`

*Source : `scripts/datagen/gen_s02_star_schema.py`*

| Colonne | Description |
|---|---|
| `sale_line_id` | Identifiant unique de la ligne de vente (grain de fact_sales). |
| `order_number` | Numéro de commande (dimension dégénérée). Une commande = plusieurs lignes. |
| `order_date` | Date de la commande. |
| `customer_id` | Clé naturelle du client (CUS-NNNNN). |
| `product_id` | Clé naturelle du produit (PRD-NNNN). |
| `store_id` | Clé naturelle du magasin (STR-NNN). |
| `channel_id` | Clé naturelle du canal (CH-WEB, CH-APP, etc.). |
| `quantity` | Quantité vendue sur la ligne. |
| `unit_price` | Prix de vente suggéré (avant rabais). |
| `discount_pct` | Pourcentage de rabais appliqué (0 à 25). |
| `net_price` | Prix net après rabais. |
| `line_total` | Total de la ligne (net_price × quantity). |

## S03 — Slowly Changing Dimensions

*Événements de changement à historiser.*

### `data/synthetic/team_N/s03/customer_changes.csv`

*Source : `scripts/datagen/gen_s03_scd_changes.py`*

| Colonne | Description |
|---|---|
| `customer_id` | Clé naturelle du client (CUS-NNNNN). |
| `change_date` | Date de l'événement de changement. |
| `change_type` | Nature du changement (city_move, segment_change, name_correction, province_change, region_reassign, type_upgrade). |
| `field_changed` | Champ concerné (city, segment, name, province). |
| `old_value` | Valeur avant le changement. |
| `new_value` | Valeur après le changement. |

### `data/synthetic/team_N/s03/store_changes.csv`

*Source : `scripts/datagen/gen_s03_scd_changes.py`*

| Colonne | Description |
|---|---|
| `store_id` | Clé naturelle du magasin (STR-NNN). |
| `change_date` | Date de l'événement de changement. |
| `change_type` | Nature du changement (city_move, segment_change, name_correction, province_change, region_reassign, type_upgrade). |
| `old_value` | Valeur avant le changement. |
| `new_value` | Valeur après le changement. |

## S04 — Dimensions dégénérées + junk

*Commandes avec drapeaux opérationnels.*

### `data/synthetic/team_N/s04/order_lines.csv`

*Source : `scripts/datagen/gen_s04_basket_flags.py`*

| Colonne | Description |
|---|---|
| `line_id` | Identifiant de ligne de commande (local au fichier S04). |
| `order_number` | Numéro de commande (dimension dégénérée). Une commande = plusieurs lignes. |
| `product_id` | Clé naturelle du produit (PRD-NNNN). |
| `quantity` | Quantité vendue sur la ligne. |
| `unit_price` | Prix de vente suggéré (avant rabais). |
| `line_total` | Total de la ligne (net_price × quantity). |

### `data/synthetic/team_N/s04/orders.csv`

*Source : `scripts/datagen/gen_s04_basket_flags.py`*

| Colonne | Description |
|---|---|
| `order_number` | Numéro de commande (dimension dégénérée). Une commande = plusieurs lignes. |
| `order_date` | Date de la commande. |
| `customer_id` | Clé naturelle du client (CUS-NNNNN). |
| `store_id` | Clé naturelle du magasin (STR-NNN). |
| `channel_id` | Clé naturelle du canal (CH-WEB, CH-APP, etc.). |
| `is_gift_wrapped` | Emballage cadeau demandé (0/1). |
| `is_express_shipping` | Livraison express (0/1). |
| `is_loyalty_redeemed` | Points de fidélité utilisés (0/1). |
| `is_promo_applied` | Promotion appliquée (0/1). |
| `is_employee_purchase` | Achat par un employé (0/1). |
| `is_online_pickup` | Ramassage en magasin après commande en ligne (0/1). |
| `is_fragile` | Article fragile (0/1). |
| `is_oversized` | Article hors gabarit (0/1). |

## S06 — Intégration entreprise

*Multi-fait : ventes, retours, inventaire, budget.*

### `data/synthetic/team_N/s06/fact_budget.csv`

*Source : `scripts/datagen/gen_s06_enterprise_integration.py`*

| Colonne | Description |
|---|---|
| `budget_id` | Identifiant unique de la ligne budgétaire. |
| `budget_month` | Premier jour du mois budgétaire (YYYY-MM-01). |
| `category` | Catégorie haut niveau (Electronics, Clothing, etc.). |
| `store_id` | Clé naturelle du magasin (STR-NNN). |
| `target_revenue` | Chiffre d'affaires cible pour la catégorie × magasin × mois. |
| `target_units` | Volume cible associé au revenue budget. |

### `data/synthetic/team_N/s06/fact_inventory_snapshot.csv`

*Source : `scripts/datagen/gen_s06_enterprise_integration.py`*

| Colonne | Description |
|---|---|
| `snapshot_id` | Identifiant unique du snapshot (grain : produit × magasin × date). |
| `snapshot_date` | Date du snapshot d'inventaire. |
| `product_id` | Clé naturelle du produit (PRD-NNNN). |
| `store_id` | Clé naturelle du magasin (STR-NNN). |
| `quantity_on_hand` | Stock disponible en magasin au jour du snapshot. |
| `quantity_on_order` | Stock commandé au fournisseur, pas encore reçu. |
| `reorder_point` | Seuil en dessous duquel réapprovisionner. |

### `data/synthetic/team_N/s06/fact_returns.csv`

*Source : `scripts/datagen/gen_s06_enterprise_integration.py`*

| Colonne | Description |
|---|---|
| `return_id` | Identifiant unique du retour. |
| `original_sale_line_id` | Clé étrangère vers fact_sales.sale_line_id. |
| `return_date` | Date du retour. |
| `product_id` | Clé naturelle du produit (PRD-NNNN). |
| `store_id` | Clé naturelle du magasin (STR-NNN). |
| `return_quantity` | Quantité retournée (≤ quantity vendue). |
| `refund_amount` | Montant remboursé au client. |
| `return_reason` | Motif du retour (defective, wrong_size, changed_mind, damaged_shipping, duplicate). |

### `data/synthetic/team_N/s06/fact_sales.csv`

*Source : `scripts/datagen/gen_s06_enterprise_integration.py`*

| Colonne | Description |
|---|---|
| `sale_line_id` | Identifiant unique de la ligne de vente (grain de fact_sales). |
| `order_number` | Numéro de commande (dimension dégénérée). Une commande = plusieurs lignes. |
| `order_date` | Date de la commande. |
| `customer_id` | Clé naturelle du client (CUS-NNNNN). |
| `product_id` | Clé naturelle du produit (PRD-NNNN). |
| `store_id` | Clé naturelle du magasin (STR-NNN). |
| `channel_id` | Clé naturelle du canal (CH-WEB, CH-APP, etc.). |
| `quantity` | Quantité vendue sur la ligne. |
| `unit_price` | Prix de vente suggéré (avant rabais). |
| `discount_pct` | Pourcentage de rabais appliqué (0 à 25). |
| `net_price` | Prix net après rabais. |
| `line_total` | Total de la ligne (net_price × quantity). |

## S07 — Dimensions spéciales

*Dates à rôles, hiérarchies, NULLs.*

### `data/synthetic/team_N/s07/customer_profile_bands.csv`

*Source : `scripts/datagen/gen_s07_special_dims.py`*

| Colonne | Description |
|---|---|
| `customer_id` | Clé naturelle du client (CUS-NNNNN). |
| `age_band` | Tranche d'âge (18-25, 26-35, 36-45, 46-55, 56-65, 65+). |
| `spend_band` | Tranche de dépense (low, medium, high, premium). |
| `frequency_band` | Fréquence d'achat (rare, occasional, regular, frequent). |

### `data/synthetic/team_N/s07/dim_geography.csv`

*Source : `scripts/datagen/gen_s07_special_dims.py`*

| Colonne | Description |
|---|---|
| `city` | Ville du magasin ou du client. |
| `region` | Région administrative (Québec, Ontario, etc.). |
| `province` | Province canadienne (QC, ON, BC, AB). |
| `country` | Pays (toujours 'Canada' dans ce jeu). |

### `data/synthetic/team_N/s07/fact_shipment.csv`

*Source : `scripts/datagen/gen_s07_special_dims.py`*

| Colonne | Description |
|---|---|
| `shipment_id` | Identifiant unique d'expédition. |
| `order_date` | Date de la commande. |
| `ship_date` | Date d'expédition (différente de order_date). |
| `delivery_date` | Date de livraison (NULL si en transit). |
| `product_id` | Clé naturelle du produit (PRD-NNNN). |
| `store_id` | Clé naturelle du magasin (STR-NNN). |
| `customer_id` | Clé naturelle du client (CUS-NNNNN). |
| `channel_id` | Clé naturelle du canal (CH-WEB, CH-APP, etc.). |
| `carrier` | Transporteur (NULL si inconnu). |
| `destination_city` | Ville de destination. |
| `destination_province` | Province de destination. |
| `delivery_status` | État (delivered, in_transit, returned, failed). |
| `shipping_cost` | Coût d'expédition facturé à NexaMart. |

## S08 — Ponts pondérés & SCD3

*Relations M:N et historique partiel.*

### `data/synthetic/team_N/s08/bridge_campaign_allocation.csv`

*Source : `scripts/datagen/gen_s08_bridges.py`*

| Colonne | Description |
|---|---|
| `allocation_id` | Identifiant unique de la ligne d'allocation campagne. |
| `campaign_id` | Clé naturelle de la campagne (CMP-NNN). |
| `segment` | Segment de fidélité associé (peut différer du segment 'principal'). |
| `budget_weight` | Pondération du budget pour ce segment (somme = 1.0 par campagne). |
| `planned_spend` | Dépense marketing planifiée, en dollars. |

### `data/synthetic/team_N/s08/bridge_customer_segment.csv`

*Source : `scripts/datagen/gen_s08_bridges.py`*

| Colonne | Description |
|---|---|
| `bridge_id` | Identifiant unique de la ligne du pont (une ligne = un client × un segment). |
| `customer_id` | Clé naturelle du client (CUS-NNNNN). |
| `segment` | Segment de fidélité associé (peut différer du segment 'principal'). |
| `weight` | Pondération du segment pour ce client (somme = 1.0 par client). |
| `effective_date` | Date d'entrée en vigueur de l'assignation au segment. |
| `is_primary` | 1 pour le segment de plus grand poids, 0 sinon. |

### `data/synthetic/team_N/s08/customer_scd3_history.csv`

*Source : `scripts/datagen/gen_s08_bridges.py`*

| Colonne | Description |
|---|---|
| `customer_id` | Clé naturelle du client (CUS-NNNNN). |
| `current_segment` | Segment actuel du client (SCD3). |
| `previous_segment` | Segment précédent du client (NULL si jamais changé). |
| `segment_change_date` | Date du dernier changement de segment (NULL si aucun). |
| `city` | Ville du magasin ou du client. |
| `province` | Province canadienne (QC, ON, BC, AB). |

### `data/synthetic/team_N/s08/dim_segment_outrigger.csv`

*Source : `scripts/datagen/gen_s08_bridges.py`*

| Colonne | Description |
|---|---|
| `segment` | Segment de fidélité associé (peut différer du segment 'principal'). |
| `discount_pct` | Pourcentage de rabais appliqué (0 à 25). |
| `free_shipping` | Livraison gratuite incluse pour le segment (0/1). |
| `priority_support` | Service client prioritaire (0/1). |
| `annual_reward_value` | Récompense annuelle en dollars pour le segment. |

## S09 — Quatre types de faits

*Transaction, snapshot, accumulating, factless.*

### `data/synthetic/team_N/s09/fact_daily_inventory.csv`

*Source : `scripts/datagen/gen_s09_fact_types.py`*

| Colonne | Description |
|---|---|
| `snapshot_id` | Identifiant unique du snapshot (grain : produit × magasin × date). |
| `snapshot_date` | Date du snapshot d'inventaire. |
| `product_id` | Clé naturelle du produit (PRD-NNNN). |
| `store_id` | Clé naturelle du magasin (STR-NNN). |
| `quantity_on_hand` | Stock disponible en magasin au jour du snapshot. |
| `quantity_on_order` | Stock commandé au fournisseur, pas encore reçu. |
| `days_of_supply` | Jours de couverture au rythme de vente courant (mesure semi-additive). |

### `data/synthetic/team_N/s09/fact_order_pipeline.csv`

*Source : `scripts/datagen/gen_s09_fact_types.py`*

| Colonne | Description |
|---|---|
| `pipeline_id` | Identifiant unique de la ligne de pipeline. |
| `order_id` | Identifiant de la commande (ORD-NNNNNN). |
| `order_date` | Date de la commande. |
| `payment_date` | Date du paiement (NULL si en attente). |
| `pick_date` | Date de préparation en entrepôt (NULL si pas encore). |
| `ship_date` | Date d'expédition (différente de order_date). |
| `delivery_date` | Date de livraison (NULL si en transit). |
| `current_status` | Jalon atteint (completed, pending_ship, pending_pick, pending_payment, cancelled). |
| `days_order_to_deliver` | Délai commande → livraison en jours (NULL si non complété). |
| `product_id` | Clé naturelle du produit (PRD-NNNN). |
| `store_id` | Clé naturelle du magasin (STR-NNN). |
| `customer_id` | Clé naturelle du client (CUS-NNNNN). |

### `data/synthetic/team_N/s09/fact_orders_transaction.csv`

*Source : `scripts/datagen/gen_s09_fact_types.py`*

| Colonne | Description |
|---|---|
| `transaction_id` | Identifiant unique de la transaction (grain fact_orders_transaction). |
| `transaction_date` | Date de la transaction. |
| `transaction_type` | Type d'événement (sale, return, exchange). |
| `product_id` | Clé naturelle du produit (PRD-NNNN). |
| `store_id` | Clé naturelle du magasin (STR-NNN). |
| `customer_id` | Clé naturelle du client (CUS-NNNNN). |
| `quantity` | Quantité vendue sur la ligne. |
| `amount` | Montant de la transaction (négatif pour un retour). |

### `data/synthetic/team_N/s09/fact_promo_exposure.csv`

*Source : `scripts/datagen/gen_s09_fact_types.py`*

| Colonne | Description |
|---|---|
| `exposure_id` | Identifiant unique de l'exposition à une campagne. |
| `exposure_date` | Date où le client a été exposé à la campagne. |
| `campaign_id` | Clé naturelle de la campagne (CMP-NNN). |
| `customer_id` | Clé naturelle du client (CUS-NNNNN). |
| `channel_id` | Clé naturelle du canal (CH-WEB, CH-APP, etc.). |

## Tables d'entrepôt DuckDB

### Dimensions

#### `dim_date`

| Colonne | Description business |
|---|---|
| `date_key` | Clé substitutive de la date utilisée par les faits. |
| `date` | Jour calendaire au format date, issu de `raw_dim_date.date_key`. |
| `year` | Année civile. |
| `quarter` | Trimestre civil. |
| `month` | Numéro de mois. |
| `month_name` | Nom du mois pour affichage. |
| `week_iso` | Semaine ISO. |
| `day_of_week` | Jour de semaine numérique. |
| `day_name` | Nom du jour pour affichage. |
| `is_weekend` | Indique samedi ou dimanche. |
| `loaded_at` | Date de chargement technique de la dimension. |

#### `dim_product`

| Colonne | Description business |
|---|---|
| `product_key` | Clé substitutive du produit. |
| `product_id` | Clé naturelle du produit source. |
| `name` | Nom commercial du produit. |
| `category` | Catégorie de référence pour drill-across avec budget. |
| `subcategory` | Sous-catégorie produit. |
| `brand` | Marque. |
| `unit_cost` | Coût unitaire utilisé pour calculer le coût des ventes. |
| `unit_price` | Prix de référence avant rabais. |
| `loaded_at` | Date de chargement technique. |

#### `dim_customer`

| Colonne | Description business |
|---|---|
| `customer_key` | Clé substitutive d'une version SCD2 du client. |
| `customer_id` | Clé naturelle du client source. |
| `name` | Nom client après corrections Type 1. |
| `segment` | Segment de fidélité historisé. |
| `city` | Ville client historisée. |
| `région` | Province client historisée dans le modèle courant. |
| `valid_from` | Début de validité de la version client. |
| `valid_to` | Fin de validité de la version client, ou `NULL` si courante. |
| `is_current` | Indique la version courante du client. |
| `loaded_at` | Date de chargement technique. |

#### `dim_store`

| Colonne | Description business |
|---|---|
| `store_key` | Clé substitutive d'une version SCD2 du magasin. |
| `store_id` | Clé naturelle du magasin source. |
| `name` | Nom du magasin. |
| `city` | Ville du magasin. |
| `région` | Région administrative historisée. |
| `province` | Province du magasin. |
| `store_type` | Type courant du magasin après écrasement Type 1. |
| `valid_from` | Début de validité de la version magasin. |
| `valid_to` | Fin de validité de la version magasin, ou `NULL` si courante. |
| `is_current` | Indique la version courante du magasin. |
| `loaded_at` | Date de chargement technique. |

#### `dim_channel`

| Colonne | Description business |
|---|---|
| `channel_key` | Clé substitutive du canal. |
| `channel_id` | Clé naturelle du canal source. |
| `channel_name` | Libellé du canal. |
| `channel_type` | Famille du canal : en ligne, physique ou téléphone. |
| `loaded_at` | Date de chargement technique. |

#### `dim_order_profile`

| Colonne | Description business |
|---|---|
| `profile_key` | Clé substitutive du profil de commande. |
| `is_gift_wrapped` | Indique une commande avec emballage cadeau. |
| `is_express_shipping` | Indique une livraison express. |
| `is_loyalty_redeemed` | Indique une utilisation de points de fidélité. |
| `is_promo_applied` | Indique une promotion appliquée. |
| `is_employee_purchase` | Indique un achat employé. |
| `is_online_pickup` | Indique un ramassage en magasin après commande en ligne. |
| `is_fragile` | Indique un article fragile. |
| `is_oversized` | Indique un article hors gabarit. |
| `profile_name` | Libellé business de la combinaison de drapeaux. |

#### `dim_segment_outrigger`

| Colonne | Description business |
|---|---|
| `segment_key` | Clé substitutive du segment. |
| `segment` | Segment de fidélité. |
| `discount_pct` | Rabais associé au segment. |
| `free_shipping` | Indique si le segment obtient la livraison gratuite. |
| `priority_support` | Indique si le segment reçoit un support prioritaire. |
| `annual_reward_value` | Valeur annuelle estimée des récompenses du segment. |

#### `dim_customer_scd3`

| Colonne | Description business |
|---|---|
| `customer_key` | Clé de la version courante du client. |
| `customer_id` | Clé naturelle du client. |
| `name` | Nom client courant. |
| `current_segment` | Segment actuel. |
| `previous_segment` | Segment précédent, conservé pour l'analyse de transition. |
| `segment_change_date` | Date du dernier changement de segment. |
| `city` | Ville courante du client. |
| `province` | Province courante du client. |

### Tables de faits

#### `fact_sales`

| Colonne | Description business |
|---|---|
| `product_key`, `customer_key`, `store_key`, `date_key`, `channel_key` | Clés conformes vers les dimensions principales. |
| `profile_key` | Profil opérationnel de la commande. |
| `sale_line_id` | Identifiant de la ligne de vente, grain de la table. |
| `order_number` | Numéro de commande conservé comme dimension dégénérée. |
| `revenue` | Revenu net de la ligne après rabais. |
| `line_total` | Alias conservé pour les checks et la compatibilité des requêtes. |
| `quantity` | Quantité vendue. |
| `discount_amount` | Montant de rabais en dollars. |
| `cost` | Coût estimé de la ligne. |

#### `fact_returns`

| Colonne | Description business |
|---|---|
| `product_key`, `customer_key`, `store_key`, `date_key`, `channel_key` | Clés conformes pour comparer les retours aux ventes. |
| `return_id` | Identifiant de la ligne de retour. |
| `original_sale_line_id` | Référence à la ligne de vente retournée. |
| `return_date` | Date du retour. |
| `return_reason` | Motif du retour. |
| `return_quantity` | Quantité retournée. |
| `refund_amount` | Montant remboursé. |

#### `fact_inventory_snapshot`

| Colonne | Description business |
|---|---|
| `date_key`, `product_key`, `store_key` | Clés conformes du snapshot. |
| `snapshot_id` | Identifiant du snapshot. |
| `snapshot_date` | Date de la photo d'inventaire. |
| `quantity_on_hand` | Stock disponible au jour du snapshot. |
| `quantity_on_order` | Stock commandé mais pas encore reçu. |
| `reorder_point` | Seuil de réapprovisionnement. |

#### `fact_budget`

| Colonne | Description business |
|---|---|
| `date_key`, `store_key` | Clés conformes mois et magasin. |
| `budget_id` | Identifiant de la ligne budgétaire. |
| `budget_month` | Mois budgétaire. |
| `category` | Catégorie produit au grain budget. |
| `target_revenue` | Revenu cible. |
| `target_quantity` | Unités cibles. |

#### `fact_orders_transaction`

| Colonne | Description business |
|---|---|
| `date_key`, `product_key`, `store_key`, `customer_key` | Clés conformes de la transaction. |
| `transaction_id` | Identifiant atomique de transaction. |
| `transaction_date` | Date de la transaction. |
| `transaction_type` | Type d'événement : vente, retour ou échange. |
| `quantity` | Quantité de la transaction. |
| `amount` | Montant de la transaction, négatif pour certains retours. |

#### `fact_daily_inventory`

| Colonne | Description business |
|---|---|
| `date_key`, `product_key`, `store_key` | Clés conformes du snapshot quotidien. |
| `snapshot_id` | Identifiant du snapshot quotidien. |
| `snapshot_date` | Date du snapshot. |
| `quantity_on_hand` | Stock disponible au jour donné. |
| `quantity_on_order` | Stock commandé. |
| `days_of_supply` | Jours de couverture au rythme de vente courant. |

#### `fact_order_pipeline`

| Colonne | Description business |
|---|---|
| `order_date_key`, `product_key`, `store_key`, `customer_key` | Clés conformes de la commande suivie. |
| `pipeline_id` | Identifiant de la ligne de pipeline. |
| `order_id` | Identifiant de commande, grain de la table. |
| `order_date`, `payment_date`, `pick_date`, `ship_date`, `delivery_date` | Jalons du cycle de vie de la commande. |
| `current_status` | Statut courant dans le pipeline. |
| `days_order_to_deliver` | Délai commande vers livraison pour les commandes livrées. |
| `reached_payment`, `reached_pick`, `reached_ship`, `reached_delivery` | Flags indiquant les jalons atteints. |

#### `fact_promo_exposure`

| Colonne | Description business |
|---|---|
| `date_key`, `customer_key`, `channel_key` | Clés conformes de l'exposition. |
| `exposure_id` | Identifiant de l'exposition. |
| `exposure_date` | Date d'exposition à la campagne. |
| `campaign_id` | Identifiant de campagne conservé comme dimension dégénérée. |

### Ponts

#### `bridge_customer_segment`

| Colonne | Description business |
|---|---|
| `bridge_id` | Identifiant de la ligne du pont. |
| `customer_key` | Version client reliée au segment. |
| `segment_key` | Segment relié au client. |
| `weight` | Poids d'attribution du client au segment ; la somme doit valoir 1.0 par client. |
| `effective_date` | Date d'entrée en vigueur de l'appartenance. |
| `is_primary` | Segment principal pour les rapports non pondérés, à utiliser avec prudence. |
