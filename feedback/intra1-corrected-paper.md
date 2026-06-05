# Copie corrigée — Examen intra 1 · GIS805-06

**Étudiant·e :** Xavier Arsenault
**Score MCQ :** 21.0 / 21  (100%)
**Score total :** 23.5 / 24.0 (98%)

> Les questions à choix multiples sont présentées ci-dessous avec ta réponse et la réponse correcte. ✓ = bonne réponse · ✗ = mauvaise réponse.

---

## Structure dimensionnelle

### ∅ q01-grain  _(annulée — point accordé à tous)_

**Question :**

Dans fact_sales chez NexaMart, le grain est « une ligne = une ligne de commande (sale_line_id) ». Que signifie cette décision ?

**Ta réponse :** Chaque ligne représente un article facturé dans une commande ; deux articles dans la même commande = deux lignes.

> _Cette question a été annulée après révision en classe. Le point est accordé à tous les étudiant·e·s._

### ✓ q02-mesure-vs-dim

**Question :**

Parmi les éléments suivants chez NexaMart, lequel est une **mesure** (et non une dimension) ?

**Tes choix :**

  La catégorie du produit
  La province du magasin
→ **Le montant total de la ligne (line_total)** ✓
  Le trimestre fiscal

### ✓ q03-additivite

**Question :**

Laquelle de ces mesures n'est **PAS** additive (on ne peut pas la SUMmer directement à travers toutes les dimensions) ?

**Tes choix :**

  revenue (chiffre d'affaires)
  quantity (quantité vendue)
→ **unit_price (prix unitaire)** ✓
  discount_amount (montant de la remise)

### ✓ q04-star-vs-snowflake

**Question :**

Pourquoi un **schéma en étoile** (dimensions dénormalisées) est-il généralement préféré à un **schéma en flocon** (dimensions normalisées) dans un entrepôt analytique ?

**Tes choix :**

  Il occupe moins d'espace disque parce qu'il évite la duplication des attributs.
→ **Il réduit le nombre de jointures nécessaires pour répondre à une requête analytique, ce qui simplifie le SQL et améliore les performances.** ✓
  Il garantit la 3e forme normale, ce qui empêche les anomalies de mise à jour.
  Il est imposé par la majorité des moteurs OLAP qui n'acceptent pas les dimensions normalisées.

### q05-grain-open  _(question ouverte)_

**Question :**

La VP demande : « Je veux comparer mes ventes par client par mois. » Un collègue propose un grain « une ligne = un client par mois ». Expliquez pourquoi cette décision est **irréversible** et quelles questions futures elle rend impossibles à répondre. Donnez 2 exemples concrets de questions perdues. (4-6 phrases)

**Ta réponse :**

Lorsqu'on définit le grain d'une table de table, il s'agit d'un contrat c'est-à-dire que chaque ligne de la table vont représenter un client par mois. Il faut que le grain soit constant afin que les requêtes analytiques d'agrégation fassent du sens. En optant pour un grain = un client par mois, il devient alors impossible d'affiner les requêtes analytiques à un grain plus fin. La bonne pratique lors du choix de modélisation est donc de prendre le grain le plus fin possible puisqu'il est toujours possible d'agréger les résultats, mais l'inverse n'est pas possible.     Ex_1  : on cherche à savoir quel jours du mois ou les revenus sont les plus élevés pour l'entreprise.     Ex_2  : Quel semaine dans l'année est la plus rentable, existe-t-il une saisonnalité hebdomadaire ?     En effet, c'est question ne peuvent être répondu par la modélisation proposée puisque le grain capturé serait une ventes pour un client par mois alors que dans mes deux exemple le grain temporel est plus fin.

## Slowly Changing Dimensions

### ✓ q06-scd-type1

**Question :**

Le magasin de Gatineau change de région : Outaouais → Québec (fusion administrative, mars 2026). Si on applique un **SCD Type 1** à dim_store, que se passe-t-il pour les rapports rétrospectifs ?

**Tes choix :**

  L'historique est préservé : les ventes de janvier–février restent attribuées à « Outaouais ».
→ **Les ventes de janvier–février sont rétroactivement attribuées à « Québec » — l'historique est faussé.** ✓
  Les ventes de janvier–février disparaissent jusqu'à reclassement manuel.
  DuckDB rejette la mise à jour par défaut pour protéger l'historique.

### ✓ q07-scd-type2

**Question :**

Pour un SCD Type 2 sur dim_store, quelle combinaison de colonnes ajoutées est **nécessaire** ?

**Tes choix :**

→ **effective_from, effective_to, is_current (et une nouvelle surrogate key par version)** ✓
  previous_value et current_value uniquement
  version_number incrémental, sans dates
  Une colonne booléenne is_deleted suffit

### ✓ q08-scd-type3

**Question :**

Quelle est la limite principale d'un SCD Type 3 ?

**Tes choix :**

  Il consomme trop d'espace disque.
→ **Il ne conserve qu'un seul niveau de changement (current_value + previous_value), pas tout l'historique.** ✓
  Il est incompatible avec DuckDB.
  Il oblige à supprimer les anciennes lignes de fait.

### ✓ q09-scd-choice

**Question :**

Un attribut customer_email contient une faute de frappe corrigée par le service client (« jean@nexamrt » → « jean@nexamart »). Quel type de SCD est le plus approprié et pourquoi ?

**Tes choix :**

→ **Type 1 : la correction d'une erreur ne mérite pas de version historique.** ✓
  Type 2 : tout changement, même mineur, doit être tracé pour audit.
  Type 3 : on garde l'ancien email comme previous_value en cas de litige.
  Aucun SCD : il faut supprimer la ligne et tout recharger.

### q10-scd-open  _(question ouverte)_

**Question :**

NexaMart envisage de reclasser ses clients « Gold » en « Platinum » quand leur dépense annuelle dépasse 10 000 $. La VP Marketing veut pouvoir analyser : « Combien de revenu ai-je généré pendant que ce client était Gold vs Platinum ? » Quel SCD recommandez-vous et quelles colonnes ajoutez-vous à dim_customer ? (3-5 phrases)

**Ta réponse :**

Je pense qu'un SCD de type 2 est à privilégier ici pour la raison suivante : l'historique possède une vrai valeur analytique. De plus, on veut savoir spécifiquement lorsque ce client passe de gold à platinum.     Or, rien n'indique que ce changement se produira seulement une fois, il est donc plus logique de choisir un SCD de type 2 qu'un SCD de type 3 puisque ce changement de segment risque d'arriver plusieurs fois dans le parcours d'un client avec l'entreprise.     Ainsi avec un SCD de type 2 et des colonnes du type valid_from et valid_to et les SK associés on peut faire une étude longitudinale d'un client et voir si se client passe de gold à Platinium et si jamais il redevient gold dans le futur.

## Jointures et clés

### ✓ q11-surrogate

**Question :**

Pourquoi joindre fact_sales à dim_store sur la **surrogate key** (store_key) plutôt que sur la clé naturelle (store_natural_id) ?

**Tes choix :**

  Uniquement parce que les entiers prennent moins d'espace disque que les chaînes — indépendamment de tout besoin historique.
→ **Parce qu'avec un SCD Type 2, la clé naturelle apparaît plusieurs fois ; seule la surrogate key identifie la BONNE version de la dimension pour chaque vente.** ✓
  Parce que DuckDB n'accepte pas les jointures sur des chaînes de caractères.
  Parce que les clés naturelles changent à chaque batch ETL.

### ✓ q12-temporal-join

**Question :**

Dans un schéma SCD Type 2, fact_sales contient store_natural_id (l'identifiant source du système OLTP) et order_date — pas de surrogate key pré-résolue. On veut récupérer les attributs du magasin tels qu'ils étaient au moment de la vente. Quelle clause de jointure est correcte ?

**Tes choix :**

  JOIN dim_store ON fact.store_natural_id = dim.store_natural_id
→ **JOIN dim_store ON fact.store_natural_id = dim.store_natural_id AND fact.order_date BETWEEN dim.effective_from AND dim.effective_to** ✓
  JOIN dim_store ON dim.is_current = TRUE
  JOIN dim_store ON fact.store_natural_id = dim.store_natural_id AND dim.is_current = TRUE

### ✓ q13-fk-direction

**Question :**

Dans un schéma en étoile, où vivent les clés étrangères (FK) ?

**Tes choix :**

  Dans les dimensions, pointant vers la table de faits.
→ **Dans la table de faits, pointant vers chaque dimension.** ✓
  Dans une table d'association séparée (bridge table) pour chaque paire fact-dim.
  Il n'y a pas de FK dans un schéma en étoile : les jointures se font sur les noms de colonnes.

### ✓ q14-natural-vs-surrogate

**Question :**

À quoi sert encore la **clé naturelle** (natural_id) si on joint sur la surrogate key ?

**Tes choix :**

  À rien — elle peut être supprimée après chargement.
→ **À retracer l'entité d'origine dans le système OLTP source (audit, debug, rapprochement).** ✓
  Elle est la clé primaire de la table de faits.
  Elle remplace la surrogate key pour les requêtes ad hoc des analystes.

### ✓ q14b-join-iscurrent

**Question :**

Pour produire un rapport « tableau de bord du jour » qui montre uniquement l'**état actuel** de chaque magasin (peu importe l'historique), quelle condition de jointure ajouter à dim_store SCD Type 2 ?

**Tes choix :**

  AND fact.order_date BETWEEN dim.effective_from AND dim.effective_to
→ **AND dim.is_current = TRUE** ✓
  Il n'y a pas besoin de condition supplémentaire : la surrogate key identifie déjà une version unique.
  Toutes les options ci-dessus sont équivalentes.

## Junk et dimensions dégénérées

### ✓ q15-degenerate

**Question :**

order_number chez NexaMart est utilisé pour regrouper les lignes d'une même commande, mais n'a aucun attribut propre (pas de date, pas de statut, pas de canal). Comment le modéliser ?

**Tes choix :**

  Créer une table dim_order avec uniquement la colonne order_number.
→ **Le laisser comme colonne dans fact_sales sans dimension dédiée : c'est une dimension dégénérée.** ✓
  Le stocker dans dim_customer comme attribut complémentaire.
  Le supprimer après chargement : il fait double emploi avec order_date.

### ✓ q16-junk-purpose

**Question :**

Pourquoi créer une **junk dimension** plutôt que de laisser les 8 flags booléens (is_gift_wrapped, is_express, is_loyalty, …) directement dans fact_sales ?

**Tes choix :**

  Pour économiser de l'espace disque (les booléens dans une dimension prennent moins de place).
→ **Pour nettoyer la table de faits, regrouper les combinaisons réellement observées en profils nommés, et faciliter l'analyse (« Loyalty+Promo » vs combinaison de flags).** ✓
  Parce que DuckDB n'accepte pas plus de 5 colonnes booléennes par table.
  Pour pouvoir y appliquer un SCD Type 2 plus tard.

### ✓ q17-junk-cardinality

**Question :**

Avec 8 flags booléens, le nombre **théorique** de combinaisons est 2^8 = 256. Pourquoi la junk dimension de NexaMart n'en contient-elle en pratique qu'une quarantaine ?

**Tes choix :**

  Parce qu'on a filtré aléatoirement pour réduire la taille.
→ **Parce qu'on ne stocke que les combinaisons réellement observées dans les données : la cardinalité réelle est très inférieure au théorique.** ✓
  Parce que la junk dimension est limitée à 50 lignes par convention.
  Parce qu'on a fusionné les profils similaires manuellement.

### ✓ q17b-junk-correlation

**Question :**

On observe que le profil « Loyalty+Promo » apparaît 87 fois alors que, sous hypothèse d'indépendance, on en attendrait ~42. Quelle interprétation est correcte pour la VP ?

**Tes choix :**

  C'est une anomalie statistique sans signification business.
→ **Les clients Loyalty utilisent activement les promotions : les deux incitatifs se cumulent chez les mêmes acheteurs.** ✓
  Les promotions sont moins efficaces auprès des clients Loyalty.
  Le système enregistre deux fois certaines commandes.

## Lecture SQL

### ✓ q18-sql-groupby

**Question :**

Que retourne cette requête ?

    SELECT p.category, SUM(f.line_total) AS revenue
    FROM fact_sales f
    JOIN dim_product p ON f.product_key = p.product_key
    GROUP BY p.category
    ORDER BY revenue DESC;

**Tes choix :**

  Le revenu total par produit (un revenu par produit individuel).
→ **Le revenu total agrégé par catégorie de produit, trié du plus élevé au plus faible.** ✓
  Le nombre de commandes par catégorie.
  Le revenu moyen par catégorie.

### ✓ q19-sql-temporal

**Question :**

Que produit cette requête sur dim_store en SCD Type 2 ?
(Dans ce schéma, la ligne courante a effective_to = '9999-12-31'.)

    SELECT f.order_date, s.region, SUM(f.line_total)
    FROM fact_sales f
    JOIN dim_store s
      ON f.store_key = s.store_key
     AND f.order_date BETWEEN s.effective_from AND s.effective_to
    GROUP BY f.order_date, s.region;

**Tes choix :**

→ **Le revenu par jour et par région **selon la région en vigueur au moment de la vente** (Outaouais avant mars, Québec après).** ✓
  Le revenu par jour et par région **actuelle** (toutes les ventes attribuées à Québec).
  Le revenu par jour, dupliqué pour chaque version historique du magasin.
  Une erreur : on ne peut pas joindre fact et dim sur deux conditions à la fois.

### ✓ q20-sql-basket

**Question :**

Que cherche cette requête ?

    SELECT f1.product_key AS p1, f2.product_key AS p2, COUNT(*) AS pairs
    FROM fact_sales f1
    JOIN fact_sales f2
      ON f1.order_number = f2.order_number
     AND f1.product_key < f2.product_key
    GROUP BY f1.product_key, f2.product_key
    ORDER BY pairs DESC;

**Tes choix :**

  Le nombre de fois où chaque produit a été vendu seul.
→ **Le nombre de paires distinctes de produits achetés ensemble dans la même commande (analyse de panier).** ✓
  Le nombre de commandes par client.
  Le produit le plus vendu, par catégorie.

### ✓ q21-sql-broken

**Question :**

Cette requête est censée donner le revenu par région SCD Type 2,
mais le résultat est faux. Qu'est-ce qui cloche ?

    SELECT s.region, SUM(f.line_total)
    FROM fact_sales f
    JOIN dim_store s ON f.store_natural_id = s.store_natural_id
    GROUP BY s.region;

**Tes choix :**

  Il manque ORDER BY.
→ **Elle joint sur la clé naturelle : chaque vente est doublée pour chaque version historique du magasin, surestimant le revenu.** ✓
  Elle utilise SUM au lieu de COUNT.
  GROUP BY devrait inclure store_natural_id.

### ✓ q22-sql-junk

**Question :**

Que retourne cette requête ?

    SELECT j.profile_label, COUNT(DISTINCT f.order_number) AS n_orders, SUM(f.line_total) AS revenue
    FROM fact_sales f
    JOIN dim_order_junk j ON f.order_junk_key = j.order_junk_key
    GROUP BY j.profile_label
    ORDER BY revenue DESC;

**Tes choix :**

  Le revenu total par produit.
→ **Le revenu et le nombre de commandes par profil opérationnel (Standard, Loyalty+Promo, Express bulk, …), triés par revenu décroissant.** ✓
  Le revenu par client par mois.
  Le profil le plus rare, avec son revenu.

## Synthèse

### q23-sql-open  _(question ouverte)_

**Question :**

La VP demande : « Quel pourcentage de mon revenu vient des commandes qui combinent à la fois Loyalty ET Promo, par trimestre fiscal ? » Décrivez **en français** la logique de la requête SQL qui répond à cette question (sans l'écrire) : quelles tables, quelles jointures, quel filtre, quelle agrégation. (4-6 phrases)

**Ta réponse :**

On part de fact_sales comme table centrale dans le FROM. On la joint à dim_order_profile (la junk dimension) via profile_key, et à dim_date via date_key pour accéder au trimestre fiscal.     Dans le WHERE, on filtre les profils où is_loyalty = TRUE AND is_promo = TRUE. Ce filtre est possible en une seule condition grâce à la junk dimension, sans toucher au fait directement.     Dans le SELECT, on regroupe par trimestre et on calcule le ratio SUM(revenue des lignes filtrées) / SUM(revenue total) — ce qui nécessite soit une sous-requête, soit une un window fonction pour avoir le total global au dénominateur.     Le résultat donne, par trimestre fiscal, la part du revenu attribuable aux commandes combinant fidélité et promotion.

---

_Copie générée le 2026-06-04 · GIS805-06 · Université de Sherbrooke_