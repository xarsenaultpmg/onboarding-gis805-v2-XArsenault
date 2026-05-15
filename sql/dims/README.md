# `sql/dims/` — tables de dimensions

Les dimensions décrivent le **contexte** : qui, quoi, où, quand, par quel canal. Chaque ligne
est une entité unique (un client, un produit, un magasin, une date, un canal).

## Ce qui va ici

Vos fichiers `.sql` qui créent les tables `dim_*` en partant des tables
`raw_*` chargées par `make load`. Un fichier par dimension :

```
sql/dims/
  dim_customer.sql
  dim_product.sql
  dim_store.sql
  dim_date.sql
  dim_channel.sql
  dim_customer_scd2.sql   <-- S03 (remplace ou coexiste avec dim_customer)
  dim_order_profile.sql   <-- S04 (junk dimension)
  dim_supplier.sql    <-- S06 (enterprise integration)
```

## Convention de nommage

- Fichier : `dim_<entité>.sql` en minuscules, underscores séparateurs.
- Table produite : même nom que le fichier sans l'extension.
- Clé substitut : `<entité>_key` (entier auto-incrémenté).
- Clé naturelle : `<entité>_id` (identifiant métier du système source).

## Par où commencer

Copiez `../templates/01_dim_from_raw.sql` et adaptez-le à votre dimension.
Pour la première dimension historisée (S03), copiez
`../templates/03_scd_type2.sql`.

## Quand cela devient obligatoire

**S02** — le fait `fact_sales` joint **cinq** dimensions avec SK :
`dim_date`, `dim_product`, `dim_store`, `dim_customer`, **`dim_channel`**
(cinq fichiers `sql/dims/`). Le numéro de commande **`order_number`** est une
**dimension dégénérée** dans le fait (pas de `dim_order`). Voir
[docs/schema-v1.md](../../docs/schema-v1.md) et [docs/s02-sample-brief.md](../../docs/s02-sample-brief.md).
