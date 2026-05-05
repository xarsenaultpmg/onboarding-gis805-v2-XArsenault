.PHONY: help generate load check clean reset

TEAM_SEED ?= $(shell python scripts/datagen/_compute_seed.py)

# ──────────────────────────────────────────────
# help : Afficher les cibles disponibles
#        Cible par défaut (lancée par `make` sans argument).
# ──────────────────────────────────────────────
.DEFAULT_GOAL := help
help:
	@echo "NexaMart -- cibles disponibles :"
	@echo ""
	@echo "  make generate  Generer vos CSVs (deterministe via team seed)"
	@echo "  make load      Charger CSVs + executer sql/staging,dims,facts,bridges/"
	@echo "  make check     Lancer validation/checks.sql -> PASS / FAIL / SKIP"
	@echo "  make reset     Supprimer uniquement le .duckdb (garde les CSVs)"
	@echo "  make clean     Tout supprimer (DB + CSVs + resultats)"
	@echo "  make help      Afficher cette aide"
	@echo ""
	@echo "Cycle hebdomadaire : generate -> (ecrire SQL) -> load -> check -> git push"
	@echo "Windows PowerShell : utiliser .\\run.ps1 <cible> au lieu de make."

# ──────────────────────────────────────────────
# generate : Produire toutes les données NexaMart
#            (dimensions + 5 faits + ponts + factless)
#            Déterministe : même seed → même données.
# ──────────────────────────────────────────────
generate:
	python scripts/datagen/gen_all.py --team-seed $(TEAM_SEED)

# ──────────────────────────────────────────────
# load : Exécuter le pipeline SQL (staging → dims → facts)
#        Produit db/nexamart.duckdb
# ──────────────────────────────────────────────
load:
	python src/run_pipeline.py

# ──────────────────────────────────────────────
# check : Valider l'intégrité du modèle
#         Clés uniques, NULLs, réconciliation, identité
# ──────────────────────────────────────────────
check:
	python src/run_checks.py

# ──────────────────────────────────────────────
# reset : Supprimer UNIQUEMENT la base DuckDB
#         Les CSVs restent — gain de ~30 s au prochain `make load`.
#         Utile après un changement de SQL sans changer de seed.
# ──────────────────────────────────────────────
reset:
	rm -f db/nexamart.duckdb db/nexamart.duckdb.wal
	rm -rf validation/results/*

# ──────────────────────────────────────────────
# clean : Réinitialiser (supprime DB + données)
#         Régénère tout depuis zéro — plus lent mais déterministe.
# ──────────────────────────────────────────────
clean:
	rm -f db/nexamart.duckdb db/nexamart.duckdb.wal
	rm -rf data/synthetic/ data/raw/*.csv data/staged/* data/exports/*
	rm -rf validation/results/*
