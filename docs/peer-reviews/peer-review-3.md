# Revue de pairs -- Jalon 3 (a S11, pack documentation)

> **Portee :** pack complet de documentation : model card, bus matrix,
> dictionnaire de donnees, journal de decisions, definitions de metriques.
> **Appariement :** aleatoire (different des Jalons 1 et 2).
> **Objectif :** le "test du lundi matin" -- un nouvel analyste doit comprendre
> l'entrepot en lisant `docs/` sans parler a l'auteur.

## Informations

- **Reviseur :** xarsenaultpmg
- **Revise :** Charles Narbonne Merineau
- **Date :** 2026-06-16
- **Repo revise :** documents partages dans `docs/board-briefs/Charles_*.md` (revue sur copie exportee, pas de clone live)

## Grille d'evaluation

### 1. Qualite du modele -- *model_quality* (40 %)
Model card complete : grain pour CHAQUE table de faits, mesures avec statut
d'additivite, SCD type par dimension, politique NULL, ponts documentes.
Bus matrix montre la conformite de toutes les dimensions avec tous les faits.

- [ ] Excellent
- [x] Satisfaisant
- [ ] A retravailler
- [ ] Absent

Justification :

La model card couvre les 8 tables de faits avec grain, type Kimball et dimensions reliees. Les politiques SCD sont explicites (`dim_customer` Type 2, `dim_customer_scd3` Type 3, dimensions Type 1) et le pont `bridge_customer_segment` est bien documente avec normalisation des poids. Les limites semi-additives (inventaire) et factless (promo) sont nommees.

Points a renforcer avant S11 :
- le statut d'additivite n'est pas systematique mesure par mesure dans la model card ;
- la politique NULL / membre inconnu (`key = -1`) n'est pas formalisee comme section dediee — seuls les NULL du pipeline sont expliques ;
- la bus matrix liste bien tous les faits S02-S09, mais n'inclut pas le pont ni `dim_segment_outrigger`, et la conformite partielle budget x produit (`category` sans `product_key`) meriterait un symbole `~` plutot qu'un simple `X` sur Category.

### 2. Qualite de validation -- *validation_quality* (25 %)
Dictionnaire de donnees : chaque colonne a une *definition d'affaires* (pas
juste un type SQL). Definitions de metriques incluent la formule, la source,
le grain, la frequence de rafraichissement.

- [ ] Excellent
- [x] Satisfaisant
- [ ] A retravailler
- [ ] Absent

Justification :

Le dictionnaire est solide sur les fichiers sources CSV : chaque colonne raw a une description business claire. La section « Business warehouse tables » resume bien grain et usage des `dim_*`, `fact_*` et du pont.

Cependant, le pack Jalon 3 exige aussi `docs/metric-definitions.md` (formule SQL, source, grain, frequence) — ce document n'etait pas dans la copie partagee. De plus, les colonnes analytiques DuckDB (`customer_key`, `store_key`, mesures des faits) ne sont pas toutes decrites colonne par colonne au niveau entrepot ; l'analyste doit inferer depuis les CSV sources.

### 3. Justification executive -- *executive_justification* (20 %)
Journal de decisions : chaque entree motivee en *langage d'affaires*, pas
technique. Le CFO doit pouvoir lire le journal et comprendre les arbitrages.

- [x] Excellent
- [ ] Satisfaisant
- [ ] A retravailler
- [ ] Absent

Justification :

Le decision log est le point le plus fort du pack. Six decisions (D01-D06) suivent toutes la structure contexte / decision / alternatives / consequences / revisable si. Chaque entree repond a une question CEO (grain S02, SCD S03, drill-across S06, pont S08, types de faits S09) en langage d'affaires, avec references SQL verifiables. Un lecteur non technique comprend pourquoi le drill-across evite le produit cartesien et pourquoi le pont pondere reconcilie avec `fact_sales`.

### 4. Trace de processus -- *process_trace* (10 %)
Pack de documentation construit progressivement, pas ecrit en bloc la veille.
`ai-usage.md` trace complete (y compris "l'IA m'a propose X, j'ai refuse parce que Y").

- [ ] Excellent
- [x] Satisfaisant
- [ ] A retravailler
- [ ] Absent

Justification :

La model card inclut un historique de versions S01-S10 qui suggere une construction incrementale. Les decisions referencent des briefs et SQL par seance, ce qui rend la trace lisible.

Limite de cette revue : je n'ai pas acces au repo Git ni a `ai-usage.md` de Charles — impossible de verifier les commits ou les refus explicites d'outputs IA. A confirmer avant S11.

### 5. Reproductibilite -- *reproducibility* (5 %)
Test : clonez le repo du pair, lancez `make generate && make load && make check`.
Tout passe ? Le pack doc pointe-t-il vers les vrais fichiers SQL/dim/fact ?

- [ ] PASS
- [x] FAIL

Justification :

Non teste dans cette session : seuls les quatre documents exportes ont ete revus, sans clone ni execution de pipeline. Sur le papier, les references SQL (`sql/views/v_s06_drill_across_region_month.sql`, checks dans `validation/checks.sql`) sont coherentes et la section reproductibilite de la model card decrit bien `make generate && make load && make check`. A valider par un clone frais avant la defense S12.

## Test du lundi matin

> Un nouvel analyste embauche lundi matin ouvre ce repo. Peut-il :
> (1) nommer les 5 tables de faits et leur grain, (2) comprendre pourquoi
> chaque dimension a son SCD choisi, (3) lancer une requete drill-across
> correcte -- en moins de 30 minutes, sans vous parler ?

- [ ] Oui
- [x] Oui avec quelques clarifications en commentaires
- [ ] Non -- des pans entiers sont opaques

Justification :

(1) Oui — la model card section 3.1 nomme 8 faits avec grain explicite (plus que les 5 minimum). (2) Oui — tableau SCD section 3.2 + decisions D03 et D05. (3) Partiellement — la bus matrix pointe vers `v_s06_drill_across_region_month.sql` et rappelle la regle « agreguer avant de joindre », mais il manque un exemple commente pour les faits S09 et le fichier metric definitions pour definir un KPI sans ambiguite.

## Point fort

Le journal de decisions : chaque choix de modelisation est relie a une question business, avec alternatives ecartees et consequences explicites. C'est exactement ce qu'un board ou un CFO attend du handoff pack.

## Amelioration la plus actionnable avant la defense au board (S12)

Ajouter `docs/metric-definitions.md` avec au moins 4 KPIs (ex. revenu net, taux de retour, ecart reel-vs-budget, jours de couverture stock) incluant formule SQL, grain, source et frequence — puis completer la bus matrix avec `~` pour la conformite partielle budget x produit et une colonne pont/segment outrigger.

---

## Apres la revue — ce que vous devez faire avant S11

1. **Committez ce fichier rempli dans VOTRE repo** (pas celui du pair) :
   ```bash
   git add docs/peer-reviews/peer-review-3.md
   git commit -m "docs: revue de pair S10 (Jalon 3) — findings integres"
   git push origin main
   ```

2. **Integrez les findings dans votre handoff pack avant S11 (18 juin).**
   Le `process_trace` de S11 verifie que ce fichier est commite dans votre repo.
   Un fichier vide ou non commite = findings non traces.

3. **Ajoutez une note dans `ai-usage.md`** si vous avez utilise l'IA pendant la revue
   (ex. : « j'ai demande a Copilot de relire mon grain statement »).
