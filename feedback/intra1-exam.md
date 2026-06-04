# Rétroaction — Examen intra 1 · GIS805-06

Bonjour Xavier,

Voici ta rétroaction pour l'examen intra 1 du 1er juin 2026.

---

## Résultat global

| Composante | Score | Maximum |
|---|---|---|
| QCM (22 questions) | 22 | 22 |
| Questions ouvertes (3 questions) | 2.5 | 3 |
| **Total** | **24.5** | **25** |

**24.5 / 25 (98%) — ✓ Suffisant**

---

## Performance par section — QCM

| Section | Score | /max |
|---|---|---|
| Structure dimensionnelle | 4 | 4 |
| Slowly Changing Dimensions | 4 | 4 |
| Jointures et clés | 5 | 5 |
| Junk et dimensions dégénérées | 4 | 4 |
| Lecture SQL | 5 | 5 |

---

## Questions ouvertes

### Q05 — Grain irréversible — 1.0 / 1

Tu expliques clairement l'irréversibilité du choix de grain en soulignant que les détails sont perdus et qu'il est impossible d'affiner les requêtes. De plus, les deux exemples concrets fournis illustrent bien les analyses qui ne peuvent plus être réalisées avec ce grain. La réponse est complète et pertinente.

### Q10 — SCD Gold → Platinum — 0.5 / 1

Tu as correctement identifié un SCD de type 2 et a justifié son choix en mentionnant l'importance de l'historique. Cependant, il n'a mentionné que deux colonnes (valid_from et valid_to) au lieu des quatre requises pour obtenir le point complet. Les colonnes is_current et une clé de substitution spécifique à la version manquent.

### Q23 — Logique SQL Loyalty+Promo par trimestre — 1.0 / 1

La réponse décrit correctement les tables et les jointures, en mentionnant fact_sales, dim_order_profile et dim_date. Le filtre est bien spécifié avec les conditions is_loyalty et is_promo. L'agrégation est également bien expliquée, avec le calcul du ratio par trimestre fiscal.

---

_Rétroaction générée le 2026-06-04 · GIS805-06 · Université de Sherbrooke_