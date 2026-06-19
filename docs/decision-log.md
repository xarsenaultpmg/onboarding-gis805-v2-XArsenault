# Decision Log — entrepôt NexaMart

Ce journal capture les décisions de modélisation qui structurent l'entrepôt
NexaMart après S09. Chaque entrée explique le contexte business, l'option
retenue, les alternatives écartées et les conséquences pour les analyses.

## Décisions

### D01 — Fixer le grain de `fact_sales` à la ligne de commande

- **Date / séance :** 2026-05-14 (S02)
- **Contexte :** La première question CEO demandait des ventes par catégorie,
  région, client, canal et période. Un grain trop grossier aurait bloqué
  l'analyse par produit et catégorie.
- **Décision :** Une ligne de `fact_sales` représente une ligne de commande,
  identifiée par `sale_line_id` et `order_number`.
- **Alternatives écartées :**
  - Grain en-tête de commande : impossible d'attribuer correctement le revenu
    à plusieurs produits dans une même commande.
  - Grain paiement : inutilement fin pour les questions S02-S09, car aucun
    processus de paiement multiple n'est modélisé.
- **Conséquences :** Les rapports par commande doivent agréger les lignes ;
  `order_number` reste une dimension dégénérée dans le fait.
- **Révisable si :** NexaMart ajoute des paiements fractionnés, taxes ou frais
  de livraison qui exigent un processus de fait distinct.
- **Références :** `sql/facts/fact_sales.sql`, `docs/schema-v1.md`,
  `answers/S02_executive_brief.md`.

### D02 — Historiser les attributs client qui changent les rapports

- **Date / séance :** 2026-05-21 (S03)
- **Contexte :** Les segments, villes et provinces client peuvent changer.
  Écraser ces attributs réattribuerait des ventes passées au profil courant et
  ferait mentir les rapports historiques.
- **Décision :** `dim_customer` utilise le SCD Type 2 pour `segment`, `city` et
  `province`, et le Type 1 pour les corrections de nom.
- **Alternatives écartées :**
  - Type 1 partout : simple à maintenir, mais invalide les comparaisons
    historiques par segment.
  - Type 3 seulement : utile pour voir le segment précédent, mais insuffisant
    pour plusieurs changements dans le temps.
- **Conséquences :** Les faits résolvent `customer_key` selon la date de
  l'événement ; les analyses courantes doivent filtrer `is_current = TRUE` si
  elles ne veulent pas l'historique.
- **Révisable si :** Les rapports exigent une version hybride SCD6 ou une
  historisation plus fine des attributs marketing.
- **Références :** `sql/dims/dim_customer.sql`, `docs/scd-policy.md`,
  `docs/visuals/scd-type2-before-after.md`.

### D03 — Historiser la région magasin mais écraser le type de magasin

- **Date / séance :** 2026-05-21 (S03)
- **Contexte :** Les réassignations de région changent l'interprétation des
  ventes par territoire. Le type de magasin, lui, sert surtout à décrire la
  classification opérationnelle courante.
- **Décision :** `dim_store` utilise le SCD Type 2 pour la région et le Type 1
  pour `store_type`.
- **Alternatives écartées :**
  - Type 1 pour la région : aurait déplacé rétroactivement les ventes passées
    dans la nouvelle région.
  - Type 2 pour tous les attributs magasin : aurait créé des versions
    historiques peu utiles pour les corrections opérationnelles.
- **Conséquences :** Les faits utilisent `store_key` résolu selon la date de
  l'événement, ce qui préserve la vérité historique des rapports territoriaux.
- **Révisable si :** Le board demande un audit détaillé des changements de
  `store_type` dans le temps.
- **Références :** `sql/dims/dim_store.sql`, `docs/scd-policy.md`,
  `answers/S03_executive_brief.md`.

### D04 — Regrouper les drapeaux de commande dans `dim_order_profile`

- **Date / séance :** 2026-05-25 (S04)
- **Contexte :** Les commandes portent plusieurs drapeaux opérationnels :
  cadeau, express, promo, achat employé, ramassage, fragile et hors gabarit.
  Les garder comme colonnes dispersées rend les rapports difficiles à lire.
- **Décision :** Créer une junk dimension `dim_order_profile` avec une ligne par
  combinaison distincte de drapeaux et un `profile_name` business.
- **Alternatives écartées :**
  - Huit colonnes directement dans `fact_sales` : possible techniquement, mais
    peu lisible pour le VP Opérations.
  - Une dimension par drapeau : trop verbeux pour des attributs binaires qui
    changent ensemble.
- **Conséquences :** `fact_sales.profile_key` relie chaque vente à un profil de
  commande ; les analyses opérationnelles agrègent par `profile_name`.
- **Révisable si :** Les drapeaux deviennent des processus autonomes avec leurs
  propres mesures ou historiques.
- **Références :** `sql/dims/dim_order_profile.sql`, `docs/profiles.md`,
  `docs/board-briefs/s04-basket-flags.md`.

### D05 — Faire le drill-across par agrégats, jamais par jointure ligne à ligne

- **Date / séance :** 2026-06-04 (S07)
- **Contexte :** Le board voulait comparer ventes, retours, inventaire et
  budget. Ces faits n'ont pas le même grain, donc une jointure directe
  multiplierait les montants.
- **Décision :** Agréger chaque fait au grain commun de la question avant de
  joindre les résultats.
- **Alternatives écartées :**
  - Jointure directe entre `fact_sales` et `fact_returns` : crée un produit
    cartésien dès qu'il existe plusieurs lignes par produit et période.
  - Vue unique universelle : masque les règles de grain et encourage des
    additions invalides.
- **Conséquences :** Les rapports publient le grain commun explicitement, par
  exemple catégorie x mois ou catégorie x magasin x mois.
- **Révisable si :** Une couche sémantique impose automatiquement les grains et
  bloque les jointures invalides.
- **Références :** `docs/bus-matrix.md`,
  `sql/integration/s07-drill-across.sql`,
  `sql/integration/s07-actual-vs-budget.sql`.

### D06 — Utiliser un pont pondéré pour les segments client M:N

- **Date / séance :** 2026-06-08 (S08)
- **Contexte :** Un client peut appartenir à plusieurs segments. Attribuer 100 %
  du revenu à chaque segment gonfle les totaux et produit un revenu fictif.
- **Décision :** Modéliser `bridge_customer_segment` avec un `weight` dont la
  somme vaut 1.0 par client, relié à `dim_segment_outrigger`.
- **Alternatives écartées :**
  - Segment primaire seulement : réconciliable, mais perd les appartenances
    secondaires.
  - Jointure naïve sans poids : conserve les relations M:N, mais multiplie le
    revenu.
- **Conséquences :** Les rapports par segment doivent utiliser
  `SUM(revenue * weight)` pour conserver le total réel.
- **Révisable si :** Le métier fournit une règle d'attribution officielle
  différente de la pondération générée par le seed.
- **Références :** `sql/bridges/bridge_customer_segment.sql`,
  `sql/checks/s08-weighted-reconciliation.sql`,
  `docs/board-briefs/s08-overlap-risk.md`.

### D07 — Séparer les quatre types de faits S09 par comportement analytique

- **Date / séance :** 2026-06-14 (S09)
- **Contexte :** Les processus S09 ne se comportent pas tous comme des ventes.
  Certains sont des événements, d'autres des photos périodiques, des cycles de
  vie ou de simples présences.
- **Décision :** Créer quatre faits séparés : `fact_orders_transaction`,
  `fact_daily_inventory`, `fact_order_pipeline` et `fact_promo_exposure`.
- **Alternatives écartées :**
  - Table de faits unique : mélangerait mesures additives, semi-additives et
    absence de mesures.
  - Modéliser l'inventaire comme transaction : obligerait à reconstruire les
    niveaux de stock à partir d'événements non disponibles.
  - Ajouter des mesures artificielles à `fact_promo_exposure` : ferait croire
    qu'une exposition a une valeur monétaire directe.
- **Conséquences :** Chaque rapport doit respecter le type de fait : `SUM` pour
  les transactions, moyenne ou dernier snapshot pour le stock, jalons pour le
  pipeline, `COUNT(*)` ou anti-jointure pour le factless.
- **Révisable si :** Les sources opérationnelles ajoutent des événements
  détaillés de mouvement de stock, de paiement ou de conversion promo.
- **Références :** `docs/fact-type-decision-tree.md`,
  `sql/fact-types/s09-transaction.sql`,
  `sql/fact-types/s09-periodic-snapshot.sql`,
  `sql/fact-types/s09-accumulating.sql`,
  `sql/fact-types/s09-factless.sql`.

### D08 — Publier quatre KPI officiels testés pour le handoff S11

- **Date / séance :** 2026-06-18 (S11, après revue par les pairs S10)
- **Contexte :** La revue S10 (Charles Narbonne Merineau) a confirmé la clarté
  du modèle, mais le pack manquait de `metric-definitions.md` avec formules
  exécutables et valeurs observées. Sans cela, le CFO ne peut pas définir
  « revenu », « taux de retour » ou « couverture promo » sans ambiguïté.
- **Décision :** Documenter quatre KPIs couvrant `fact_sales`, `fact_returns`,
  `fact_order_pipeline` et `fact_promo_exposure`, chacun testé sur DuckDB local.
- **Alternatives écartées :**
  - KPIs uniquement depuis `fact_sales` : ne démontre pas la portée multi-faits.
  - Formules sans valeur observée : non livrables pour S11 selon le guide S10.
- **Conséquences :** Les briefs S11 et la défense S12 s'appuient sur
  `docs/metric-definitions.md` comme source canonique des définitions.
- **Révisable si :** Finance impose une définition différente de revenu net ou si
  de nouvelles sources ajoutent taxes, frais ou conversions promo.
- **Références :** `docs/metric-definitions.md`, `docs/board-briefs/Charles_peer-review-3.md`,
  `sql/integration/s07-drill-across.sql`, `sql/fact-types/s09-factless.sql`.

## Décisions en attente

- Décider si les dates de jalon de `fact_order_pipeline` doivent devenir des
  role-playing FK vers `dim_date` ou rester des colonnes de délai dans le fait.

## Décisions revisitées

- Aucune décision n'est supersédée au 2026-06-18. Les choix ci-dessus restent
  cohérents avec les briefs S02 à S09 et le handoff pack S11.

---

*Une décision est utile si un analyste peut comprendre pourquoi le modèle est
construit ainsi, quel risque elle évite, et quand il faudrait la réouvrir.*
