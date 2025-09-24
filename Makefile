build:
	poetry install

setup:
	poetry run alembic -c src/sdb_user_profile_svc/alembic/alembic.ini upgrade head

alembic:
	poetry run alembic -c src/sdb_user_profile_svc/alembic/alembic.ini $(ARGS)

unittest:
	poetry run pytest tests

run:
	poetry run sdb_user_profile_svc