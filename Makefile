.PHONY: up backend venv install test

up:
	# Start services via docker compose
	docker compose up -d --build

backend:
	cd backend && source venv/bin/activate && uvicorn backend.app:app --reload

venv:
	python3 -m venv backend/venv
	./backend/scripts/setup_venv.sh

install:
	cd backend && source venv/bin/activate && pip install -r requirements.txt

test:
	cd backend && source venv/bin/activate && pytest -q
