# Trace d'usage IA — GIS805

> Chaque interaction significative avec un outil IA doit être documentée ici.
> Ce fichier est **obligatoire** et évalué à chaque remise.

## Format par entrée

```
### YYYY-MM-DD — Séance SXX
- **Modèle :** (ChatGPT-4o, Claude, Copilot, etc.)
- **Prompt :** (copier-coller exact)
- **Résultat :** (résumé de ce que l'IA a produit)
- **Validation :** (comment vous avez vérifié/modifié le résultat)
- **Justification :** (pourquoi cette interaction était nécessaire)
```

---

### 2026-05-10 — Séance S01
- **Modèle :** Claude Sonnet 4.6
- **Prompt :** « Aide-moi à remplir le document S01_executive_brief.md pour répondre à la question du CEO : quelles catégories déclinent dans quelles régions et pourquoi ? »
- **Résultat :** Claude a guidé la rédaction de chaque section du brief : réponse exécutive, décisions de modélisation, preuve SQL, validation et risques. Il a aussi construit la requête SQL avec window function LAG pour identifier les déclins trimestriels.
- **Validation :**
  - J'ai roulé toutes les requêtes dans mon Codespace sur ma base `db/nexamart.duckdb` pour vérifier les résultats.
  - J'ai validé la réconciliation des totaux (896 840.55 $ brut = 896 840.55 $ avec jointures).
  - J'ai vérifié manuellement Québec/Home & Garden : seulement 5 transactions en Q2 — signal retiré des priorités CEO.
  - J'ai confirmé que mes données ne couvrent que 2025, ce qui a justifié le choix d'une comparaison QoQ plutôt qu'YoY.
- **Justification :** Claude a servi de co-équipier analytique pour structurer la démarche, construire les requêtes SQL et valider la cohérence des chiffres avant présentation au CEO. Toutes les décisions finales et la validation des résultats ont été faites par moi.

### 2026-05-14 — Séance S02
- **Modèle :** Claude Sonnet 4.6
- **Prompt :** « Implement the plan Livrables S02 (par artefact) : SQL d’analyse, diagramme Mermaid, docs/schema-v1.md, board brief, S02_executive_brief.md, ai-usage ; commentaires SQL en français ; valider sur db/nexamart.duckdb. » — puis, dans des échanges suivants : modèle Draw.io, lisibilité (texte noir), cohérence des libellés avec le Mermaid, clarification SK/SCD vs lab S02.
- **Résultat :** Fichiers créés selon le plan (`sql/analysis/s02-first-answer.sql`, `diagrams/schema-v1.mmd`, `docs/schema-v1.md`, `docs/board-briefs/s02-star-schema.md`, `answers/S02_executive_brief.md`) ; ajout de `diagrams/schema-v1.drawio` ; chiffres de preuve et validation issus d’une exécution locale sur `db/nexamart.duckdb`. Ensuite : alignement des étiquettes de liaison Draw.io sur les libellés du `.mmd`, bloc `FACT_SALES` harmonisé avec les colonnes du Mermaid, note sur les clés naturelles v1 ; section **« Clés substitutives (SK) et SCD »** dans `docs/schema-v1.md` (hors exigences explicites du [GIS805-02_lab.md](docs/lab-guides/GIS805-02_lab.md)).
- **Validation :**
  - Requête S02 exécutée sans erreur ; `SUM(line_total)` identique avec et sans jointures ; 0 orphelin sur les trois dimensions utilisées ; 3 000 lignes et 3 000 `sale_line_id` distincts.
  - Relu les textes pour alignement avec [docs/schema-v1.md](docs/schema-v1.md) et la rubrique du lab (grain, catégorie / région / trimestre).
  - Vérifié la cohérence visuelle entre [diagrams/schema-v1.mmd](diagrams/schema-v1.mmd) et [diagrams/schema-v1.drawio](diagrams/schema-v1.drawio) (mêmes relations et libellés de rôles sur les flèches ; colonnes du fait alignées).
  - Relu la section SK/SCD : formulation conforme au guide de lab S02 (pas d’obligation de SK ni de SCD à cette séance).
- **Justification :** Accélérer la mise en forme des livrables et la validation SQL tout en conservant les décisions de conception et les montants vérifiés manuellement sur la base locale ; itérer sur les diagrammes et la doc pour lever l’ambiguïté SK/SCD et garder une trace d’usage complète.

### 2026-05-15 — Séance S02 (harmonisation lab)
- **Modèle :** Cursor / agent
- **Prompt :** Harmoniser tous les livrables S02 sur le lab (pas de `dim_order`, cinq dimensions dont `dim_channel`, `order_number` dégénérée).
- **Résultat :** Mise à jour de `fact_sales.sql`, `schema-v1.mmd`, `schema-v1.md`, `schema-v1.drawio`, briefs, `sql/dims/README.md`.
- **Validation :** `.\run.ps1 load` puis `.\run.ps1 check` ; `.\run.ps1 sql sql\analysis\s02-first-answer.sql`.
- **Justification :** Aligner le dépôt sur GIS805-02 et `s02-sample-brief.md` après écart avec une variante « diapo order_key ».

### 2026-05-21 — Séance S03
- **Modèle :** Claude Sonnet 4.6
- **Prompt :** « Aide-moi à livrer la séance S03 : quels changements dans nos dimensions doivent garder la vérité historique, et lesquels peuvent être écrasés ? Je dois montrer au VP pourquoi l’ancien rapport était trompeur, rédiger la politique SCD, et prouver la différence entre Type 1 et Type 2 avec du SQL sur mes données NexaMart. »
- **Résultat :** Claude a guidé la rédaction du brief exécutif (réponse au CEO, décisions de modélisation, risques), de la politique SCD par attribut dans `docs/scd-policy.md`, et du brief conseil. Il a aidé à construire la démo `sql/scd/type1_vs_type2_demo.sql` (rapport trompeur vs correct par segment) et à historiser `dim_customer` / `dim_store` avec `valid_from`, `valid_to` et `is_current`, ainsi que les jointures temporelles dans `fact_sales`.
- **Validation :**
  - J’ai roulé `.\run.ps1 generate`, `.\run.ps1 load` et les requêtes de démo sur `db/nexamart.duckdb` pour vérifier les chiffres du brief.
  - J’ai confirmé le check `scd2_one_current` (PASS) et que `dim_customer` passe de 285 à 443 lignes après historisation — cohérent avec les événements de `raw_customer_changes`.
  - J’ai vérifié l’exemple **CUS-00152** : 5 527,41 $ identiques, mais segment **Inactive** (Type 2, juste) vs **New** (Type 1, faux) — retenu comme illustration principale dans le brief.
  - J’ai validé l’écart agrégé sur le segment **Gold** (129,78 $) entre les deux rapports, pour montrer que l’erreur n’est pas seulement théorique.
  - J’ai relu `docs/scd-policy.md` et les sections exécutives pour m’assurer que les justifications restent en langage d’affaires (segment, région, moment de la vente), pas en jargon technique.
- **Justification :** Claude a servi de co-équipier pour structurer la politique SCD, formuler l’argument VP (« pourquoi l’historique était faux ») et accélérer le SQL de preuve. Le choix Type 1 vs Type 2 par attribut, l’exemple client retenu et la validation des montants ont été faits par moi.

### 2026-05-25 — Séance S04
- **Modèle :** Cursor / agent (Claude)
- **Prompt :** « Implémenter le plan Lab GIS805-04 : junk dimension dim_order_profile, profile_key dans fact_sales, basket_pairs.sql, docs schema-v2/profiles/board brief, S04_executive_brief, 5 commits atomiques. »
- **Résultat :** Création de `sql/dims/dim_order_profile.sql` (CASE pour profils VP), enrichissement de `fact_sales` via `raw_orders`, requête `basket_pairs.sql`, documentation et brief exécutif avec chiffres du seed d’équipe.
- **Validation :**
  - `.\run.ps1 generate`, `.\run.ps1 load`, `.\run.ps1 check` — `dim_order_profile` présent, grain fact_sales PASS.
  - Vérifié **99** combinaisons observées vs **256** théoriques ; fréquences recopiées dans `docs/profiles.md` depuis requête sur `raw_orders`.
  - Exécuté `basket_pairs.sql` : top paires à 9 co-occurrences ; revenus par profil contrôlés manuellement pour les 3 premiers libellés.
  - Relu les noms de profils (« Commande standard », « Promo fidélité », etc.) pour lisibilité VP.
- **Justification :** Accélérer la construction SQL et la doc tout en validant chaque chiffre du brief sur `db/nexamart.duckdb` local ; les choix de nommage et la priorisation des recommandations VP restent ma responsabilité.

### 2026-06-04 — Séance S07
- **Modèle :** Claude Sonnet 4.6
- **Prompt :** « Aide-moi à livrer la séance S07 : le board peut-il voir ventes, retours, inventaire et budget dans une seule vue sans mentir ? Je dois construire les tables de faits manquantes, écrire un drill-across entre fact_sales et fact_returns, une vue réel-vs-budget, et répondre à la question du CEO avec des chiffres sur mes données. Utilise mes tables DuckDB modélisées, pas les raw. »
- **Résultat :** Claude a guidé la création des tables de faits manquantes (`fact_returns`, `fact_budget`, `fact_inventory_snapshot`), des requêtes d'intégration (`s07-drill-across.sql`, `s07-actual-vs-budget.sql`), du fichier de réconciliation, de la bus matrix et des deux briefs. Toutes les analyses partent de `fact_*` et `dim_*`, pas des `raw_*`.
- **Validation :**
  - J'ai roulé `.\run.ps1 generate` puis `.\run.ps1 load` sur `db/nexamart.duckdb` (seed `team_3577855103`) pour matérialiser les 4 faits : `fact_sales` (3 000 lignes), `fact_returns` (161), `fact_budget` (1 200), `fact_inventory_snapshot` (6 996).
  - J'ai exécuté `sql/checks/s07-reconciliation.sql` : les 4 contrôles retournent `PASS` avec écart `0,00` — les totaux agrégés par CTE sont identiques aux totaux directs des tables.
  - J'ai exécuté le drill-across ventes × retours et retenu le KPI **Automotive — mars 2025** : 931,92 $ de remboursements sur 4 351,32 $ de ventes, soit **21,42 %** de taux — signal le plus fort sur mes données.
  - J'ai exécuté la vue réel-vs-budget et retenu **Sports & Outdoors — NexaMart Calgary — mai 2025** : -100 916,21 $ (-99,3 %) comme écart le plus significatif à reporter au CFO.
  - J'ai relu `docs/bus-matrix.md` pour vérifier que les dimensions conformes utilisées dans les requêtes corresponde bien à celles déclarées dans la matrice.
- **Justification :** Claude a servi de co-équipier analytique pour structurer l'intégration multi-star, construire les requêtes drill-across au grain commun et produire les preuves chiffrées pour le brief. Les KPI retenus, les interprétations business et la validation des totaux ont été faits par moi.

### 2026-06-08 — Séance S08
- **Modèle :** Cursor / agent GPT-5.5
- **Prompt :** « Aide-moi à remplir le document S08_executive_brief.md pour répondre à la question du CEO : comment allouer les coûts et comprendre les segments clients qui se chevauchent sans double-compter ? »
- **Résultat :** L'agent a aidé à matérialiser les dimensions S08 manquantes (`dim_segment_outrigger`, `dim_customer_scd3`), à écrire l'allocation pondérée (`sql/bridges/s08-weighted-allocation.sql`), la réconciliation (`sql/checks/s08-weighted-reconciliation.sql`), le brief exécutif S08 et la note de risque board.
- **Validation :**
  - J'ai roulé `.\run.ps1 generate` avec le seed `team_3577855103`, puis `.\run.ps1 load` pour charger les tables dans `db/nexamart.duckdb`.
  - J'ai exécuté `sql/bridges/s08-weighted-allocation.sql` sur DuckDB : le revenu réel pondéré par segment totalise **661 114,94 $**, et la jointure naïve totalise **885 282,55 $**.
  - J'ai exécuté `sql/checks/s08-weighted-reconciliation.sql` : `BRIDGE_WEIGHT` retourne 0 anomalie, et le total pondéré réconcilie avec le total réel avec un écart de **0,00 $**.
  - J'ai vérifié que les chiffres du brief viennent des tables DuckDB chargées, pas d'une lecture directe des CSV bruts.
- **Justification :** Accélérer la structuration des requêtes et des textes exécutifs tout en gardant la responsabilité sur les choix de modélisation, l'interprétation business et la validation des chiffres du seed local.

### 2026-06-14 — Séance S09
- **Modèle :** Cursor / agent GPT-5.5
- **Prompt :** « Aide-moi à livrer la séance S09 : quels processus NexaMart sont transactionnels, lesquels sont des snapshots, et lesquels sont de simples présences ? Je dois construire les tables de faits S09 manquantes, compléter les requêtes SQL des quatre types de faits, rédiger l'arbre de décision et produire le brief exécutif avec des chiffres réels sur mes données. Utilise les tables DuckDB modélisées, pas les CSV bruts, et prépare les changements en plusieurs sprints sans committer avant ma relecture. »
- **Résultat :** L'agent a aidé à matérialiser les 4 tables de faits S09 (`fact_orders_transaction`, `fact_daily_inventory`, `fact_order_pipeline`, `fact_promo_exposure`), à compléter les 4 fichiers d'analyse `sql/fact-types/s09-*.sql`, à rédiger l'arbre de décision et le brief exécutif S09.
- **Validation :**
  - J'ai roulé `.\run.ps1 generate`, `.\run.ps1 load` et `.\run.ps1 check` sur le seed `team_3577855103`; le résultat final est **31 PASS, 0 FAIL, 0 SKIP**.
  - Les requêtes S09 ont été exécutées avec `.\run.ps1 sql` : `fact_orders_transaction` contient **1 662 transactions** et **531 486,99 $** de revenu brut.
  - Le piège semi-additif a été vérifié sur `fact_daily_inventory` : pour `Pet Supplies`, `SUM / AVG = 30,0`, soit les 30 jours de snapshots.
  - Le pipeline contient **429 commandes**, dont **301 livrées** (**70,2 %**) avec un délai moyen de **10,3 jours**; les commandes non livrées ont été conservées dans le funnel.
  - La factless `fact_promo_exposure` contient **132 expositions**; **170 clients actifs sur 285** n'ont pas été exposés (**59,6 %**).
- **Justification :** Accélérer la production des livrables S09 tout en respectant la stratégie de sprints incrémentaux et en validant les chiffres directement dans DuckDB avant de les intégrer au brief.

### 2026-06-16 — Séance S10
- **Modèle :** Cursor / agent GPT-5.5
- **Prompt :** « Aide-moi à compléter la revue de pairs Jalon 3 (`peer-review-3.md`) sur le pack documentation de Charles : model card, bus matrix, dictionnaire, decision log. Identifie ensuite les améliorations à appliquer à mon propre handoff pack avant S11. Ne pas copier le contenu du pair — je dois noter ce qui manque et ce que je refuse d'accepter sans preuve. »
- **Résultat :** L'agent a aidé à rédiger la grille dans `docs/peer-reviews/peer-review-3.md` (qualité modèle, validation, justification exécutive, trace, reproductibilité) et à lister les actions S11 : table d'additivité mesure par mesure, politique NULL, symboles `~` dans la bus matrix, pont/outrigger, et création de `docs/metric-definitions.md`.
- **Validation :**
  - J'ai relu les documents Charles dans `docs/board-briefs/Charles_*.md` avant de noter chaque critère — revue sur copie exportée, pas de clone live.
  - J'ai refusé « Excellent » en validation quality tant que `metric-definitions.md` n'était pas fourni chez Charles — noté « Satisfaisant » avec justification explicite.
  - J'ai intégré le retour reçu de Charles (`Charles_peer-review-3.md`) : priorité S11 = KPIs testés sur DuckDB.
  - J'ai committé `docs/peer-reviews/peer-review-3.md` pour tracer le processus (exigence S10).
- **Justification :** Structurer la revue par les pairs et traduire les findings en actions concrètes pour mon pack, sans copier le contenu du pair ni sur-noter sans preuve.

### 2026-06-18 — Séance S11
- **Modèle :** Cursor / agent GPT-5.5
- **Prompt :** « Implémente le plan S11 : polish du handoff pack après S10 (`model-card.md`, `bus-matrix.md`, `data-dictionary.md`, `decision-log.md`), rédige `docs/metric-definitions.md` (≥ 4 KPIs testés sur DuckDB), complète `answers/S11_executive_brief.md` pour la question CEO du passage de relais, mets à jour `ai-usage.md`, lance `.\run.ps1 check`. Ne pas push sans ma relecture. »
- **Résultat :** L'agent a ajouté la section politique NULL et l'additivité mesure par mesure à la model card, complété la bus matrix S11 (pont/outrigger), formalisé quatre KPIs dans `metric-definitions.md`, rédigé D08 dans le decision log, et produit le brief exécutif S11 avec preuve SQL et test de relais (5 questions).
- **Validation :**
  - J'ai exécuté les requêtes KPI sur `db/nexamart.duckdb` (seed `team_3577855103`) : revenu jan 2025 = **62 630,86 $** ; déc 2025 = **54 228,47 $** ; livraison pipeline = **70,2 %** ; couverture promo = **46,3 %** ; pic retour **Automotive / 2025-03 = 21,42 %**.
  - `.\run.ps1 check` : **31 PASS, 0 FAIL, 0 SKIP**.
  - J'ai vérifié que chaque formule KPI n'utilise que des tables/colonnes présentes dans mon DuckDB — rejeté toute suggestion avec tables absentes.
  - J'ai relu le brief S11 : les 5 réponses du test de relais correspondent aux docs finaux et à `validation/checks.sql`.
- **Justification :** Accélérer la formalisation du handoff pack final tout en validant chaque chiffre sur le seed local ; les choix de KPI, l'interprétation business et la décision de ne pas push immédiatement restent ma responsabilité.

### 2026-06-18 — Séance S11 (relecture croisée)
- **Modèle :** Cursor / agent GPT-5.5
- **Prompt :** « Relecture finale S11 vs slides du professeur : compare les livrables au checklist de remise, signale les écarts, puis applique les ajustements — ajouter `metric-definitions.md` au brief, clarifier revenu vs retours, ajouter un KPI écart réel vs budget (`fact_budget`), harmoniser la model card, propriétaires par fait. Ne pas committer sans mon approbation. »
- **Résultat :** L'agent a produit une grille conformité/exigences, puis a mis à jour `answers/S11_executive_brief.md` (livrabile metric-definitions, propriétaires par table de faits, preuve SQL alignée), `docs/metric-definitions.md` (5e KPI budget, clarification revenu avant retours), `docs/model-card.md` (intro handoff S11) et `docs/decision-log.md` (D08 → cinq KPIs).
- **Validation :**
  - J'ai exécuté la requête écart réel vs budget sur DuckDB : plus grand écart absolu = **Sports & Outdoors / 2025-05 : -99,3 %** (741,33 $ réel vs 101 657,54 $ cible) — cohérent avec S07.
  - J'ai confirmé que le KPI revenu mensuel exclut bien les retours et renvoie au KPI « taux de retour » pour les remboursements.
  - J'ai relu le brief : lecture CEO ~5 min, pas de TODO restants, preuve SQL exécutable sans modification.
- **Justification :** Fermer les écarts signalés à la relecture (checklist slides 17–18) avant push ; j'ai conservé le contrôle sur le commit et le push.

<!-- Ajoutez vos entrées ci-dessous -->
