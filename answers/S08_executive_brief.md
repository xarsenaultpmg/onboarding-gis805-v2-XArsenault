# Brief exécutif — S08 : Segments chevauchants et pont pondéré NexaMart

> **Question du CEO (S08) :** comment allouer les coûts et comprendre les segments clients qui se chevauchent sans double-compter ?

## Réponse exécutive

Oui, mais seulement si les rapports de segmentation utilisent un **pont pondéré**. Sur mon seed `team_3577855103`, le revenu réel de `fact_sales` est de **661 114,94 $**. Une jointure naïve entre ventes et segments monte artificiellement à **885 282,55 $**, soit **224 167,61 $** de revenu dupliqué.

La correction est `bridge_customer_segment` : chaque vente est répartie selon `weight`, et les poids somment à **1,0** par `customer_key`. Avec cette méthode, le total pondéré revient exactement à **661 114,94 $**.

## Décisions de modélisation

| Élément | Décision |
|---|---|
| Grain du pont | Une ligne = un `customer_key` × un `segment_key` × un `weight`. |
| Clé client | Le pont utilise `customer_key`, pas `customer_id`, pour couvrir les versions SCD2 utilisées par `fact_sales`. |
| Dimension segment | `dim_segment_outrigger` porte les attributs de segment et fournit `segment_key`. |
| Règle de validation | Aucun rapport segmenté n'est accepté sans `SUM(weight) = 1,0` par client et total pondéré = total réel. |
| SCD3 | `dim_customer_scd3` sert à comparer `previous_segment` et `current_segment` sans remplacer l'historique SCD2. |

## Preuve — allocation du revenu

Fichier : [`sql/bridges/s08-weighted-allocation.sql`](../sql/bridges/s08-weighted-allocation.sql)

| Segment | Revenu naïf | Attribution primaire | Revenu pondéré | Coût campagne alloué | Surévaluation naïve |
|---|---:|---:|---:|---:|---:|
| Platinum | 182 402,58 $ | 135 242,31 $ | 136 376,28 $ | 10 510,50 $ | 46 026,30 $ |
| New | 175 726,40 $ | 131 584,09 $ | 130 821,32 $ | 87 728,72 $ | 44 905,08 $ |
| Inactive | 145 389,11 $ | 126 759,21 $ | 115 222,16 $ | 0,00 $ | 30 166,95 $ |
| Gold | 144 555,35 $ | 104 009,37 $ | 105 783,11 $ | 40 713,47 $ | 38 772,24 $ |
| Bronze | 115 620,60 $ | 81 962,77 $ | 88 520,86 $ | 44 357,74 $ | 27 099,74 $ |
| Silver | 121 588,51 $ | 81 557,19 $ | 84 391,21 $ | 34 200,37 $ | 37 197,30 $ |

**Lecture business :** Platinum est le segment le plus surestimé en dollars par la jointure naïve (**46 026,30 $**). Silver a le ratio de gonflement le plus élevé : son revenu naïf vaut **1,4408×** son revenu pondéré. Le board ne doit donc jamais additionner les segments issus d'une jointure non pondérée.

## Preuve — réconciliation

Fichier : [`sql/checks/s08-weighted-reconciliation.sql`](../sql/checks/s08-weighted-reconciliation.sql)

| Contrôle | Référence | Comparé | Écart | Résultat |
|---|---:|---:|---:|---|
| Poids du pont client | 0 client en anomalie | 0 | 0,00 | PASS |
| Total ventes réel vs pondéré | 661 114,94 $ | 661 114,94 $ | 0,00 $ | PASS |
| Fan-out naïf observé | 661 114,94 $ | 885 282,55 $ | 224 167,61 $ | INFO |
| Poids campagne | 0 campagne en anomalie | 0 | 0,00 | PASS |
| Coût campagne alloué | 217 510,80 $ | 217 510,80 $ | 0,00 $ | INFO |

Les coûts campagne utilisent `raw_bridge_campaign_allocation.planned_spend`, qui est déjà un montant alloué par ligne campagne × segment dans le générateur S08. Le multiplier de nouveau par `budget_weight` sous-estimerait le coût.

## Signal SCD3

`dim_customer_scd3` contient **285 clients**, dont **121** ont un `previous_segment` non nul. Les transitions les plus fréquentes sont `Silver → Gold`, `Silver → Inactive` et `Silver → Platinum`, avec **8 clients** chacune. Cette vue est utile pour analyser les migrations récentes de segment, tandis que le pont pondéré reste la méthode correcte pour allouer le revenu.

## Recommandation au CEO

Pour les rapports board par segment, utiliser **l'attribution pondérée** : elle respecte le chevauchement des clients et conserve le total réel. L'attribution primaire peut rester utile pour nommer un propriétaire opérationnel, mais elle masque les appartenances secondaires. La jointure naïve doit être interdite dans les rapports exécutifs, car elle crée un revenu fictif de **224 167,61 $** sur ce seed.
