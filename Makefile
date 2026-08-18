setup:
	python3 -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt

migrate:
	.venv/bin/python manage.py makemigrations
	.venv/bin/python manage.py migrate

sync:
	.venv/bin/python manage.py sync_players
	.venv/bin/python manage.py sync_current
	.venv/bin/python manage.py sync_transactions
	.venv/bin/python manage.py sync_news
