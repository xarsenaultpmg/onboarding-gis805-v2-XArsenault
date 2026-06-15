# S10 — Guide de préparation : sprint documentation et rétroaction

> **Contexte :** S10 (15 juin) est une séance de **pratique non notée**.
> Vous construisez votre handoff pack et en testez la lisibilité avec un pair.
> La remise **notée** (10 %) est en **S11** (18 juin) : handoff pack complet + metric definitions.

---

## Ce que vous produisez ce soir (S10)

| Document | Chemin | Critère d'acceptation |
|----------|--------|----------------------|
| Model card | `docs/model-card.md` | Un analyste junior comprend le modèle sans vous appeler |
| Bus matrix | `docs/bus-matrix.md` | À jour après S09 — toutes les tables de faits listées |
| Dictionnaire de données | `docs/data-dictionary.md` | Chaque `dim_*` et `fact_*` avec définition business |
| Journal de décisions | `docs/decision-log.md` | Au moins 5 décisions avec justification business |

> Ces drafts **ne sont pas soumis ce soir**. Vous les finalisez en S11.

---

## La revue par les pairs (S10)

Échangez votre draft de model card avec un pair. Chacun évalue l'autre en 15 minutes :

1. **Grain** — est-il explicitement énoncé pour chaque table de faits ?
2. **SCD** — la politique est-elle documentée et justifiée ?
3. **NULLs** — les membres inconnus sont-ils nommés et justifiés ?
4. **Bus matrix** — est-elle à jour avec toutes les tables de faits produites depuis S02 ?
5. **Décision log** — les décisions expliquent-elles *pourquoi*, pas seulement *quoi* ?

Chaque étudiant repart avec **1 point fort + 1 point à améliorer** avant S11.

> **À faire avant de quitter S10 :** remplissez `docs/peer-reviews/peer-review-3.md`
> dans VOTRE repo avec les findings de la revue, puis committez et poussez.
> Ce fichier fait partie du `process_trace` noté en S11.

---

## Checklist avant la remise S11 (18 juin)

### Documents handoff
- [ ] `docs/model-card.md` : grain, faits, dimensions, SCD, NULLs, ponts, risques (≥ 500 octets)
- [ ] `docs/bus-matrix.md` : colonnes = tables de faits, lignes = dimensions (≥ 200 octets)
- [ ] `docs/data-dictionary.md` : chaque colonne avec définition business (≥ 200 octets)
- [ ] `docs/decision-log.md` : au moins 5 décisions justifiées (≥ 200 octets)
- [ ] `docs/metric-definitions.md` : au moins 4 KPIs (nom, formule SQL, grain, source, fréquence) (≥ 300 octets)

### Brief et trace
- [ ] `answers/S11_executive_brief.md` : sections obligatoires remplies (≥ 400 octets)
- [ ] `ai-usage.md` : toutes les interactions IA tracées

### Technique
- [ ] `make check` passe sans FAIL depuis un clone frais
- [ ] `db/nexamart.duckdb` est à jour (`make load` récent)
- [ ] Tout est commité et poussé sur `main`

---

## Format du metric definitions pack (`docs/metric-definitions.md`)

Pour chaque KPI de votre modèle :

```markdown
| Nom | Formule SQL (avec grain) | Source | Fréquence |
|-----|--------------------------|--------|-----------|
| Revenue total | `SUM(fact_sales.revenue) GROUP BY dim_date.month` | fact_sales | Quotidien |
| Taux de retour | `COUNT(fact_returns) / COUNT(fact_sales)` | fact_returns, fact_sales | Hebdomadaire |
```

**Minimum 4 KPIs couvrant au moins 2 tables de faits différentes.**
Testez chaque formule sur votre DuckDB avant de soumettre.

---

## Questions difficiles à anticiper pour l'examen final (S12)

L'examen final teste la maîtrise complète — les sujets ci-dessous reviennent souvent :

1. **« Pourquoi ce grain et pas un plus fin/grossier ? »** — Nommez une question impossible avec un grain différent.
2. **« Comment savez-vous que vos chiffres sont justes ? »** — Montrez votre logique de réconciliation.
3. **« Que se passe-t-il quand un client change de région ? »** — Expliquez votre politique SCD et son impact.
4. **« Définissez "revenue" sans ambiguïté. »** — C'est exactement ce que votre metric definitions pack doit répondre.
5. **« Deux tables de faits partagent-elles une dimension conforme ? »** — Votre bus matrix répond à ça.


---

## Structure recommandee (7 min)

| Temps     | Section                    | Ce que vous dites                                    |
|-----------|----------------------------|------------------------------------------------------|
| 0:00-1:00 | **Question du CEO**        | Quelle question strategique votre modele resout-il ? |
| 1:00-2:30 | **Le modele**              | Grain, faits, dimensions cles. Montrez le schema.    |
| 2:30-4:00 | **La preuve**              | Requete SQL + resultat qui repond a la question.     |
| 4:00-5:00 | **Les decisions**          | SCD, NULLs, ponts — pourquoi ces choix ?             |
| 5:00-6:00 | **Les limites**            | Ce que votre modele ne couvre pas (encore).           |
| 6:00-7:00 | **La recommandation**      | Quelle decision business le CEO peut prendre ?       |

---

## Checklist avant la presentation

### Contenu
- [ ] Mon grain statement est clair : « une ligne = … »
- [ ] J'ai un schema visuel (Mermaid ou bus matrix) a montrer
- [ ] J'ai une requete SQL qui repond a la question du CEO
- [ ] Les resultats de la requete sont coherents (totaux reconcilies)
- [ ] Mes decisions SCD, NULL, et pont sont justifiees par un besoin business

### Technique
- [ ] `make check` passe sans FAIL
- [ ] Ma base DuckDB est a jour (`make load` recent)
- [ ] Mon depot est commitee et pousse sur GitHub
- [ ] `docs/verify-before-pushing.md` est complete

### Presentation
- [ ] Je peux expliquer chaque ligne de ma requete SQL principale
- [ ] Je connais les limites de mon modele (ce qu'il ne couvre pas)
- [ ] J'ai prepare des reponses aux questions difficiles (voir ci-dessous)

---

## Questions difficiles a anticiper

Le board va poser des questions. Preparez vos reponses :

1. **« Pourquoi ce grain et pas un plus fin/grossier ? »**
   - Nommez une question qui serait impossible avec un grain plus grossier
   - Nommez un cout concret d'un grain plus fin

2. **« Comment savez-vous que vos chiffres sont justes ? »**
   - Montrez votre requete de reconciliation
   - `make check` + verification manuelle sur un sous-ensemble

3. **« Que se passe-t-il quand un client change de region ? »**
   - Expliquez votre politique SCD (Type 1/2/3) et pourquoi
   - Montrez l'impact sur un rapport avant/apres

4. **« Pourquoi certaines dimensions ont des "Inconnu" ? »**
   - Expliquez votre politique NULL et le membre inconnu (key=-1)
   - Montrez que les totaux incluent ces lignes

5. **« Le modele peut-il repondre a une nouvelle question ? »**
   - Ecrivez la requete en direct (ou demandez a votre assistant)
   - Montrez que le schema en etoile rend la nouvelle question simple

6. **« Quel est le plus gros risque de votre modele ? »**
   - Soyez honnete : donnees manquantes, grain trop grossier, SCD pas teste
   - Proposez un plan concret pour le resoudre

---

## Prompts pour votre assistant IA

Utilisez ces prompts pour preparer votre defense :

- « Structure ma presentation de 7 min : question, modele, preuve, decisions, limites, recommandation. »
- « Genere 5 questions difficiles que le CFO pourrait poser sur mon modele. »
- « Simule un contre-interrogatoire sur mes choix de grain et de SCD. »
- « Voici mes resultats SQL. Le total est-il coherent avec [X] ? Explique tout ecart. »

> **Regle d'or :** si votre assistant genere une reponse que vous ne
> comprenez pas, **ne l'utilisez pas**. Le board detectera immediatement
> que ce n'est pas votre raisonnement.

---

## Apres la defense

Documentez les questions recues et vos reponses dans :
- `docs/board-q-and-a-log.md`
- `docs/metric-definitions.md` (si des definitions ont ete clarifiees)

Commitez : `git add -A && git commit -m "S12 board defense" && git push`
