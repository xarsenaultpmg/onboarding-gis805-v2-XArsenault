# Bus Matrix — entrepôt NexaMart

> **Mettez à jour ce document après chaque séance** où vous ajoutez une table.
> Ce tableau est la **carte de conformité** : quelles dimensions sont partagées
> (conformes) entre quelles tables de faits ?
>
> Le bus matrix est le test ultime du drill-across : si deux tables de faits
> partagent un ✓ sur la même ligne, vous pouvez les interroger ensemble via
> une dimension conformée — sans jointure directe fait-à-fait.

## Convention

| Symbole | Signification |
|---|---|
| ✓ | Dimension conforme — clé de substitution `_key` présente dans ce fait |
| [r] | Role-playing : même `dim_date`, plusieurs FK distinctes dans le même fait |
| ◐ | Accès via bridge — double-comptage possible sans `SUM(weight)` |
| — | Non applicable — décision documentée dans `docs/decision-log.md` |
| ? | À vérifier dans votre implémentation |

---

## Matrice de conformité

> **Colonnes** = tables de faits · **Lignes** = dimensions
> Remplissez selon **votre** implémentation — pas le modèle de référence.
> Une cellule vide est une décision : documentez-la dans `decision-log.md`.

| Dimension | `fact_sales` | `fact_returns` | `fact_orders_transaction` | `fact_daily_inventory` | `fact_order_pipeline` | `fact_budget` | `fact_promo_exposure` |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `dim_date` | ✓ | ✓ | ✓ | ✓ | ✓ [r]×5 | ✓ | ✓ |
| `dim_customer` | ✓ | ✓ | ✓ | — | ✓ | — | ✓ |
| `dim_product` | ✓ | ✓ | ✓ | ✓ | — | ✓ | — |
| `dim_store` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| `dim_channel` | ✓ | ? | ✓ | — | ✓ | — | ✓ |
| `dim_campaign` | — | — | — | — | — | — | ✓ |
| `dim_order_profile` (junk) | — | — | ✓ | — | — | — | — |
| `dim_segment` (via bridge) | ◐ | — | ◐ | — | — | — | — |

---

## Notes

**`dim_date [r]×5` dans `fact_order_pipeline`**
Les cinq jalons utilisent `dim_date` sous des alias distincts :
`order_date_key`, `payment_date_key`, `pick_date_key`, `ship_date_key`,
`delivery_date_key`. Une seule table physique, cinq rôles — c'est le
**role-playing** étudié en S07. Chaque jointure doit avoir un alias distinct
(`d_order`, `d_ship`, etc.).

**`dim_segment ◐`**
`dim_segment` n'est pas jointe directement aux tables de faits. L'accès
passe par `bridge_customer_segment`. Pour tout calcul de revenu par segment :
```sql
SUM(f.line_total * b.weight)   -- pondéré = correct
SUM(f.line_total)              -- sans weight = double-comptage (FAUX)
```
Voir S08.

**`dim_channel ?` dans `fact_returns`**
Vérifiez si votre implémentation inclut `channel_key` dans `fact_returns`.
Si oui, passez `?` à `✓` et documentez la décision. Si non, passez à `—`.

**`dim_order_profile`**
Dimension poubelle (*junk*) regroupant les indicateurs discrets de la
transaction (`transaction_type`, `is_promotional`, etc.). Connectée
uniquement à `fact_orders_transaction` — grain identique.

---

## Vérification avant S11

- [ ] Ma `dim_date` partage le même `date_key` entre tous mes faits ?
- [ ] Chaque `✓` correspond à une FK réelle dans mon schéma DuckDB ?
- [ ] Les cellules `—` sont-elles justifiées dans `decision-log.md` ?
- [ ] La matrice est à jour avec mes 7 tables de faits (après S09) ?
- [ ] Les cellules `?` ont été résolues (`✓` ou `—`) ?
