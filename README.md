# GIS805 — Bienvenue dans votre entrepôt de données

Vous venez d'accepter votre premier assignment. Ce dépôt est **votre espace de travail** pour tout le trimestre.

> **Lien d'acceptation du devoir :** [https://classroom.github.com/a/Tndi64Pu](https://classroom.github.com/a/Tndi64Pu)

> **Le scénario :** Vous êtes le Head of Data de NexaMart, une chaîne de
> commerce de détail. Chaque semaine, le CEO pose une question stratégique
> — et les systèmes opérationnels ne peuvent pas y répondre. Votre job :
> construire l'entrepôt de données qui rend ces réponses possibles.

Pas besoin d'être programmeur. Vous travaillez en **langage naturel d'abord** :
un assistant IA est votre coéquipier, vous lui posez des questions en français,
et vous développez votre jugement sur les réponses.

---

## Démarrage — choisissez votre chemin

### Chemin A : Codespace (recommandé — zéro installation)

Tout se passe dans votre navigateur. Rien à installer.

1. Sur la page de votre dépôt, cliquez **Code** (bouton vert) puis **Codespaces** puis **Create codespace on main**
2. Attendez environ 2 minutes — un éditeur VS Code s'ouvre avec tout déjà configuré
3. C'est tout. Passez à la section suivante

> Votre GitHub Student Developer Pack vous donne 60 heures/mois gratuites.
> Pensez à arrêter votre Codespace quand vous ne travaillez pas
> (menu `...` en haut à gauche puis **Stop Codespace**).

### Chemin B : VS Code sur votre ordinateur

Si vous préférez travailler en local, ou si vos heures Codespace sont épuisées.

1. Installez [VS Code](https://code.visualstudio.com/), [Python 3.10+](https://www.python.org/downloads/) et [Git](https://git-scm.com/downloads)
2. Dans VS Code, installez les extensions **GitHub Copilot** et **GitHub Copilot Chat** (gratuit via Student Developer Pack)
3. Clonez votre dépôt : palette de commandes (`Ctrl+Shift+P`) puis **Git: Clone**
4. Ouvrez un terminal dans VS Code et tapez :
   ```bash
   pip install -r requirements.txt
   ```

> Le guide complet avec toutes les étapes est dans [`docs/S00-SETUP.md`](docs/S00-SETUP.md).

### Votre premier réflexe

Quel que soit le chemin choisi, ouvrez **Copilot Chat** (icône de bulle dans
la barre latérale) et posez votre première question :

> **Qu'est-ce qui se trouve dans mon dépôt ? Explique-moi la structure du projet.**

Vous venez de faire votre première interaction de travail assistée par IA.
C'est exactement comme ça qu'on travaille dans ce cours.

---

## Vos premières commandes

Dans le terminal, lancez ces trois commandes dans l'ordre.
Choisissez le bloc correspondant à votre plateforme — les deux sont strictement équivalents.

**Mac / Linux / Codespace :**

```bash
make generate   # Génère vos données uniques (liées à votre username)
make load       # Charge les données dans la base DuckDB
make check      # Vérifie que tout est correct
```

**Windows PowerShell :**

```powershell
.\run.ps1 generate   # Génère vos données uniques (liées à votre username)
.\run.ps1 load       # Charge les données dans la base DuckDB
.\run.ps1 check      # Vérifie que tout est correct
```

> **Windows + `make` ?** Git Bash / WSL comprennent `make`, mais sous PowerShell natif utilisez `.\run.ps1`. Les deux appellent exactement les mêmes scripts Python.

Si `check` affiche tout en vert, vous êtes prêt pour la séance 1.

> **Pas sûr de ce que font ces commandes ?** Demandez à votre assistant IA :
> *« Qu'est-ce que fait `make generate` ? »*

---

## Ce que vous construisez

Au fil des **12 séances**, vous construisez l'entrepôt analytique complet de NexaMart :

1. **`fact_sales`** (S02) — Les ventes, ligne par ligne
2. **`fact_returns`** (S06) — Les retours et remboursements
3. **`fact_budget`** (S06) — Le budget par catégorie, magasin et mois
4. **`fact_daily_inventory`** (S09) — L'inventaire quotidien
5. **`fact_order_pipeline`** (S09) — Le cycle de vie des commandes

Plus trois structures complémentaires : une dimension consolidée (`junk_order_profile`),
un pont clients-segments (`bridge_customer_segment`), et une table de faits sans mesure
(`fact_promo_exposure`). Vous les découvrirez en classe.

Chaque table est accompagnée de dimensions (clients, produits, magasins, dates, canaux)
et d'un brief exécutif que vous rédigez pour le CEO.

---

## Livrables par séance

Vous créez vous-même chaque brief dans `answers/SXX_executive_brief.md`.
Pas de gabarit prérempli — voir [`answers/README.md`](answers/README.md) pour
les sections attendues et [`docs/s02-sample-brief.md`](docs/s02-sample-brief.md)
pour un exemple annoté.

| Séance | Livrable principal |
|--------|--------------------|
| S01 | Brief exécutif — question + obstacles + diagnostic |
| S02 | Grain statement + étoile + SQL preuve (`sql/facts/fact_sales.sql`) |
| S03 | Politique SCD + comparaison avant/après |
| S04 | Dimension poubelle + degenerate + analyse panier |
| S06 | Bus matrix + drill-across + réel-vs-cible (`sql/views/*.sql`) |
| S07 | Hiérarchies + politique NULLs + role-playing dates |
| S08 | Pont pondéré + réconciliation |
| S09 | Arbre de décision types de faits + process map |
| S11 | Model card + bus matrix + dictionnaire + journal de décisions + metric definitions (`docs/`) |
Chaque entrée dans `ai-usage.md` inclut : date, prompt exact, modèle utilisé, comment vous avez validé/modifié le résultat.

---

## Besoin d'aide ?

| Ressource | Description |
|-----------|-------------|
| [`docs/calendar.md`](docs/calendar.md) | Calendrier complet des 12 séances (dates, titres, jalons) |
| [`docs/S00-SETUP.md`](docs/S00-SETUP.md) | Guide complet de configuration (3 chemins, dépannage) |
| [`docs/faq.md`](docs/faq.md) | Questions fréquentes (DuckDB, travail individuel, etc.) |
| [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) | Dépannage par symptôme (messages d'erreur) |
| [`docs/s02-sample-brief.md`](docs/s02-sample-brief.md) | Exemple annoté de brief exécutif |
| Votre assistant IA | **Premier réflexe** — posez-lui la question en français |

---

## Structure du dépôt

```text
answers/           Vos briefs exécutifs (un par séance) — VOUS les créez
submissions/       Dossiers de remise (a1, a2, final) — voir submissions/README.md
sql/
  staging/         Vos vues de nettoyage intermédiaires
  dims/            Vos dimensions (dim_*.sql)
  facts/           Vos tables de faits (fact_*.sql)
  views/           Vos vues analytiques / drill-across
  checks/          Vos checks SQL personnels
  templates/       5 patterns SQL annotés — à étudier, pas à copier aveuglément
  sandbox/         Vos explorations libres
scripts/datagen/   Générateurs de données (ne pas modifier)
src/               run_pipeline.py + run_checks.py (ne pas modifier)
data/              Données générées — unique à vous (gitignore)
db/                nexamart.duckdb — votre entrepôt (gitignore)
docs/              Guides (S00-SETUP, FAQ, exemple annoté, formulaires peer-review)
meta/              Empreinte + fingerprint de votre jeu de données
validation/        checks.sql canonique exécuté par make check
.devcontainer/     Config Codespace (Python 3.12 + DuckDB + extensions)
.github/           CI GitHub Classroom (génère + load + check à chaque push)
ai-usage.md        Trace obligatoire de toutes vos interactions IA
```

> Envie d'en savoir plus ? Demandez à votre assistant :
> *« Explique-moi à quoi sert chaque dossier dans ce projet. »*

---

## Références

- Kimball & Ross — [*The Data Warehouse Toolkit* (3rd ed.)](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/data-warehouse-dw-toolkit/)
- Kimball Group — [Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- dbt Labs — [Analytics Engineering Guide](https://www.getdbt.com/analytics-engineering/start-here)
- [DuckDB Documentation](https://duckdb.org/docs/)
