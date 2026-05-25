# GIS805 — Séance 04 / 14 — Panier d'achat et drapeaux : les patterns que l'étoile simple ne couvre pas

> Guide de studio (version Markdown). PDF équivalent : `docs/lab-guides/GIS805-04_lab.pdf`.

## En bref

- **Date :** 25 mai 2026
- **Horaire :** 19 h 00 – 22 h 00
- **Lieu :** Longueuil
- **Temps estimé :** 105 min (~1.8 h)

## Objectif

Maîtriser les dimensions dégénérées et les junk dimensions en modélisant les commandes NexaMart avec numéros de commande et profils opérationnels.

## Question du CEO

> « Quels patterns de commande NexaMart sont importants pour les opérations, et quels produits sont achetés ensemble ? »

## Contexte du soir

**NexaMart S04 : Quels patterns de commande NexaMart sont importants pour les**

Les commandes NexaMart ont un numéro unique et 8 drapeaux opérationnels (emballage cadeau, livraison express, fidélité, promo, achat employé, ramassage en ligne, fragile, surdimensionné). Le VP Opérations veut des profils de commande nommés.

## Résultats d'apprentissage

- Identifier et implémenter une dimension dégénérée (numéro de commande).
- Consolider des drapeaux booléens en une junk dimension avec profils nommés.
- Analyser les affinités de panier par paires de produits.
- Produire des profils opérationnels exploitables par un VP.

## Points clés

- Dimension dégénérée = clé sans attributs → reste dans la table de faits.
- Junk dimension = drapeaux consolidés → profils opérationnels exploitables.
- Les profils doivent avoir des noms qu'un VP peut utiliser, pas juste des booléens.

## Idées reçues à déjouer

  **Réalité :** Le numéro de commande n'a pas d'attributs intéressants. C'est une dimension dégénérée stockée directement dans la table de faits.
  **Réalité :** 8 drapeaux = 256 combinaisons possibles. Une junk dimension les consolide et crée des profils analytiques.

## Déroulé

### Partie 1 — Degenerate + junk dim theory  *(20 min)*

Dimension dégénérée, junk dimension, profils nommés

### Partie 2 — Sprint 1 : junk dimension build  *(40 min)*

Construire la junk dimension, nommer les profils, charger dans DuckDB

### Partie 3 — Sprint 2 : basket analysis + brief  *(45 min)*

Analyse de panier par paires, board brief avec recommandations VP

## Lab

**Objectif du lab :** Build junk dimension with named profiles and analyze basket patterns.

**Livrable :** Junk dimension + basket pairs + board brief.

**Fichiers à produire (`repo_artifacts`) :**

- `answers/S04_executive_brief.md`
- `sql/dims/dim_order_profile.sql`
- `sql/analysis/basket_pairs.sql`
- `docs/schema-v2.md`
- `docs/board-briefs/s04-basket-flags.md`

## Remise

- **Échéance :** Before next session starts
- **Artefacts requis :**
  - `answers/S04_executive_brief.md`
  - `db/nexamart.duckdb`
  - `ai-usage.md`
- **Rubrique de notation :**
  - **model_quality** (40 %) — order_number dans fact_sales comme dim dégénérée. Junk dim regroupe ≥ 2 flags avec profils nommés.
  - **validation_quality** (25 %) — Requête retourne les profils nommés agrégés correctement. Aucun fait dans la junk dim.
  - **executive_justification** (20 %) — Recommandation VP justifie le choix junk vs flags séparés avec nombre de combinaisons réelles.
  - **process_trace** (10 %) — Docs/profiles.md liste les profils nommés avec leur fréquence observée dans le seed.
  - **reproducibility** (5 %)

## Lectures

- [Kimball Group -- Degenerate Dimensions](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/degenerate-dimension/) — Quand et pourquoi garder un attribut directement dans la table de faits
- [Kimball Group -- Junk Dimensions](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/junk-dimension/) — Regrouper des drapeaux low-cardinality dans une dimension compacte

---

*Généré automatiquement à partir de `content/sessions/GIS805-04.yaml`. Pour corriger une coquille, modifiez le YAML source et poussez sur `master` — la CI régénère PDF + Markdown.*
