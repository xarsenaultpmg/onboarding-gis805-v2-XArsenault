# Brief conseil — Schéma en étoile ventes (S02)

## Question du CEO (S02)

Quel schéma en étoile rend la question exécutive **répétable et fiable chaque mois** ?

## Réponse en une page

NexaMart retient une **étoile ventes** centrée sur **`fact_sales`**, conforme au **lab S02** ([GIS805-02_lab.md](../lab-guides/GIS805-02_lab.md)). Le grain est **une ligne = une ligne de commande**, identifiée par **`sale_line_id`** et **`order_number`** (dimension dégénérée — pas de `dim_order`).

Le fait porte **cinq clés substitut** : **`product_key`**, **`customer_key`**, **`store_key`**, **`date_key`**, **`channel_key`**, vers les dimensions **date, produit, magasin, client et canal**. Les mesures sont **`revenue`**, **`quantity`**, **`discount_amount`** et **`cost`**.

Pour la question du **S01** (catégories × régions × trimestres), on agrège **`SUM(revenue)`** avec **`dim_product`**, **`dim_store`** (colonne **`région`**) et **`dim_date`**.

## Pourquoi c’est « board-ready »

- **Grain explicite** : tout le monde sait ce qu’une ligne représente avant d’interpréter un chiffre.
- **Dimensions partagées** : date, produit, magasin, client et canal pourront servir d’autres faits sans casser les définitions.
- **Preuve** : une requête SQL d’agrégation standard valide le modèle sur les données actuelles.

## Références techniques

- Conception détaillée et decision log : [docs/schema-v1.md](../schema-v1.md)
- Diagrammes : [diagrams/schema-v1.mmd](../../diagrams/schema-v1.mmd), [diagrams/schema-v1.drawio](../../diagrams/schema-v1.drawio)
- Requête de preuve : [sql/analysis/s02-first-answer.sql](../../sql/analysis/s02-first-answer.sql)
