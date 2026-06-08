# GIS805 — Séance 08 / 12 — Ponts pondérés, SCD avancés et relations many-to-many chez NexaMart

> Guide de studio (version Markdown). PDF équivalent : `docs/lab-guides/GIS805-08_lab.pdf`.

## En bref

- **Date :** 8 juin 2026
- **Horaire :** 19 h 00 – 22 h 00
- **Lieu :** Longueuil
- **Temps estimé :** 105 min (~1.8 h)

## Objectif

Résoudre le problème du double-comptage dans les segments clients NexaMart en utilisant des ponts pondérés, implémenter une logique SCD3/hybride, et vérifier la réconciliation des totaux.

## Question du CEO

> « Comment allouer les coûts et comprendre les segments clients qui se chevauchent sans double-compter ? »

## Contexte du soir

**NexaMart S08 : Comment allouer les coûts et comprendre les segments clients**

Les clients NexaMart appartiennent à plusieurs segments (Platinum, Gold, Silver...). Les campagnes marketing sont allouées à plusieurs segments. Le CEO veut voir revenu et coût par segment, mais sans duplication.

## Résultats d'apprentissage

- Construire un pont pondéré customer↔segment avec poids sommant à 1.0.
- Implémenter un SCD Type 3 (current_segment + previous_segment).
- Vérifier que les totaux pondérés réconcilent avec les totaux réels.
- Modéliser une allocation budgétaire campagne↔segment sans duplication.

## Points clés

- Aucun pont n'est accepté sans preuve que les totaux pondérés = totaux réels.
- SCD3 = simple et lisible pour current vs previous.
- La vérification est un livrable, pas un bonus.

## Idées reçues à déjouer

- **Mythe :** On peut simplement joindre clients aux segments sans pondération
  **Réalité :** Un client dans 3 segments sans pondération triple le revenu dans les rapports. Les poids doivent sommer à 1.0.
- **Mythe :** SCD Type 2 est toujours suffisant pour l'historique
  **Réalité :** Pour certains cas (segment actuel vs précédent), un Type 3 est plus simple et plus lisible que Type 2.

## Déroulé

### Partie 1 — Bridge theory + SCD3 intro  *(20 min)*

Ponts pondérés, M:N, SCD3/hybrid, outrigger mention

### Partie 2 — Sprint 1 : weighted bridge  *(45 min)*

Construire bridge_customer_segment, vérifier sum(weight)=1

### Partie 3 — Sprint 2 : reconciliation + campaign allocation  *(40 min)*

Requête de réconciliation, allocation campagne, board brief

## Lab

**Objectif du lab :** Build weighted bridges and verify no double-counting.

**Livrable :** Weighted bridge + reconciliation proof + board brief.

**Fichiers à produire (`repo_artifacts`) :**

- `answers/S08_executive_brief.md`
- `sql/bridges/s08-weighted-allocation.sql`
- `sql/checks/s08-weighted-reconciliation.sql`
- `docs/board-briefs/s08-overlap-risk.md`

## Remise

- **Échéance :** Before next session starts
- **Artefacts requis :**
  - `answers/S08_executive_brief.md`
  - `db/nexamart.duckdb`
  - `ai-usage.md`
- **Rubrique de notation :**
  - **model_quality** (40 %) — bridge_customer_segment avec colonne weight. SCD Type 3 implémenté ou documenté comme décision explicite.
  - **validation_quality** (25 %) — SELECT SUM(weight) GROUP BY customer_key retourne 1.00 pour tous les clients. Revenu sans double-comptage.
  - **executive_justification** (20 %) — Brief distingue le revenu par segment loyauté sans double-comptage. Décision SCD3 justifiée business.
  - **process_trace** (10 %) — docs/bridge-policy.md documenté le choix pondération et la règle de réconciliation SCD3.
  - **reproducibility** (5 %)

## Lectures

- [Kimball Group -- Multivalued Dimensions and Bridge Tables](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/multivalued-dimension-bridge-table/) — Le pattern pont pour les relations M:N sans double-comptage
- [Kimball Group -- SCD Type 3](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-3/) — Garder current et previous dans la même ligne de dimension

---

*Généré automatiquement à partir de `content/sessions/GIS805-08.yaml`. Pour corriger une coquille, modifiez le YAML source et poussez sur `master` — la CI régénère PDF + Markdown.*
