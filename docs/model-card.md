# Model Card — entrepôt NexaMart

Cette model card documente l'entrepôt analytique NexaMart tel qu'il existe
au handoff S11 (v0.11). Elle sert à un analyste junior qui doit comprendre le modèle,
ses grains, ses limites et ses règles de validation sans relire tout le SQL.

## 1. Identification

- **Nom du modèle :** NexaMart Data Warehouse (GIS805)
- **Propriétaire :** Xavier Arsenault, Head of Data (simulation GIS805)
- **Dernière mise à jour :** 2026-06-18 (S10, intégration revue par les pairs)
- **Version :** 0.11, handoff pack S11

## 2. Intention

### 2.1 Questions business couvertes

- Quel revenu, coût et volume NexaMart génère-t-il par produit, magasin,
  client, canal et période ?
- Quels produits, régions ou périodes concentrent les retours et les
  remboursements ?
- Le board peut-il comparer ventes, retours, inventaire et budget sans
  multiplier les montants par une mauvaise jointure entre faits ?
- Quels segments clients reçoivent le revenu quand un client appartient à
  plusieurs segments, et quelle est la différence entre attribution naïve et
  attribution pondérée ?
- Quels processus NexaMart relèvent d'une table transactionnelle, d'un
  snapshot périodique, d'un snapshot accumulatif ou d'une table factless ?

### 2.2 Questions hors scope

- Le modèle ne prédit pas la demande future ; il décrit les faits générés
  par le seed local.
- Il ne supporte pas encore le ciblage nominatif ou les données personnelles
  identifiables, car les clients sont synthétiques et les courriels sont
  réduits au domaine.
- Il ne modélise pas les paiements, split payments, taxes ou frais de
  livraison comme processus de faits séparés.

## 3. Structure

### 3.1 Tables de faits

| Fact | Grain | Type | Mesures principales | Dimensions reliées |
|---|---|---|---|---|
| `fact_sales` | Une ligne de commande (`sale_line_id` + `order_number`) | Transaction | `revenue`, `line_total`, `quantity`, `discount_amount`, `cost` | `dim_date`, `dim_product`, `dim_store`, `dim_customer`, `dim_channel`, `dim_order_profile` |
| `fact_returns` | Une ligne de retour (`return_id`) | Transaction | `refund_amount`, `return_quantity` | `dim_date`, `dim_product`, `dim_store`, `dim_customer`, `dim_channel` |
| `fact_inventory_snapshot` | Produit x magasin x date de snapshot | Periodic snapshot | `quantity_on_hand`, `quantity_on_order`, `reorder_point` | `dim_date`, `dim_product`, `dim_store` |
| `fact_budget` | Mois x catégorie x magasin | Periodic snapshot budgétaire | `target_revenue`, `target_quantity` | `dim_date`, `dim_store`, catégorie conforme par libellé |
| `fact_orders_transaction` | Une transaction atomique (`transaction_id`) | Transaction | `quantity`, `amount` | `dim_date`, `dim_product`, `dim_store`, `dim_customer` |
| `fact_daily_inventory` | Produit x magasin x jour | Periodic snapshot | `quantity_on_hand`, `quantity_on_order`, `days_of_supply` | `dim_date`, `dim_product`, `dim_store` |
| `fact_order_pipeline` | Une commande suivie dans son cycle de vie (`order_id`) | Accumulating snapshot | jalons, `days_order_to_deliver`, flags de jalons atteints | `dim_date` comme date de commande, `dim_product`, `dim_store`, `dim_customer` |
| `fact_promo_exposure` | Client x campagne x date d'exposition | Factless | aucune mesure ; la présence de la ligne est le fait | `dim_date`, `dim_customer`, `dim_channel` |

Mesures et additivité :

| Mesure | Table | Additivité | Note |
|---|---|---|---|
| `line_total`, `revenue`, `quantity` | `fact_sales` | Additive | Sommable par produit, magasin, période. |
| `refund_amount`, `return_quantity` | `fact_returns` | Additive | Comparer aux ventes seulement après agrégation commune. |
| `target_revenue`, `target_quantity` | `fact_budget` | Additive | Grain catégorie × magasin × mois seulement. |
| `quantity_on_hand`, `days_of_supply` | `fact_daily_inventory`, `fact_inventory_snapshot` | Semi-additive | Moyenne ou dernier jour sur l'axe temps ; ne pas sommer sur plusieurs dates. |
| `days_order_to_deliver`, flags de jalon | `fact_order_pipeline` | Non additive | Délais et états ; agréger par commande ou par période avec prudence. |
| Présence de ligne | `fact_promo_exposure` | Factless | `COUNT(*)` ou anti-jointure ; pas de montant financier. |
| `line_total * weight` | `fact_sales` × pont | Additive après pondération | Total pondéré par segment réconciliable au revenu réel. |

Les définitions KPI testées (formule, grain, fréquence, valeur observée) sont dans
`docs/metric-definitions.md`.

### 3.2 Dimensions

| Dimension | Type SCD | Clés | Notes |
|---|---|---|---|
| `dim_date` | Type 1 | `date_key`, `date` | Calendrier conforme pour jours, mois, trimestres et semaines ISO. |
| `dim_customer` | Type 2 + Type 1 | `customer_key`, `customer_id` | Segment, ville et province sont historisés ; corrections de nom sont écrasées. |
| `dim_store` | Type 2 + Type 1 | `store_key`, `store_id` | Région historisée ; type de magasin écrasé quand il s'agit d'une classification courante. |
| `dim_product` | Type 1 | `product_key`, `product_id` | Produit, catégorie, sous-catégorie, marque, coût et prix de référence. |
| `dim_channel` | Type 1 | `channel_key`, `channel_id` | Canal de vente et type de canal. |
| `dim_order_profile` | Junk dimension | `profile_key` | Regroupe huit drapeaux opérationnels de commande en profils nommés. |
| `dim_segment_outrigger` | Type 1 | `segment_key`, `segment` | Attributs de segment utilisés par le pont pondéré. |
| `dim_customer_scd3` | Type 3 | `customer_key`, `customer_id` | Segment actuel et segment précédent pour analyser les transitions récentes. |

### 3.3 Ponts et cas particuliers

- `bridge_customer_segment` modélise l'appartenance M:N entre clients et
  segments. La règle de conservation est `SUM(weight) = 1.0` par client.
- `fact_budget.category` n'a pas de `product_key` ; la conformité avec
  `dim_product` est donc valide seulement au grain catégorie.
- `order_number`, `transaction_id`, `order_id`, `campaign_id` et
  `original_sale_line_id` sont des dimensions dégénérées conservées dans les
  faits quand aucune dimension descriptive séparée n'est utile.
- Les dates de `fact_order_pipeline` sont des jalons dans une même ligne :
  `order_date`, `payment_date`, `pick_date`, `ship_date`, `delivery_date`.

### 3.4 Politique NULL et membres inconnus

| Situation | Traitement | Exemple |
|---|---|---|
| FK obligatoire vers une dimension conforme | `INNER JOIN` au chargement ; aucune FK `*_key` NULL dans les faits contrôlés par `FK_NOT_NULL` | `fact_sales.product_key`, `customer_key`, `store_key`, `date_key`, `channel_key` |
| FK optionnelle (couverture partielle) | `LEFT JOIN` ; `NULL` signifie « non applicable » ou « source absente » | `fact_sales.profile_key` quand `order_number` n'existe pas dans `raw_orders` (S04) |
| Jalons non atteints (accumulating snapshot) | Colonnes de date laissées à `NULL` ; ce n'est pas une erreur de chargement | `fact_order_pipeline.payment_date`, `delivery_date` pour commandes en cours |
| Mesures dérivées sur cycle incomplet | `NULL` jusqu'à ce que le jalon final soit connu | `days_order_to_deliver` quand `delivery_date IS NULL` |
| Division par zéro dans les KPIs | `NULLIF(dénominateur, 0)` dans les formules publiées | taux de retour, couverture promo dans `docs/metric-definitions.md` |
| Membre inconnu (`key = -1`) | Non utilisé dans ce modèle : les faits principaux résolvent toutes les FK obligatoires au chargement. Si une source ajoute des valeurs manquantes, introduire une ligne `-1` dans la dimension concernée avant de remplacer les `NULL`. | voir `docs/worked-examples/s07-role-playing-dates-walkthrough.md` |

Règle opérationnelle : un `NULL` dans une FK contrôlée par `FK_NOT_NULL` est une anomalie
à corriger au pipeline. Un `NULL` dans un jalon de pipeline ou dans `profile_key`
a un sens business documenté et ne doit pas être remplacé aveuglément par zéro.

## 4. Hypothèses clés et décisions structurantes

- Le grain de `fact_sales` reste la ligne de commande, pas l'en-tête de
  commande, pour préserver l'analyse par produit et catégorie.
- Les faits ne sont jamais joints directement entre eux pour un drill-across ;
  ils sont d'abord agrégés au grain commun de la question.
- `dim_customer` et `dim_store` utilisent le SCD Type 2 seulement pour les
  attributs qui changent l'interprétation historique d'un rapport.
- Les combinaisons de drapeaux opérationnels vivent dans `dim_order_profile`
  pour éviter huit colonnes répétées dans les rapports.
- Les segments clients M:N utilisent un pont pondéré pour éviter de créer du
  revenu fictif.
- Les quatre faits S09 sont séparés par type de processus, car additionner un
  snapshot quotidien ou traiter une exposition comme un montant donnerait des
  conclusions trompeuses.

Le détail de ces choix est dans `docs/decision-log.md`.

## 5. Qualité et fiabilité

### 5.1 Checks actifs

| Check | Ce qu'il protège | Référence |
|---|---|---|
| `TABLE_EXISTS` | Présence des tables attendues dans DuckDB | `validation/checks.sql` |
| `ROW_COUNT` | Cardinalités minimales des dimensions et faits clés | `validation/checks.sql` |
| `PK_UNIQUE` | Unicité des clés dimensionnelles | `validation/checks.sql` |
| `SCD2_ONE_CURRENT` | Au plus une version courante par client | `validation/checks.sql` |
| `FK_NOT_NULL` | Résolution des FK de `fact_sales` | `validation/checks.sql` |
| `GRAIN_UNIQUE` | Unicité du grain `fact_sales` | `validation/checks.sql` |
| `BRIDGE_WEIGHT` | Somme des poids de segment = 1.0 | `sql/checks/s08-weighted-reconciliation.sql` |

Les résultats courants sont produits par `.\run.ps1 check` dans
`validation/results/`.

### 5.2 Limites connues

- `dim_customer` contient une colonne `"région"` qui représente la province
  du client ; les rapports exécutifs doivent nommer clairement cet axe.
- `bridge_customer_segment` joint toutes les versions SCD2 d'un client pour
  couvrir l'historique ; les analyses temporelles fines doivent filtrer la
  version client appropriée.
- `fact_daily_inventory` et `fact_inventory_snapshot` sont semi-additifs :
  sommer le stock sur plusieurs jours gonfle artificiellement le niveau de
  stock.
- `fact_promo_exposure` ne prouve pas une conversion ou un achat ; elle prouve
  seulement l'exposition à une campagne.

## 6. Audience et usages acceptables

### 6.1 Pour qui

- Board NexaMart et CEO : décisions hebdomadaires sur ventes, retours,
  inventaire, budget, segments et promotions.
- Head of Data : validation de grains, SCD, ponts et règles de drill-across.
- Analyste junior : requêtes ad hoc au-dessus des dimensions conformes.

### 6.2 Pour quoi, pas

- Utiliser le warehouse pour des rapports agrégés, des comparaisons de
  performance et des preuves de modélisation.
- Ne pas l'utiliser pour des décisions client nominatives, de la prévision ou
  des analyses temps réel.
- Ne pas joindre deux tables de faits ligne à ligne ; toujours agréger chaque
  fait au grain commun avant de comparer.

## 7. Reproductibilité

- **Seed :** déterministe depuis le username GitHub.
- **Pipeline Windows :** `.\run.ps1 generate`, `.\run.ps1 load`,
  `.\run.ps1 check`.
- **Pipeline Unix :** `make generate && make load && make check`.
- **Version du code :** le commit courant est l'état canonique du modèle.

## 8. Historique

| Date | Version | Changement majeur | Référence |
|---|---|---|---|
| 2026-05-10 | 0.01 | Exploration initiale et premier brief CEO | `answers/S01_executive_brief.md` |
| 2026-05-14 | 0.02 | Première étoile `fact_sales` avec dimensions conformes | `docs/schema-v1.md` |
| 2026-05-21 | 0.03 | Politique SCD client et magasin | `docs/scd-policy.md` |
| 2026-05-25 | 0.04 | Dimension dégénérée et junk dimension de commande | `docs/profiles.md` |
| 2026-06-04 | 0.07 | Intégration entreprise ventes, retours, inventaire et budget | `docs/bus-matrix.md` |
| 2026-06-08 | 0.08 | Ponts pondérés et SCD Type 3 | `docs/board-briefs/s08-overlap-risk.md` |
| 2026-06-14 | 0.09 | Quatre types de tables de faits | `docs/fact-type-decision-tree.md` |
| 2026-06-15 | 0.10 | Handoff pack S10 en préparation | `docs/defense-template.md` |
| 2026-06-18 | 0.11 | KPIs officiels testés après revue par les pairs | `docs/metric-definitions.md` |

---

*Cette model card est un livrable vivant. À chaque séance, elle doit permettre
à un remplaçant de comprendre le modèle et ses risques sans relire le SQL.*
