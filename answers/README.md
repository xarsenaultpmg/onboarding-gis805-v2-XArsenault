# Briefs exécutifs — où écrire vos réponses hebdomadaires

Chaque semaine (sauf les séances d'examen), vous **créez vous-même** le brief
qui répond à la question du CEO. Il n'y a **pas** de gabarit pré-rempli —
commencer par une page blanche est volontaire : un livrable exécutif
s'adapte à la question, pas l'inverse.

## Nommage

```
answers/S01_executive_brief.md
answers/S02_executive_brief.md
...
answers/S11_executive_brief.md
```

Les séances **S06** et **S12** sont des examens — pas de brief.
La séance **S10** est une séance de pratique non notée — pas de brief obligatoire.

## Sections attendues (repère, pas obligation)

- **Question du CEO** — reprise textuelle de la question de la semaine
- **Réponse exécutive** — 3 à 5 lignes, en français d'affaires, sans jargon
- **Décisions de modélisation** — grain, mesures, dimensions, SCD, hypothèses
- **Preuve** — requête SQL (ou extrait) + résultat tabulaire
- **Validation** — comment vous avez vérifié (checks, réconciliation)
- **Risques / limites** — ce que votre modèle ne couvre *pas*
- **Prochaine recommandation** — la décision ou l'action qui suit

## Exemple annoté

Un brief modèle (S02, question catégories/régions) est commenté dans
[`../docs/s02-sample-brief.md`](../docs/s02-sample-brief.md). Lisez les
annotations `[-> ...]` : chacune explique *pourquoi* la section fonctionne.

## Test du « lundi matin »

Un cadre qui ouvre votre brief sans vous avoir parlé doit pouvoir :
(1) nommer la question posée, (2) comprendre la réponse, (3) savoir quelle
décision prendre ensuite — en moins de 2 minutes.
