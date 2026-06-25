# Copie corrigée — Examen final · GIS805

**Étudiant·e :** Xavier Arsenault
**Score QCM :** 28.0 / 29  (97%)
**Score total :** 34.0 / 35.0 (97%)

> Les questions à choix multiples sont présentées ci-dessous avec ta réponse et la réponse correcte. ✓ = bonne réponse · ✗ = mauvaise réponse.

---

## Architecture décisionnelle

### ✓ q01-oltp-vs-olap

**Question :**

Le directeur des ventes NexaMart lance une requête sur le système de caisse (OLTP) pour obtenir les ventes mensuelles par catégorie et région. La requête prend 47 secondes et ralentit les caisses en production. Quelle est la raison fondamentale de ce problème ?

**Tes choix :**

  Le système OLTP n'a pas assez de RAM pour traiter les agrégations multi-catégories demandées.
  Les ventes mensuelles ne sont pas stockées dans le système de caisse, il manque une table.
→ **Un OLTP est optimisé pour des transactions unitaires, pas pour agréger des millions de lignes.** ✓
  Ajouter un index composé sur category et region suffirait à résoudre la lenteur observée.

### ✓ q02-olap-caracteristique

**Question :**

Parmi les caractéristiques suivantes, laquelle décrit un système OLAP (analytique/entrepôt) et NON un système OLTP ?

**Tes choix :**

→ **Données historisées et dénormalisées dans un modèle en étoile.** ✓
  Optimisé pour des écritures courtes et nombreuses en temps réel.
  Une ligne représente une transaction opérationnelle unitaire.
  La disponibilité temps-réel est critique pour l'opération.

### ✓ q03-processus-metier

**Question :**

NexaMart+ (programme d'abonnement) génère les événements suivants : inscription, paiement mensuel, annulation, et exposition à une promotion. Si l'inscription et l'annulation sont modélisées comme deux étapes du lifecycle d'abonnement, combien de processus métier distincts cela représente-t-il pour la modélisation dimensionnelle ?

**Tes choix :**

  1 — tout entre dans une seule table de faits abonnements.
  2 — un processus transactionnel (paiements) et un promotionnel.
  4 — chaque événement est un processus métier distinct.
→ **3 — lifecycle, paiement mensuel et promotion sont trois processus.** ✓

### ✓ q04-mesure-vs-descripteur

**Question :**

Classez l'élément suivant : « revenu mensuel récurrent (MRR) du programme NexaMart+ ». C'est :

**Tes choix :**

  Un descripteur (dimension) décrivant un attribut du client.
→ **Une mesure/KPI numérique dont l'additivité dépend du grain.** ✓
  Une clé subrogée identifiant une version de dimension.
  Un grain définissant le niveau de détail d'une table de faits.

### ✓ q05-entrepot-vs-adhoc

**Question :**

Un collègue suggère : « Pas besoin d'entrepôt — on peut joindre les tables OLTP directement pour les rapports. » Quel est l'argument le plus fort CONTRE cette approche ?

**Tes choix :**

  Créer des vues matérialisées dans l'OLTP résout les problèmes de performance.
  Les tables OLTP ne contiennent pas les colonnes nécessaires aux rapports.
  Créer une réplique en lecture réduit l'impact, donc remplace un entrepôt.
→ **Les requêtes analytiques dégradent l'OLTP et les changements de schéma cassent les rapports.** ✓

### ✓ q06-hypothese-limite

**Question :**

Trois systèmes opérationnels NexaMart (caisse, facturation d'abonnement, CRM) ne se parlent pas. Quelle hypothèse est INDISPENSABLE pour intégrer les analyses client entre les trois systèmes dans l'entrepôt ?

**Tes choix :**

  Chaque système est hébergé dans le même cloud ou la même région.
  Les trois systèmes utilisent le même format de date et d'encodage.
→ **Un mécanisme fiable de rapprochement des clients existe ou peut être construit.** ✓
  Les trois systèmes partagent le même identifiant courriel comme clé.

## Cœur analytique

### ✓ q07-grain

**Question :**

Pour fact_subscription_event (abonnements NexaMart+), on hésite entre deux grains : (A) une ligne = un événement d'abonnement individuel, ou (B) une ligne = un abonné par mois (agrégé). Quel est le meilleur choix et pourquoi ?

**Tes choix :**

→ **A — le grain fin préserve le détail ; on agrège A vers B mais pas l'inverse.** ✓
  B — moins de lignes, donc meilleures performances de requête.
  B — le grain mensuel suffit, car les rapports actuels sont mensuels.
  A et B sont équivalents : on peut passer de l'un à l'autre sans perte.

### ✓ q08-scd-type2-lignes

**Question :**

Un abonné NexaMart+ passe du forfait « Basic » au forfait « Premium » en mars 2026 (en supposant qu'il n'avait qu'une seule ligne Basic avant cette date). En SCD Type 2 sur dim_subscriber, combien de lignes cet abonné a-t-il dans la dimension après le changement ?

**Tes choix :**

  1 — on écrase l'ancien forfait par une mise à jour Type 1.
  3 — une ligne par mois depuis la date d'inscription initiale.
→ **2 — une ligne Basic (is_current=FALSE) et une Premium (is_current=TRUE).** ✓
  2 — mais les deux lignes conservent is_current=TRUE.

### ✗ q09-scd-jointure

**Question :**

Un client passe de Silver à Gold le 2026-03-01. Le CEO veut attribuer chaque vente au plan EN VIGUEUR AU MOMENT DE LA VENTE. fact_sales contient uniquement customer_id (identifiant naturel) et order_date, pas de customer_key. dim_customer utilise un intervalle [effective_from, effective_to) où effective_to vaut 9999-12-31 pour la ligne courante. Quelle condition de jointure (pseudo-SQL) est correcte entre fact_sales (f) et dim_customer (c) en SCD Type 2 ?

**Tes choix :**

  JOIN dim_customer c ON c.customer_key = f.customer_key WHERE c.is_current = TRUE
  JOIN dim_customer c ON c.customer_id = f.customer_id WHERE c.is_current = TRUE AND c.effective_from IS NOT NULL
→ **JOIN dim_customer c ON c.customer_id = f.customer_id AND f.order_date BETWEEN c.effective_from AND c.effective_to** ✗
  JOIN dim_customer c ON c.customer_id = f.customer_id AND f.order_date >= c.effective_from AND f.order_date < c.effective_to

**Bonne réponse :** JOIN dim_customer c ON c.customer_id = f.customer_id AND f.order_date >= c.effective_from AND f.order_date < c.effective_to

### ✓ q10-additivite

**Question :**

Classez la mesure « taux_de_marge (revenu - coût) / revenu » stockée dans fact_sales :

**Tes choix :**

  Additive — on peut faire SUM sur toutes les dimensions sans restriction.
  Semi-additive — sommable par produit ou région, mais pas sur l'axe temps.
→ **Non-additive — c'est un ratio qu'il faut recalculer après agrégation.** ✓
  Ce n'est pas une mesure — c'est un attribut descriptif de dimension.

### ✓ q11-junk

**Question :**

La table fact_subscription_event contient déjà 20+ colonnes de mesure. Elle porte aussi 4 attributs à faible cardinalité non mesurables (is_trial, is_auto_renew, is_gifted, is_winback). Selon Kimball, quelle est la meilleure approche de modélisation ?

**Tes choix :**

→ **Créer une junk dimension regroupant les combinaisons en profils (max 16 lignes).** ✓
  Garder les 4 drapeaux comme colonnes directement dans la table de faits.
  Créer 4 tables de dimensions séparées, une par indicateur booléen.
  Stocker les drapeaux dans dim_date comme attributs temporels du jour.

### ✓ q12-drill-across

**Question :**

Pour répondre à « les abonnés dépensent-ils plus ? », on combine fact_sales et fact_subscription_event. Pourquoi éviter un JOIN direct entre ces deux tables de faits ?

**Tes choix :**

  Joindre sur subscriber_key puis dédupliquer les lignes en double après coup avec DISTINCT.
→ **Les grains diffèrent : le JOIN multiplie les lignes ; agréger au grain commun d'abord.** ✓
  Les deux tables de faits n'ont aucune colonne de jointure commune exploitable.
  Un UNION ALL des deux faits avec un flag source est plus performant qu'un JOIN.

## Fiabilité et gouvernance

### ✓ q13-null-semantique

**Question :**

Dans fact_subscription_event, cancel_date est un attribut de date servant au calcul de délai (pas une FK vers dim_date). Il est NULL pour les abonnements toujours actifs. Faut-il remplacer ce NULL par une valeur sentinelle (ex. 9999-12-31) ?

**Tes choix :**

  Oui — un NULL dans une colonne de date casse les requêtes GROUP BY.
→ **Non — ce NULL porte un sens analytique (« pas encore annulé »).** ✓
  Oui — toute colonne de date dans un fait doit avoir une valeur.
  Non — mais il faut ajouter une ligne « Not Yet » dans dim_date.

### ✓ q14-membre-inconnu

**Question :**

Une FK de fait ne doit jamais être NULL (FK_NOT_NULL). Quelle technique respecte cette règle SANS perdre de lignes quand la dimension est inconnue ?

**Tes choix :**

→ **Un membre inconnu (*_key = -1) dans la dimension absorbe les FK manquantes.** ✓
  Supprimer les lignes de faits dont la FK est manquante ou inconnue.
  Remplacer la FK par 0 et ignorer la dimension dans les requêtes.
  Garder la FK NULL et mettre la mesure associée à NULL aussi.

### ✓ q15-reconciliation

**Question :**

Après avoir construit un pont pondéré subscriber-segment pour NexaMart+, quel contrôle de réconciliation est INDISPENSABLE ?

**Tes choix :**

  Vérifier que le nombre de lignes du pont égale exactement le nombre d'abonnés actifs.
  Vérifier que chaque abonné possède au moins un segment attribué dans le pont.
  Vérifier que chaque segment du pont contient au moins un abonné actif associé.
→ **Vérifier SUM(weight)=1.0 par abonné ET revenu total avec pont = sans pont.** ✓

### ✓ q16-quality-checks

**Question :**

Le « make check » de NexaMart vérifie TABLE_EXISTS, ROW_COUNT, PK_UNIQUE, FK_NOT_NULL et RECONCILE. Quels contrôles détecteraient ENSEMBLE qu'une jointure a multiplié les lignes et gonflé les totaux, même si les doublons ne violent pas une clé primaire déclarée ?

**Tes choix :**

  TABLE_EXISTS + FK_NOT_NULL — la table existe et les FK sont non NULL.
  PK_UNIQUE + FK_NOT_NULL — clés uniques et FK non NULL.
→ **ROW_COUNT + RECONCILE — lignes au-delà de l'attendu et totaux non réconciliés.** ✓
  PK_UNIQUE + ROW_COUNT — clés uniques et nombre de lignes attendu.

### ✓ q17-model-card

**Question :**

Quels éléments sont les PLUS importants d'une model card pour un entrepôt dimensionnel ?

**Tes choix :**

  DDL complet, lineage des transformations, inventaire des dashboards et SLA.
  Data dictionary, scripts SQL, nom du propriétaire et historique des changes.
  Liste des outils BI connectés, calendrier de maintenance et contacts support.
→ **Grain, politiques SCD, fréquence de rafraîchissement, limites et propriétaire.** ✓

### ✓ q18-handoff-pack

**Question :**

Selon la méthode GIS805, le handoff pack permet à un collègue de reprendre le modèle si le lead analyste quitte NexaMart. Quels sont les 4 documents minimaux ?

**Tes choix :**

→ **Model card, bus matrix, decision log, data dictionary.** ✓
  README, CHANGELOG, LICENSE, CONTRIBUTING (format open-source).
  ERD, DDL complet, ETL script, test plan (format dev-ops).
  Slides, rapport mensuel, budget, backlog (format gestion de projet).

## Outil de pilotage (KPIs)

### ✓ q19-fact-type-pipeline

**Question :**

NexaMart+ suit le « pipeline d'abonnement » pour un cycle donné : inscription, premier paiement, activation, annulation ou renouvellement. Chaque étape a un timestamp. Quel type de table de faits est le plus approprié ?

**Tes choix :**

  Transaction — une ligne par événement individuel du pipeline.
  Periodic snapshot — une photo mensuelle de l'état des abonnements.
→ **Accumulating snapshot — une ligne par abonnement, mise à jour par étape.** ✓
  Factless fact — l'existence de l'abonnement est le seul fait enregistré.

### ✓ q20-kpi-churn

**Question :**

Le taux d'attrition (churn rate) mensuel se calcule comme : annulations du mois / abonnés actifs en début de mois. Ce KPI est basé sur :

**Tes choix :**

→ **Periodic snapshot des actifs (dénominateur) et annulations du mois (numérateur).** ✓
  fact_sales (dénominateur : revenu total) et dim_subscriber (numérateur : inactifs).
  dim_subscriber (dénominateur : tous les clients) et fact_sales (numérateur : retours).
  Pont pondéré subscriber-segment (dénominateur) et dim_date (numérateur : mois).

### ✓ q21-variance-numerique

**Question :**

Au T4, le segment Gold affiche un revenu brut de 1 200 k$ et un budget cible de 1 000 k$. 15% du revenu brut est retourné. Quelle est la variance vs budget APRÈS retours ?

**Tes choix :**

  +20% — variance brute, sans tenir compte des retours.
→ **+2% — revenu net 1 020 k$ vs budget 1 000 k$.** ✓
  -15% — on soustrait directement le taux de retour.
  +5% — moyenne entre +20% et -15%.

### ✓ q22-piege-semi-additif

**Question :**

Le tableau de bord affiche abonnés_actifs par mois. Un analyste fait SUM(abonnés_actifs) sur 12 mois et obtient un total annuel. Quel est le problème ?

**Tes choix :**

  Aucun problème — SUM est valide sur toutes les dimensions ; pas de correction.
  Données manquantes certains mois ; combler les trous par interpolation linéaire.
  Il faut joindre à dim_date et grouper par trimestre avant de sommer les mois.
→ **Semi-additif : SUM recompte les mêmes abonnés ; utiliser AVG ou fin de période.** ✓

### ✓ q23-factless

**Question :**

NexaMart+ envoie des offres promotionnelles aux abonnés. La table fact_promo_exposure enregistre quels abonnés ont été exposés à quelle promotion, sans mesure numérique. Comment répondre à « quels abonnés éligibles n'ont PAS été exposés à la promo Black Friday » ?

**Tes choix :**

  SELECT * FROM fact_promo_exposure WHERE exposed = FALSE (filtrer la table directement).
  Compter les NULLs dans la colonne promo_id de fact_promo_exposure pour cette promo.
→ **Anti-jointure : éligibles (dim_subscriber) MINUS exposés dans fact_promo_exposure.** ✓
  Impossible — une factless fact ne permet pas de répondre à ce type de question.

### ✓ q24-variance-budget

**Question :**

Un analyste joint fact_subscription_payments au grain transactionnel avec fact_budget au grain région × mois, puis calcule SUM(f.amount) - SUM(b.target) par région et mois. Les variances sont gonflées. Quel est le problème ?

**Tes choix :**

  Il manque un filtre WHERE sur l'année courante pour limiter les lignes jointes.
→ **Le budget est dupliqué par ligne de paiement ; agréger au grain région × mois d'abord.** ✓
  Les colonnes region_key et month_key ne sont pas indexées, d'où un scan complet.
  Il faut utiliser un LEFT JOIN au lieu d'un INNER JOIN pour conserver les budgets.

## Justification

### ✓ q25-etl-vs-elt

**Question :**

Le CTO demande : « ETL ou ELT ? ». Quelle affirmation est correcte ?

**Tes choix :**

  ETL et ELT sont la même chose, la différence est purement marketing.
  ELT élimine le besoin de transformations amont ; les données brutes suffisent.
→ **ETL transforme avant chargement ; ELT charge puis transforme dans la cible.** ✓
  ETL est obligatoire pour construire un modèle en étoile ; ELT ne le permet pas.

### ✓ q26-gis806-boundary

**Question :**

GIS805 = structurer la vérité décisionnelle. GIS806 = ?

**Tes choix :**

→ **Créer, peupler, optimiser et opérer l'infrastructure (ETL/ELT, OLAP, cloud).** ✓
  La même chose que GIS805 mais avec des volumes de données plus grands.
  Marketing analytics et science des données appliquée au commerce.
  Concevoir uniquement les dimensions conformes et la bus matrix.

### ✓ q27-pont-revenu

**Question :**

Un abonné NexaMart+ génère 100 $ de revenu et appartient à 3 segments avec poids normalisés [0.3, 0.2, 0.5]. Quel revenu est attribué au segment dont le poids est 0.2 ?

**Tes choix :**

  100 $ — le revenu total est attribué intégralement à chaque segment.
  33.33 $ — répartition égale entre les 3 segments de l'abonné.
  50 $ — on applique par erreur le poids 0.5 d'un autre segment.
→ **20 $ — revenu × poids = 100 × 0.2 = 20 $.** ✓

### ✓ q28-reconciliation-manquantes

**Question :**

fact_sales contient 2 950 lignes, mais la source en a 2 973. Après inspection, les 23 lignes source ont des customer_id absents de dim_customer. Les lignes manquantes sont dues à :

**Tes choix :**

  Un problème de RAM lors du chargement des données source.
→ **Un INNER JOIN a éliminé les lignes dont le customer_id est absent.** ✓
  Un filtre WHERE sur la date a exclu les anciennes lignes source.
  Un doublon de clé primaire a fusionné 23 paires de lignes.

### ✓ q29-matching-4types

**Question :**

Classez chaque table dans le bon type de fait : (1) fact_sales_detail (une ligne par ligne de vente), (2) fact_inventory_monthly (stock en fin de mois), (3) fact_claim_lifecycle (une ligne par réclamation avec une colonne date par étape : open > assign > investigate > close), (4) fact_student_course_registration (sans mesure numérique).

**Tes choix :**

→ **(1) Transaction, (2) Periodic snapshot, (3) Accumulating snapshot, (4) Factless.** ✓
  (1) Periodic snapshot, (2) Transaction, (3) Factless, (4) Accumulating snapshot.
  (1) Accumulating snapshot, (2) Factless, (3) Transaction, (4) Periodic snapshot.
  (1) Transaction, (2) Accumulating snapshot, (3) Periodic snapshot, (4) Factless.

### q30-defense-grain  _(question ouverte)_  — 2.0 / 2

**Question :**

Vous avez choisi le grain de fact_sales à la LIGNE DE COMMANDE plutôt qu'à la COMMANDE. Défendez : nommez UNE question impossible au grain plus grossier et UN coût du grain plus fin. (3-6 phrases)

**Ta réponse :**

Le fait d'avoir un grain plus fin dans la table fact_sales permet de faire des analyses qu'un grain plus grossier ne permet de pas de faire.     À titre d'exemple, avec le grain ; une ligne = une commande, il est impossible de faire une analyse au niveau du produit. On pourrait penser à faire une analyse du panier d'achat et voir le uplift lorsque deux produits sont achetés en paire.     Ce type d'analyse n'est possible que lorsque le grain en question est plus fin soi à un ligne = un article de la commande.     De plus, avoir un grain plus fin n'empêche pas l'analyse au niveau de la commande, ça prend seulement une degenerated dimension pour faire l'aggrégation. En effet, il est toujours possible de passer d'un grain plus fin à une aggrégation, mais l'inverse n'est pas possible.     En contre partie, avoir un grain plus fin demande plus de stockage sur l'entrepôt de données.

**Commentaire :**

Tu as bien identifié une question impossible au grain plus grossier, en mentionnant l'analyse au niveau du produit. De plus, tu as clairement expliqué le coût du grain plus fin en termes de stockage, ce qui est concret et pertinent. Ton argumentation est solide et bien structurée.

### q31-defense-scd  _(question ouverte)_  — 2.0 / 2

**Question :**

Vous avez historisé le segment de fidélité en SCD Type 2 plutôt que Type 1. Quelle distorsion le Type 1 introduit-il dans un rapport trimestriel par segment, éventuellement ventilé par région ? Expliquez le mécanisme. (3-6 phrases)

**Ta réponse :**

Le fait de choisir un SCD de type 2 ici à beaucoup plus de sens d'un point de vue analytique.     En effet, avec un SCD de type 2 on conserve l'historique et évite le biais qu'un SCD de type 1 aurait introduit dans notre analyse. Si on avait décidé dans notre politique SCD d'opter pour le type 1 pour le changement de segment les revenus engendré par le segment aurait été attribué au nouveau segment alors que ce n'est pas fidèle à la réalité opérationnel. En effet, ceci aurait donc attribué les ventes d'un segment à la mauvaise région.     C'est pourquoi l'approche d'un SCD type 2 avec les SK, effective_from, effective_to and is_current fait beacoup plus de sens pour avoir un portrait juste des ventes par segment par régions même si un SCD de type 2 complexifie le modèle de données.

**Commentaire :**

Tu as bien identifié que le SCD de type 1 réattribue les ventes au segment actuel, ce qui fausse l'historique. De plus, tu as expliqué clairement le mécanisme de l'absence de nouvelles lignes, ce qui permet de comprendre pourquoi les ventes passées sont mal attribuées. C'est une réponse complète et pertinente.

### q32-defense-limite  _(question ouverte)_  — 2.0 / 2

**Question :**

Nommez une limite majeure de votre entrepôt NexaMart+ documentable dans la model card. Expliquez le risque métier et proposez UNE mitigation concrète. (3-6 phrases)

**Ta réponse :**

Le model card est essentiel à la pérennité de l'entrepôt car il documente le grain de chaque table de faits, la politique SCD, les règles NULL, les contraintes du pont pondéré et les limites connues du modèle. Ce document permet de comprendre le raisonnement business derrière ces choix de modélisation.     À titre d'exemple, une limite majeure documentée dans le model card est la semi-additivité de fact_daily_inventory : sommer quantity_on_hand sur plusieurs jours gonfle artificiellement le niveau de stock, car chaque snapshot capture l'état complet de l'inventaire à une date fixe. Le risque métier est concret  : un analyste obtient un chiffre 30× trop élevé sans aucun message d'erreur SQL, ce qui peut induire le CEO à croire que NexaMart n'a pas besoin de réapprovisionner alors que le stock est critique.     La mitigation est d'imposer AVG(quantity_on_hand). Ainsi en utilisant la moyenne au lieu de la somme, on se retrouve avec des valeurs qui sont cohérentes et on peut prendre des décisions éclairées sur l'approvisionnement.

**Commentaire :**

Tu as bien identifié une limite réelle du modèle et expliqué le risque métier associé de manière claire. La mitigation proposée est concrète et pertinente, ce qui montre une bonne compréhension des enjeux liés à la modélisation des données.

---

_Copie générée le 2026-06-25 · GIS805 · Université de Sherbrooke_