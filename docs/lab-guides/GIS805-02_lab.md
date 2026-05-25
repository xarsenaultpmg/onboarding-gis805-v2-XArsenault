# GIS805 — Séance 02 / 14 — Schéma en étoile, grain et dimensions conformes : le premier modèle NexaMart

> Guide de studio (version Markdown). PDF équivalent : `docs/lab-guides/GIS805-02_lab.pdf`.

## En bref

- **Date :** 14 mai 2026
- **Horaire :** 19 h 00 – 22 h 00
- **Lieu :** Longueuil
- **Temps estimé :** 105 min (~1.8 h)

## Objectif

Concevoir le premier schéma en étoile, définir le grain comme décision irréversible, et prouver par une requête SQL que le modèle répond à la question du CEO.

## Question du CEO

> « Quel schéma en étoile rend votre question CEO répétable et fiable chaque mois ? »

## Contexte du soir

**NexaMart S02 : Quel schéma en étoile rend votre question CEO répétable ?**

Le CEO veut que chaque étudiant modélise son processus principal comme un schéma en étoile. Le grain doit être assez fin pour répondre aux variantes futures de la question, mais pas si fin que la table de faits devienne ingérable.

## Résultats d'apprentissage

- Concevoir un schéma en étoile avec table de faits et dimensions.
- Formaliser un grain statement comme contrat de conception.
- Identifier les dimensions conformes partagées entre tables de faits.
- Écrire une première requête SQL qui prouve que le modèle répond à la question du S01.

## Points clés

- Le grain est un contrat : une ligne dans la table de faits représente exactement...
- Les dimensions conformes partagées (date, product, store) rendent le drill-across possible.
- Un schéma n'est valide que s'il produit une réponse vérifiable.

## Idées reçues à déjouer

  **Réalité :** Le grain est la décision la plus importante et la plus difficile à changer. Un grain trop grossier ferme dès questions pour toujours.
  **Réalité :** Chaque dimension doit répondre à un besoin analytique réel. Trop de dimensions créent de la complexité sans valeur.

## Déroulé

### Partie 1 — Grain : la décision irréversible  *(25 min)*

Théorie du grain, additivity, semi-additivity, exemples NexaMart

### Partie 2 — Sprint 1 : schema v1  *(40 min)*

Grain statement dans le brief, diagramme Mermaid, puis DDL des 5 tables dim_* (dim_product, dim_customer, dim_store, dim_date, dim_channel) depuis les raw_* via make load

### Partie 3 — Sprint 2 : première réponse SQL  *(40 min)*

DDL de fact_sales depuis raw_fact_sales (grain déclaré en commentaire), make load, puis requête CEO dans sql/analysis/s02-ceo-answer.sql et make check

## Lab

**Objectif du lab :** Construire le premier schéma en étoile complet de NexaMart en SQL réel : créer les tables de dimensions (dim_*) depuis les raw_*, créer fact_sales avec un grain déclaré, puis prouver par une requête analytique que le modèle répond à la question du CEO.


Ce lab progresse en trois actes dans l'ordre obligatoire : dims → fact_sales → requête CEO. Une fois vos dim_* et fact_sales créés via make load, toutes les requêtes analytiques partent de fact_sales — jamais des raw_*. Les tables raw_* sont uniquement le matériau brut que make load consomme. DDL (Data Definition Language) désigne les instructions SQL qui créent des structures — ici, CREATE OR REPLACE TABLE. Ce sont ces fichiers .sql qui matérialisent votre schéma en étoile dans DuckDB.

### Avant de commencer — vérifier votre environnement  *(5 min)*

**Objectif :** S'assurer que les données synthétiques sont générées et les tables raw_* chargées dans DuckDB avant d'écrire la moindre ligne de SQL.

1. Depuis la racine du repo dans votre terminal : make generate (génère vos CSV uniques depuis votre username GitHub).
2. Exécutez make load (charge les CSV dans DuckDB sous db/nexamart.duckdb et exécute les SQL existants).
3. Ouvrez DuckDB (duckdb db/nexamart.duckdb) et exécutez SHOW TABLES; — vous devez voir raw_dim_product, raw_dim_customer, raw_dim_store, raw_dim_date, raw_dim_channel, raw_fact_sales.
4. Si une table raw_* est absente, relancez make generate puis make load et vérifiez à nouveau.

**Résultat attendu :** 6 tables raw_* visibles dans DuckDB — prêtes à être transformées.

**Erreurs fréquentes :**
- ⚠️ make generate échoue : vérifiez que votre username GitHub est dans .env et que vous avez suivi le setup S01.
- ⚠️ DuckDB vide après make load : vérifiez que vous êtes à la racine du repo (là où se trouve le Makefile).

### Déclarer le grain avant toute ligne de SQL  *(10 min)*

**Objectif :** Ancrer la décision de grain comme phrase écrite et vérifiable avant d'ouvrir DuckDB.

1. Ouvrez answers/S02_executive_brief.md.
2. Sous Décisions de modélisation, écrivez : Une ligne dans fact_sales représente [votre grain], identifiée par [colonnes clé naturelle].
3. Posez-vous la question : si une commande contient 3 produits, combien de lignes génère-t-elle dans fact_sales ? Notez le nombre dans le brief.
4. Validez avec votre voisin : en lisant votre phrase, peut-il deviner combien de lignes une commande de 5 produits génère ?
5. Dans GitHub Copilot Chat, copiez ce prompt : Génère un diagramme Mermaid erDiagram pour mon étoile NexaMart. Au centre : FACT_SALES au grain [votre grain exact]. Inclus : DIM_PRODUCT, DIM_CUSTOMER, DIM_DATE, DIM_STORE, DIM_CHANNEL. Montre les clés étrangères avec ||--o{. Syntaxe DuckDB. Pas de snowflake.
6. Insérez le bloc mermaid généré dans le brief juste sous votre phrase de grain. Vérifiez : chaque dimension est-elle connectée à FACT_SALES ? Le grain dans le diagramme correspond-il à votre phrase de l'étape 2 ?

**Résultat attendu :** Phrase de grain + diagramme Mermaid insérés dans le brief — avant d'écrire une ligne de DDL.

**Erreurs fréquentes :**
- ⚠️ Grain vague comme une vente : demandez-vous si c'est une vente d'un produit ou d'une commande entière.
- ⚠️ Grain au niveau en-tête de commande : impossible de ventiler par produit — votre requête CEO échouera en Sprint 2.

### Créer les tables de dimensions depuis les raw_*  *(30 min)*

**Objectif :** Écrire le DDL pour transformer chaque table raw_dim_* en une vraie table dim_* avec clé subrogée et colonnes propres.

Après make generate && make load, les tables raw_dim_* existent dans DuckDB. Votre travail : écrire le DDL (CREATE OR REPLACE TABLE ... AS SELECT ...) qui crée les dim_* depuis ces raw. Chaque fichier sql/dims/*.sql correspond à une dimension. Utilisez sql/templates/01_dim_from_raw.sql comme modèle.

1. Créez sql/dims/dim_product.sql depuis raw_dim_product. Colonnes obligatoires : product_key (ROW_NUMBER), product_id (clé naturelle), name, category, subcategory, brand, unit_cost.
2. Créez sql/dims/dim_customer.sql depuis raw_dim_customer. Colonnes : customer_key, customer_id, full_name, loyalty_segment, city, province.
3. Créez sql/dims/dim_store.sql depuis raw_dim_store. Colonnes : store_key, store_id, store_name, city, province, region.
4. Créez sql/dims/dim_date.sql depuis raw_dim_date. Colonnes : date_key, date, day, month, quarter, year, month_name.
5. Créez sql/dims/dim_channel.sql depuis raw_dim_channel. Colonnes : channel_key, channel_id, channel_name, channel_type.
6. Exécutez make load. Vérifiez que chaque dim_*.sql affiche OK sans erreur.
7. Dans DuckDB, vérifiez : SELECT COUNT(*) FROM dim_product; — le nombre doit correspondre à vos CSV.

**Résultat attendu :** 5 fichiers sql/dims/ + toutes les tables dim_* présentes et peuplées dans DuckDB.

**Erreurs fréquentes :**
- ⚠️ Oublier WHERE [clé] IS NOT NULL : les NULL dans les clés naturelles cassent les jointures dans fact_sales.
- ⚠️ Garder les noms bruts (ex : p_id) sans renommer : les FK dans fact_sales ne correspondront pas.
- ⚠️ Ne pas relancer make load après écriture : les tables n'existent pas tant que make load n'a pas tourné.

### Créer fact_sales avec le grain déclaré  *(20 min)*

**Objectif :** Construire la table de faits qui référence les dimensions via leurs clés naturelles et respecte le grain déclaré à l'exercice 1.

Pour S02, fact_sales utilise les clés naturelles (_id) pour les jointures, pas encore les clés subrogées (_key). Cela suffit pour prouver le modèle. Le pipeline make load exécute dans l'ordre staging → dims → facts : fact_sales doit donc venir après les dims.

1. Créez sql/facts/fact_sales.sql. Première ligne : -- GRAIN : une ligne = [votre grain statement exact].
2. Sélectionnez depuis raw_fact_sales : order_number, sale_line_id (dégénérés), order_date, customer_id, product_id, store_id, channel_id, quantity, unit_price, discount_pct, net_price, line_total.
3. Ajoutez la mesure dérivée : quantity * unit_price AS gross_amount.
4. Exécutez make load — vérifiez que fact_sales se crée sans erreur après les dims.
5. Testez une jointure : SELECT COUNT(*) FROM fact_sales f JOIN dim_product p ON f.product_id = p.product_id; — ce COUNT doit égaler COUNT(*) FROM fact_sales.

**Résultat attendu :** sql/facts/fact_sales.sql fonctionnel + fact_sales peuplé dans DuckDB avec jointures qui fonctionnent.

**Erreurs fréquentes :**
- ⚠️ Joindre sur product_key au lieu de product_id : les _key n'existent dans raw_* que si vous les avez créés. Utilisez les _id.
- ⚠️ grain_unique FAIL dans make check : deux lignes ont le même (order_number, sale_line_id). Vérifiez votre clause SELECT.

### La requête CEO depuis fact_sales — quitter les raw_* pour toujours  *(25 min)*

**Objectif :** Écrire la requête analytique en joignant fact_sales aux dimensions — jamais aux raw_* — et coller le résultat dans le brief exécutif.

À partir de maintenant, toutes vos requêtes analytiques partent de fact_sales et joignent les dim_*. Vous ne touchez plus aux raw_* pour des analyses.

1. Créez sql/analysis/s02-ceo-answer.sql.
2. Écrivez la requête : revenus par catégorie de produit, par région de magasin, par trimestre. Joignez fact_sales à dim_product (category), dim_store (region), dim_date (quarter). Agrégez avec SUM(line_total).
3. Exécutez dans DuckDB — vérifiez des lignes avec des chiffres non-NULL et non-zéro.
4. Copiez les premières lignes du résultat dans answers/S02_executive_brief.md, section Preuve. Répondez en 2 phrases à la question du CEO.
5. Exécutez make check — les 4 checks S02 doivent être PASS : fact_sales_not_empty, dim_keys_unique, fact_sales_no_null_fk, grain_unique_fact_sales.

**Résultat attendu :** sql/analysis/s02-ceo-answer.sql fonctionnel + résultats dans le brief + make check tout vert.

**Erreurs fréquentes :**
- ⚠️ GROUP BY incomplet : vous obtenez une seule ligne. Chaque colonne non agrégée dans SELECT doit être dans GROUP BY.
- ⚠️ NULL dans region ou category : jointure manquante ou FK incorrecte. Déboguez avec WHERE region IS NULL.
- ⚠️ Requêter raw_fact_sales au lieu de fact_sales : les calculs fonctionnent mais la valeur du modèle dimensionnel est perdue.

### Traçabilité IA — compléter ai-usage.md  *(5 min)*

**Objectif :** Documenter les interactions IA significatives qui ont influencé vos décisions ce soir.

ai-usage.md n'est pas une formalité. C'est un contrat intellectuel : quelles décisions avez-vous déléguées à l'IA, et lesquelles avez-vous prises vous-même ? Le grain statement, le choix des colonnes et les noms de FK vous appartiennent.

1. Ouvrez ai-usage.md à la racine du repo (créez-le s'il n'existe pas encore).
2. Pour chaque interaction IA significative ce soir (génération du Mermaid, DDL d'une dim, correction d'erreur make check), notez : prompt résumé | résultat obtenu | ce que vous avez modifié avant d'accepter.
3. Une ligne par interaction suffit — l'objectif est de montrer votre raisonnement, pas de remplir une grille.

**Résultat attendu :** ai-usage.md non vide avec au moins 2-3 interactions documentées.

**Erreurs fréquentes :**
- ⚠️ ai-usage.md absent : artefact requis — la CI bloque la soumission s'il manque.
- ⚠️ Entrées vides ou trop génériques (ex : utilisé Copilot) : notez au moins la décision que vous avez prise après chaque suggestion.

Les fichiers se créent dans cet ordre strict : dims → fact_sales → requête CEO. Si make check échoue sur dim_keys_unique, corrigez avant de tester fact_sales. Si fact_sales_no_null_fk échoue, vos noms de colonnes FK ne correspondent pas.

**Fichiers à produire (`repo_artifacts`) :**

- `sql/dims/dim_product.sql` — DDL dimension produit (product_key, product_id, name, category, subcategory, brand)
- `sql/dims/dim_customer.sql` — DDL dimension client (customer_key, customer_id, full_name, loyalty_segment, city, province)
- `sql/dims/dim_store.sql` — DDL dimension magasin (store_key, store_id, store_name, city, province, region)
- `sql/dims/dim_date.sql` — DDL dimension date (date_key, date, day, month, quarter, year)
- `sql/dims/dim_channel.sql` — DDL dimension canal (channel_key, channel_id, channel_name)
- `sql/facts/fact_sales.sql` — DDL fact_sales au grain déclaré, avec commentaire grain et FK vers toutes les dimensions
- `sql/analysis/s02-ceo-answer.sql` — Requête CEO : revenus par catégorie × région × trimestre depuis fact_sales JOIN dim_*
- `answers/S02_executive_brief.md` — Brief exécutif avec grain statement, schéma Mermaid, preuve SQL (résultats copiés)

## Remise

- **Échéance :** Before next session starts
- **Artefacts requis :**
  - `sql/dims/dim_product.sql`
  - `sql/dims/dim_customer.sql`
  - `sql/dims/dim_store.sql`
  - `sql/dims/dim_date.sql`
  - `sql/dims/dim_channel.sql`
  - `sql/facts/fact_sales.sql`
  - `sql/analysis/s02-ceo-answer.sql`
  - `answers/S02_executive_brief.md`
  - `db/nexamart.duckdb`
  - `ai-usage.md`
- **Rubrique de notation :**
  - **model_quality** (40 %) — Grain de fact_sales déclaré ('une ligne = une ligne de commande'). Schéma Mermaid cohérent avec ≥ 3 dimensions.
  - **validation_quality** (25 %) — Requête retourne les ventes par catégorie, région et trimestre sans erreur.
  - **executive_justification** (20 %) — Brief situe le résultat dans le contexte des ventes NexaMart en déclin.
  - **process_trace** (10 %) — Décision log documenté le choix de grain avec justification business.
  - **reproducibility** (5 %)

## Lectures

- [Kimball Group -- Star Schema Fundamentals](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/star-schema-olap-cube/) — Le schema en étoile et la declaration du grain
- [dbt Labs -- How we structure our dbt projects](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview) — Bonnes pratiques de structuration analytique moderne
- [DuckDB -- SQL Introduction](https://duckdb.org/docs/sql/introduction) — Syntaxe SQL dans DuckDB pour créer tables et vues

---

*Généré automatiquement à partir de `content/sessions/GIS805-02.yaml`. Pour corriger une coquille, modifiez le YAML source et poussez sur `master` — la CI régénère PDF + Markdown.*
