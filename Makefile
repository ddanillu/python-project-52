install:
	uv sync

collectstatic:
	uv run manage.py collectstatic

migrate:
	uv run manage.py migrate

lint:
	uv run ruff check

build:
	./build.sh

render-start:
	gunicorn task_manager.wsgi