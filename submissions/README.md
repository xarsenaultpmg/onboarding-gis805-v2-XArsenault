# Comment soumettre votre travail

Pas de branches. Pas de pull request. Deux options au choix.

---

## Option A — Bouton dans GitHub (recommandée)

1. Allez dans l'onglet **Actions** de votre dépôt GitHub.
2. Dans la liste à gauche, cliquez sur **Submit Gate**.
3. Cliquez sur **Run workflow** (bouton gris en haut à droite).
4. Choisissez votre fenêtre dans le menu déroulant : `a1`, `a2` ou `final`.
5. Cliquez sur le bouton vert **Run workflow**.

La vérification démarre. Gardez le lien de la run comme preuve de remise.

---

## Option B — Fichier de déclenchement (si vous êtes à l'aise avec Git)

1. Ouvrez le fichier correspondant à votre jalon :
   - Remise 1 → `submissions/a1/SUBMIT.md`
   - Remise 2 → `submissions/a2/SUBMIT.md`
   - Remise finale → `submissions/final/SUBMIT.md`
2. Écrivez le nom de votre équipe à la ligne prévue.
3. Committez et poussez sur `main`.

Le workflow *Submit Gate* se déclenche automatiquement.

---

## C'est quoi une « remise officielle » ?

La vérification lit l'état de `main` au moment où elle s'exécute.
Si elle passe (**✅**), ce commit-là constitue votre remise.
Si elle échoue (**❌**), corrigez ce qui est indiqué et soumettez à nouveau
avant la date limite — vous pouvez soumettre plusieurs fois.

Les résultats détaillés apparaissent dans l'onglet **Actions → Submit Gate → Run**,
sous l'onglet **Summary** ou dans l'artefact `session-report-*`.

---

## Divulgation IA (`ai-usage.md`)

Ce fichier à la racine du dépôt est **obligatoire** pour les trois remises.
Une remise dont `ai-usage.md` est absent ou vide sera marquée incomplète.

À partir du printemps 2026, les jalons sont remis via une **pull request
de `main` vers une branche `submit/aX` protégée**. Les anciens dossiers
`a1/`, `a2/`, `final/` (qui historiquement contenaient des copies)
restent acceptés en complément (snapshot zip facultatif), mais ce qui
est *évalué* est l'état de `main` au moment où le PR est ouvert.

## Trois jalons

| Branche cible      | Jalon                              | Sessions couvertes | Échéance indicative |
|--------------------|-------------------------------------|--------------------|---------------------|
| `submit/a1`        | Revue de pairs 1                    | S01–S04            | voir `docs/calendar.md` |
| `submit/a2`        | Revue de pairs 2                    | S06–S09            | voir `docs/calendar.md` |
| `submit/final`     | Remise finale (défense de pack)     | S11–S13            | voir `docs/calendar.md` |

## Étapes (toutes les remises)

1. Sur `main`, vérifiez que vos artéfacts de la fenêtre de remise sont à jour
   (briefs, SQL, `ai-usage.md`).
2. Vérifiez localement :
   ```bash
   python src/run_session_checks.py --mode submit --window a1
   ```
   (remplacez `a1` selon le jalon visé).
3. Ouvrez un **pull request** :
   - Source : `main`
   - Cible  : `submit/a1` (ou `a2` / `final`)
   - Titre  : `[REMISE a1] <équipe>`
4. Le job **`structural-submit-gate`** doit être vert avant le merge. Il bloque
   tant qu'un artéfact requis manque ou qu'un fichier SQL committé est
   syntactiquement cassé. Les vérifications d'entrepôt et les sections de
   brief manquantes restent indicatives.
5. Si activée (variable `RUBRIC_ENABLED == 'true'`), la **Rubric advisory**
   poste un commentaire collant avec une notation indicative par dimension.
   **Cette note ne bloque jamais le merge.**
6. L'instructeur revoit, demande des révisions au besoin, puis merge. Le SHA
   mergé fait foi pour la note finale.

## Échéances : indicatives, pas bloquantes

Les dates limites de chaque session apparaissent dans
`validation/session_manifest.yaml` et `docs/calendar.md`. La CI émet un
**avertissement** quand une échéance est dépassée mais ne bloque pas le push.
La pénalité éventuelle est appliquée par l'instructeur, pas par le pipeline.

## Divulgation IA (obligatoire)

Le fichier `ai-usage.md` à la racine du repo est une **condition de remise**
pour les trois jalons. Décrivez :

- les outils utilisés (modèles, IDE-assistants, etc.),
- pour quelles tâches (génération, révision, debug, brainstorming),
- ce qui a été conservé tel quel vs reformulé,
- ce que vous *n'avez pas* utilisé d'IA pour (par ex. la justification
  business, la décision de grain).

Le **Rubric advisory** envoie le brief à un fournisseur LLM externe
(Anthropic ou OpenAI) **après redaction** des identifiants Git, courriels et
numéros d'identification. Le journal de redaction est conservé dans
`validation/results/grader_redactions.txt`. Voir
`tools/grader/grade_brief.py` pour les détails techniques.

> **Désactivation rapide** : un instructeur peut couper la notation
> automatique en mettant la variable Actions `RUBRIC_ENABLED` à `false`.

---

## Legacy : dossiers `a1/` `a2/` `final/`

Toujours acceptés comme snapshot d'appoint (zip ou copie) mais non requis.
Ils contiennent un `.gitkeep` pour rester suivis par Git.
