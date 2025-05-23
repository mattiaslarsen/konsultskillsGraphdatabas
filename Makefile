.PHONY: setup start import clean deepclean wait_neo4j all check

# Default import path, can be overridden: make import IMPORT_PATH=/din/vag
IMPORT_PATH ?= C:/Users/matti/GNR8 AB/GNR8 AB - Konsultprofiler

all: setup start wait_neo4j import

setup:
	uv venv
	.venv\Scripts\activate
	uv pip install -e .

start:
	docker compose up -d

# Vi använder en separat Python-fil för att vänta in Neo4j, eftersom komplexa one-liners ofta ger syntaxfel i Makefile.
wait_neo4j:
	python wait_neo4j.py

import:
	python src/konsultskills_graphdb/import_profiles.py --path "$(IMPORT_PATH)"

clean:
	docker compose down

# Remove venv and Python cache
# Kör: make deepclean för att städa allt

deepclean: clean
	rmdir /S /Q .venv 2>NUL || true
	del /S /Q __pycache__ 2>NUL || true

check:
	python check_import.py 