.PHONY: setup start import clean all

all: setup start import

setup:
	uv venv
	.venv\Scripts\activate
	uv pip install -e .

start:
	docker compose up -d

import:
	python src/konsultskills_graphdb/import_profiles.py

clean:
	docker compose down 