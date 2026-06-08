# GIS805 — Séance 07 / 12 — Soirée d'intégration : multi-star, drill-across et réel-vs-cible

> Guide de studio (version Markdown). PDF équivalent : `docs/lab-guides/GIS805-07_lab.pdf`.

## En bref

- **Date :** 4 juin 2026
- **Horaire :** 19 h 00 – 22 h 00
- **Lieu :** Longueuil
- **Temps estimé :** 105 min (~1.8 h)

## Objectif

Intégrer les étoiles indépendantes de NexaMart via les dimensions conformes. Construire 4 tables de faits, écrire des requêtes drill-across, et comparer le réel aux cibles budgétaires.

## Question du CEO

> « Le board peut-il voir ventes, retours, inventaire et budget dans une seule vue sans mentir ? »

## Contexte du soir

**NexaMart S07 : Le board peut-il voir ventes, retours, inventaire et budget **

C'est la soirée d'intégration. Jusqu'à présent, chaque étoile existait indépendamment. Le CEO veut une vue consolidée : ventes réelles vs budget, taux de retour par catégorie, et niveaux d'inventaire. Tout doit passer par des dimensions conformes.

## Résultats d'apprentissage

- Concevoir plusieurs tables de faits partageant des dimensions conformes.
- Écrire une requête drill-across correcte entre fact_sales et fact_returns.
- Construire une vue réel-vs-budget sans joindre des faits entre elles.
- Publier un bus matrix documentant la conformité entre vos tables de faits.

## Points clés

- Cette soirée intègre vos étoiles indépendantes en un entrepôt cohérent.
- Chaque jointure doit passer par des dimensions conformes — jamais fact-to-fact.
- Le bus matrix est le document le plus important de l'intégration.

## Idées reçues à déjouer

- **Mythe :** On peut joindre deux tables de faits directement
  **Réalité :** Joindre fact_sales à fact_returns crée un produit cartésien. Le drill-across passe par les dimensions conformes.
- **Mythe :** Budget et ventes ont le même grain
  **Réalité :** fact_budget est mensuel par catégorie×magasin. fact_sales est transactionnel. Le drill-across exige une agrégation au grain commun.

## Déroulé

### Partie 1 — Multi-star theory + bus matrix  *(20 min)*

Dimensions conformes, drill-across, grains multiples

### Partie 2 — Sprint 1 : integration night  *(45 min)*

Charger 4 fact tables, vérifier conformité, écrire drill-across

### Partie 3 — Sprint 2 : actual-vs-budget + board report  *(40 min)*

Vue réel-vs-cible, rapport consolidé pour le board

## Lab

**Objectif du lab :** Integrer les etoiles independantes NexaMart via les dimensions conformes. Construire un drill-across entre fact_sales et fact_returns, une vue actual-vs-budget au grain commun, et repondre a la question du CEO avec evidence provenant d'au moins deux tables de faits.


Votre DuckDB (db/nexamart.duckdb) contient 4 tables de faits independantes chargees via make generate && make load. Ce soir vous les integrez en un entrepot coherent via les dimensions conformes. Attention : fact_budget.category est un VARCHAR brut — pas de FK vers dim_product, mais les valeurs categoriques sont identiques (Electronics, Clothing, etc.).

**Livrable :** Bus matrix + drill-across ventes x retours + vue actual-vs-budget + board brief.

### Exercice 0 — Decouverte du schema  *(10 min)*

**Objectif :** Verifier que les 4 tables sont chargees et comprendre les colonnes disponibles avant d ecrire une seule requete d integration.

fact_budget.category est un VARCHAR brut. Verifiez que ses valeurs correspondent exactement a dim_product.category avant les sprints.

1. make generate && make load  (ou make check si deja fait)
2. SELECT COUNT(*) FROM fact_sales;
3. SELECT COUNT(*) FROM fact_returns;
4. SELECT COUNT(*) FROM fact_inventory_snapshot;
5. SELECT COUNT(*) FROM fact_budget;
6. DESCRIBE fact_sales; DESCRIBE fact_returns; DESCRIBE fact_budget;
7. SELECT DISTINCT category FROM fact_budget ORDER BY 1;
8. SELECT DISTINCT category FROM dim_product ORDER BY 1;
9. -- Les deux listes doivent etre identiques (case-sensitive). Si non : le FULL OUTER JOIN donnera des NULLs.

**Résultat attendu :** 4 tables non vides. fact_budget.category et dim_product.category ont exactement les memes valeurs distinctes.


**Erreurs fréquentes :**
- ⚠️ fact_budget.category ne correspond pas a dim_product.category : verifiez majuscules et espaces
- ⚠️ Table vide apres make load : re-lancez make generate puis make load

### Exercice 1 — Bus Matrix  *(15 min)*

**Objectif :** Documenter quelles dimensions sont conformes entre les 4 tables de faits. C est le livrable d architecture le plus important de ce soir.

Une dimension est conforme si elle partage les memes cles entre plusieurs tables de faits. fact_budget utilise store_key et category (degenerate) — pas de customer_key ni de channel_key. Justifiez chaque case vide.

1. Creez docs/bus-matrix.md avec ce squelette (completez les cases avec une coche ou laissez vide) :
2. | Dimension               | fact_sales | fact_returns | fact_inventory_snapshot | fact_budget |
3. |-------------------------|------------|--------------|-------------------------|-------------|
4. | dim_date (date_key)     |            |              |                         |             |
5. | dim_product (product_key)|           |              |                         |             |
6. | dim_store (store_key)   |            |              |                         |             |
7. | dim_customer            |            |              |                         |             |
8. | dim_promo               |            |              |                         |             |
9. Requete de verification de conformite :
10. SELECT COUNT(DISTINCT product_key) FROM fact_sales;
11. SELECT COUNT(DISTINCT product_key) FROM fact_returns;
12. -- Les deux doivent reference les memes product_key dans dim_product
13. Ajoutez une note : dim_customer absent de fact_budget = grain different (intentionnel)
14. git add docs/bus-matrix.md && git commit -m 'S07 bus-matrix documented'

**Résultat attendu :** docs/bus-matrix.md commite avec 5 dimensions x 4 tables de faits, coches pour les cases conformes, cases vides justifiees.


**Erreurs fréquentes :**
- ⚠️ Coche pour dim_customer dans fact_budget : fact_budget n'a pas de customer_key
- ⚠️ Oublier fact_inventory_snapshot dans la matrice
- ⚠️ Cases vides sans justification : expliquez pourquoi la dimension est absente

### Exercice 2 — Drill-across ventes vs retours  *(30 min)*

**Objectif :** Ecrire une requete drill-across fonctionnelle entre fact_sales et fact_returns via dim_product, sans produit cartesien.

Fichier cible : sql/integration/s07-drill-across.sql. Grain commun : category x mois. Verifiez imperativement que SUM(revenue) de votre CTE sales_agg = SUM(line_total) de fact_sales. Si ce n est pas le cas, votre GROUP BY est incorrect.

1. Creez sql/integration/s07-drill-across.sql
2. -- CTE 1 : ventes aggregees au grain category x mois
3. WITH sales_agg AS (
4.   SELECT p.category, DATE_TRUNC('month', f.order_date) AS mois,
5.          SUM(f.line_total) AS revenue, SUM(f.quantity) AS units_sold
6.   FROM fact_sales f JOIN dim_product p USING (product_key) GROUP BY 1, 2),
7. -- CTE 2 : retours aggreges au meme grain
8.   returns_agg AS (
9.   SELECT p.category, DATE_TRUNC('month', r.return_date) AS mois,
10.          SUM(r.refund_amount) AS total_refunds, SUM(r.return_quantity) AS units_returned
11.   FROM fact_returns r JOIN dim_product p USING (product_key) GROUP BY 1, 2)
12. -- Jointure via FULL OUTER JOIN sur le grain commun
13. SELECT COALESCE(s.category, r.category) AS category,
14.        COALESCE(s.mois, r.mois)          AS mois,
15.        s.revenue, s.units_sold, r.total_refunds, r.units_returned
16. FROM sales_agg s FULL OUTER JOIN returns_agg r
17.   ON s.category = r.category AND s.mois = r.mois
18. ORDER BY 2, 1;
19. -- VERIFICATION OBLIGATOIRE (ajoutez en commentaire avec le resultat observe) :
20. -- SELECT SUM(revenue) FROM sales_agg; => doit egaliser SELECT SUM(line_total) FROM fact_sales
21. git add -A && git commit -m 'S07 sprint1 drill-across fonctionnel'

**Résultat attendu :** Tableau category x mois avec revenue et total_refunds cote a cote. SUM(revenue) de la CTE = SUM(line_total) de fact_sales.


**Erreurs fréquentes :**
- ⚠️ JOIN direct fact_sales JOIN fact_returns sans CTE : produit cartesien garanti
- ⚠️ INNER JOIN au lieu de FULL OUTER JOIN : perd les categories avec ventes mais 0 retours
- ⚠️ GROUP BY incomplet (oublier le mois) : totaux incorrects et non reconciliables
- ⚠️ product_key au lieu de category dans le grain : fact_budget ne connait pas les product_key

### Exercice 3 — Reel vs budget  *(25 min)*

**Objectif :** Construire une vue actual_vs_budget au grain category x store_key x mois, avec variance absolue et variance en pourcentage.

Fichier cible : sql/integration/s07-actual-vs-budget.sql. fact_budget.category est un VARCHAR degenerate (pas de FK vers dim_product). Pour joindre avec fact_sales, aggregez d abord via dim_product pour obtenir p.category. Le grain commun est (category, store_key, budget_month).

1. Creez sql/integration/s07-actual-vs-budget.sql
2. -- CTE : fact_sales au grain category x store_key x mois
3. WITH actual AS (
4.   SELECT p.category, f.store_key, DATE_TRUNC('month', f.order_date) AS mois,
5.          SUM(f.line_total) AS actual_revenue
6.   FROM fact_sales f JOIN dim_product p USING (product_key) GROUP BY 1, 2, 3)
7. -- Jointure avec fact_budget sur le grain commun
8. SELECT COALESCE(a.category, b.category)    AS category,
9.        COALESCE(a.store_key, b.store_key)  AS store_key,
10.        COALESCE(a.mois, b.budget_month)    AS mois,
11.        a.actual_revenue,
12.        b.target_revenue,
13.        (a.actual_revenue - b.target_revenue)              AS variance,
14.        ROUND(100.0*(a.actual_revenue - b.target_revenue)
15.              / NULLIF(b.target_revenue, 0), 1)            AS pct_variance
16. FROM actual a FULL OUTER JOIN fact_budget b
17.   ON  a.category  = b.category
18.   AND a.store_key = b.store_key
19.   AND a.mois      = b.budget_month
20. ORDER BY mois, category;
21. Creez sql/checks/s07-reconciliation.sql avec les deux verifications :
22. -- 1. SELECT SUM(actual_revenue) FROM actual; => doit egaliser SELECT SUM(line_total) FROM fact_sales
23. -- 2. SELECT SUM(revenue) FROM sales_agg;   => idem (recopiez depuis s07-drill-across.sql)
24. git add -A && git commit -m 'S07 sprint2 actual-vs-budget + reconciliation'

**Résultat attendu :** Vue avec category, store_key, mois, actual_revenue, target_revenue, variance, pct_variance. Les categories avec budget mais 0 ventes apparaissent (FULL OUTER JOIN). Totaux reconcilies.


**Erreurs fréquentes :**
- ⚠️ Oublier dim_product dans la CTE actual : fact_sales n'a pas de colonne category
- ⚠️ INNER JOIN avec fact_budget : perd les categories avec budget mais 0 ventes reelles
- ⚠️ Division sans NULLIF : erreur de division par zero si target_revenue = 0
- ⚠️ Joindre sur store_id au lieu de store_key : fact_budget n'a pas de colonne store_id

Committez incrementalement (>= 3 commits distincts). Documentez chaque interaction IA dans ai-usage.md (outil, prompt utilise, ce que vous avez valide manuellement). Ces deux points valent 15 % de la note (process_trace 10 % + reproducibility 5 %).

**Fichiers à produire (`repo_artifacts`) :**

- `answers/S07_executive_brief.md` — Brief CEO : quelle categorie depasse ou manque son budget ? (chiffre observe obligatoire, evidence provenant d au moins 2 tables de faits)
- `docs/bus-matrix.md` — Tableau markdown 5 dimensions x 4 tables de faits avec coches et justifications pour les cases vides
- `sql/integration/s07-drill-across.sql` — CTE drill-across ventes x retours avec verification reconciliation en commentaire
- `sql/integration/s07-actual-vs-budget.sql` — Vue actual-vs-budget avec variance et pct_variance au grain category x store_key x mois
- `sql/checks/s07-reconciliation.sql` — Deux requetes de verification : SUM(actual_revenue) = SUM(line_total), SUM(revenue du drill-across) = SUM(line_total)
- `docs/board-briefs/s07-enterprise-view.md` — Vue consolidee pour le board repondant a la question du CEO avec evidence multi-table

## Remise

- **Échéance :** Before next session starts
- **Artefacts requis :**
  - `answers/S07_executive_brief.md`
  - `db/nexamart.duckdb`
  - `ai-usage.md`
- **Rubrique de notation :**
  - **model_quality** (40 %) — Bus matrix complète. Drill-across entre deux fact tables via une dimension conforme.
  - **validation_quality** (25 %) — Requête drill-across retourne un résultat cohérent entre les deux tables (même dimension de jointure).
  - **executive_justification** (20 %) — Brief répond à une question qui nécessite les deux tables. Énonce explicitement la dimension conforme utilisée.
  - **process_trace** (10 %) — Bus matrix commitée dans docs/bus-matrix.md. Décision de grain partagé documentée.
  - **reproducibility** (5 %)

## Lectures

- [Kimball Group -- Conformed Dimensions](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/conformed-dimension/) — Dimensions partagees entre tables de faits pour le drill-across
- [Kimball Group -- Enterprise Data Warehouse Bus Architecture](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/kimball-data-warehouse-bus-architecture/) — La bus matrix comme outil d'integration entre tables de faits
- [DuckDB -- Multiple Result Sets](https://duckdb.org/docs/sql/query_syntax/select) — Syntaxe SQL pour les requêtes multi-tables et les CTEs

---

*Généré automatiquement à partir de `content/sessions/GIS805-07.yaml`. Pour corriger une coquille, modifiez le YAML source et poussez sur `master` — la CI régénère PDF + Markdown.*
